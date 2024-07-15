

class ClarifyMachine:
    def __init__(self, llm):
        self.llm = llm

    def generate_system_question(self, question, used_grounding=None, attribute=None, attrs=None):
        if used_grounding:
            question_result = self.llm.execute(method_name='select-and-ask', input_dict={'question': question,
                                                                                   'grounding': used_grounding, 'attrs': attrs})

        elif attribute:
            question_result = self.llm.execute(method_name='align-ask',
                                               input_dict={'question': question, 'grounding': attribute})
        try:
            return [x for x in question_result.split('\n') if len(x.strip()) > 0][0]
        except:
            return None

