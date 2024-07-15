import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'

from machines.user_simulator import UserSimulator
from machines.retrieval_machine import RetrievalMachine
from machines.clarify_machine import ClarifyMachine
from machines.answer_machine import AnswerMachine
from models.llm import LLM
from args import get_parser
from evaluator import Evaluator, normalize_value
import json
import pandas as pd
import time
import re


def format_grounding(row, table, ignore_cols=None, exclude_value=None):
    to_ignore = ['index', 'url', 'uid', 'titleintro', 'sectionintro']
    if ignore_cols:
        to_ignore.extend(ignore_cols)

    prefect_grounding = table[row:row + 1]
    differ_keys = [x for x in prefect_grounding.columns.to_list() if
                   x not in to_ignore]
    rst_str = ''
    for cur_key in differ_keys:
        if len(cur_key.strip()) == 0: continue
        if type(prefect_grounding[cur_key]) == pd.DataFrame:
            article = re.sub(r'\n[0-9]?(spoilers)?', '', prefect_grounding[cur_key].to_string().strip())
        else:
            article = ' '.join(prefect_grounding[cur_key].tolist())
        try:
            if exclude_value:
                if normalize_value(exclude_value) != normalize_value(article):
                    rst_str += '{}: {}; '.format(cur_key, article)
            else:
                rst_str += '{}: {}; '.format(cur_key, article)
        except:
            import ipdb;ipdb.set_trace()
    return rst_str.strip()


class EvaluationPipeline:
    def __init__(self, args):
        self.args = args
        llm = LLM(apikey=args.apikey, model_name=args.model_name)
        llm_eval = LLM(apikey=args.apikey, model_name=args.model_name_eval)
        self.user_simulator = UserSimulator(llm=llm_eval)
        self.retrieval_machine = RetrievalMachine(llm=llm, args=args)
        self.clarify_machine = ClarifyMachine(llm=llm)
        self.answer_machine = AnswerMachine(llm=llm)
        self.evaluator = Evaluator(llm=llm_eval)
        self.run()

    def run(self):
        raw_data = pd.read_csv('./dataset/good_stage2_data.csv')
        question_simplified_data = pd.read_csv('./dataset/data_list_fix.csv')
        data_idx, num_valid = 0, 0
        header_use = True

        for row in question_simplified_data.iterrows():
            _, _,complex_query, complex_answer, simple_question, decomposed_queires, answers, groundings, table_id = [y for x, y in row[1].items()]
            table, NL_columns = self.retrieval_machine.fetch_doc_df(table_id)
            raw_row = raw_data[data_idx:data_idx+1]
            details = json.loads(raw_row['easy_conversation'].item())
            if 'surface_annotations' not in details[-1]:
                continue
            elif details[-1]['surface_annotations']['answer_type'] not in ['Single Cell', 'Single Row']:
                continue
            # use new grounding id to loc
            gold_groundings = [(x['surface_annotations']['selected_rows'], x['surface_annotations']['selected_columns'])
                               for x in details if 'surface_annotations' in x]
            # find candidate rows
            perfect_row_id = gold_groundings[-1][0][0] - 1
            perfect_row = format_grounding(perfect_row_id, table)
            if not complex_answer in perfect_row:
                continue

            num_valid += 1

            deanswered_gold_grounding = format_grounding(perfect_row_id, table, exclude_value=complex_answer)
            user_question = simple_question
            for noisy_gnd_num in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
                irrelevant_row_ids = [x for x in range(table.shape[0]) if x != perfect_row_id]
                fullset_ids = irrelevant_row_ids[:noisy_gnd_num] + [perfect_row_id]
                table_used = table.loc[fullset_ids]
                fuzzy_str = [format_grounding(x, table_used) for x in range(table_used.shape[0])]
                table_columns = [x for x in table.columns if x not in ['titleintro', 'sectionintro', 'url', 'uid']]
                try:
                    col_with_values = ['{}: {}'.format(x, ', '.join(table[y].unique()[:3])) for x, y in zip(NL_columns[:-4], table_columns)]
                except:
                    col_with_values = table_columns
                col_with_values = [x for x in col_with_values if complex_answer not in x]
                t0 = time.time()
                described_attributes = self.answer_machine.llm.execute('describe_attributes', {'attribute': '\n'.join(col_with_values),})
                matched_attributes = self.answer_machine.llm.execute('extract_constraints',
                                                                     {'columns': described_attributes,
                                                                      'question': user_question})
                aligned_result = []
                filtered_candidates = fuzzy_str
                for line in matched_attributes.split('\n'):
                    if len(filtered_candidates) <= 1:
                        break
                    if 'None' in line: continue
                    try:
                        column_value, condition = line.split('|')
                    except:
                        continue
                    column_value = column_value.strip()
                    condition = condition.strip()
                    try:
                        possible_values = table_used['_'.join(normalize_value(column_value).split())].unique()
                        attr_str = '{} with possible values of {}.'.format(column_value, possible_values)
                        value_options = '\n'.join(possible_values)
                    except:
                        continue
                    cr_rst = self.answer_machine.llm.execute('confident_match_values', {'question': user_question, 'constraint': condition, "options": value_options})
                    if 'None' in cr_rst:
                        # ask a question regarding this condition
                        system_question = self.clarify_machine.generate_system_question(question=condition, attribute=attr_str)
                        user_answer = self.user_simulator.respond(goal=user_question, current_question=system_question, grounding=deanswered_gold_grounding)

                        aligned_result.append('Clarifying question: {} Answer: {}'.format(system_question.strip(), user_answer))
                    else:
                        aligned_result.append('{}'.format(cr_rst))

                    try:
                        to_exam_ans = aligned_result[-1] if 'Answer:' not in aligned_result[-1] else \
                        aligned_result[-1].split('Answer:')[1].strip()
                        to_exam_ans = normalize_value(to_exam_ans).replace(' ', '')
                        refered = [normalize_value(x).replace(' ', '') for x in possible_values]
                        refered = [x for x in refered if x in to_exam_ans or to_exam_ans in x][0]
                        filtered_candidates = [x for x in filtered_candidates if
                                               normalize_value(x).replace(' ',
                                                                          '') in refered or refered in normalize_value(
                                                   x).replace(' ', '')]
                    except:
                        try:
                            to_exam_ans = aligned_result[-1]
                            to_exam_ans = normalize_value(to_exam_ans).replace(' ', '')
                            refered = [normalize_value(x).replace(' ', '') for x in possible_values]
                            refered = [x for x in refered if x in to_exam_ans or to_exam_ans in x][0]
                            filtered_candidates = [x for x in filtered_candidates if
                                                   normalize_value(x).replace(' ',
                                                                              '') in refered or refered in normalize_value(
                                                       x).replace(' ', '')]
                        except:
                            aligned_result = aligned_result[:-1]
                            pass
                if len(filtered_candidates) > 1:
                    col_question = [x for x in table_columns if x not in user_question]
                    used_grounding = '\n###\n'.join(filtered_candidates)
                    deanswered_gold_grounding = format_grounding(perfect_row_id, table, exclude_value=complex_answer)
                    # here need to know the previous results ? No, direct ask is fine, but asked feature shall be
                    system_question = self.clarify_machine.generate_system_question(question=user_question, used_grounding=used_grounding, attrs=col_question)
                    if system_question is not None:
                        user_answer = self.user_simulator.respond(goal=user_question, current_question=system_question, grounding=deanswered_gold_grounding)
                        aligned_result = aligned_result + ['Clarifying question: {} Answer: {}'.format(system_question, user_answer)]

                used_analyze = '\n'.join(['{}. {}'.format(i + 1, x) for i, x in enumerate(aligned_result)])
                answer = self.answer_machine.llm.execute('answer-select', {'grounding': '\n'.join(fuzzy_str), 'clarify': used_analyze, 'question': user_question})
                coverage, hallucination = self.evaluator.end2end(simple_question, complex_answer, deanswered_gold_grounding, answer, used_analyze)
                result_dict = {'#irrelevant': [noisy_gnd_num], 'question': [user_question], 'answer': [answer], 'gold': [complex_answer],
                               'knowledge': [fuzzy_str], 'analyze': [used_analyze],
                               'hallucination': [hallucination], 'coverage': [coverage]}
                df = pd.DataFrame.from_dict(result_dict)
                df.to_csv('./result.csv', mode='a', header=header_use)
                header_use = False
            data_idx += 1
        print('done')
        import ipdb;ipdb.set_trace()


if __name__ == '__main__':
    args = get_parser()
    evaluator = EvaluationPipeline(args)