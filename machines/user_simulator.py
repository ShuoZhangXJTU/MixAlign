
class UserSimulator:
    def __init__(self, llm):
        self.llm = llm

    def respond(self, goal, current_question, grounding=None):
        return self.llm.execute(method_name='user_simulator', input_dict={'question': goal, 'sys_question': current_question, 'detail':grounding})

