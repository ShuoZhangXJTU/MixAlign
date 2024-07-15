import string
import re


def normalize_value(value_str):
    value_str.replace('\n', '')
    value_str = value_str.translate(str.maketrans('', '', string.punctuation))
    value_str = value_str.lower().strip()
    return value_str


def check_if_in(word, str):
    word = normalize_value(word)
    str = normalize_value(str)
    res = re.sub(r'(\W+)', lambda x: ' '+x.group(0)+' ', word).split()
    in_res = [x for x in res if x in str]
    # import ipdb;ipdb.set_trace()
    return len(res) == len(in_res)


class Evaluator:
    def __init__(self, llm):
        self.llm = llm

    def end2end(self, question, gold_answer, gold_grounding, answer, clr=None):
        gold_answer = gold_answer.strip()
        answer = answer.strip()
        if len(answer.split()) == 1:
            if answer in gold_answer or gold_answer in answer:
                return 1, 0

        hallu = self.llm.execute('e2e-hallucination', {'question':question, 'gold': gold_answer, 'context': gold_grounding, 'summary': answer})
        hallu_score = 1 if 'Yes' in hallu else 0
        cover = self.llm.execute('e2e-coverage', {'gold': gold_answer, 'summary': answer})
        cover_score = 1 if 'Yes' in cover else 0
        # if clr is not None:
        #     accept = self.llm.execute('e2e-accept', {'question_ori': question, 'question_clr': clr, 'gold': gold_answer})
        #     accept_score = 0 if 'Yes' in cover else 1
        # else:
        #     accept_score = None
        return cover_score, hallu_score