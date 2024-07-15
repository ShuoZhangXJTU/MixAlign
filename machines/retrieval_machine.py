from machines.sql_machine import SQLMachine

class RetrievalMachine(SQLMachine):
    def __init__(self, llm, args):
        super(RetrievalMachine, self).__init__()
        self.llm = llm
