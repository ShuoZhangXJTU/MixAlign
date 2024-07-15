import torch
from evaluator import normalize_value



class SQLMachine:
    def __init__(self, args=None):
        self.online_db = None
        self.title2subtitle2table = torch.load('dataset/title2subtitle2table.pt')
        self.id2title2subtitle = torch.load('dataset/id2title2subtitle.pt')
    def fetch_doc_df(self, table_name=None):
        if table_name is None:
            table_name = self.table_name
        title, subtitle = self.id2title2subtitle[table_name]
        df = self.title2subtitle2table[title][subtitle]
        origin_columns = df.columns
        df.columns = ['_'.join(normalize_value(x).split()) for x in df.columns]
        return df, origin_columns
