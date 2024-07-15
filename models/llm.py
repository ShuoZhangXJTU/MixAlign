from models.prompt_base import BASIC_TEMPLATE
import logging
logging.basicConfig(level=logging.INFO)
from langchain import LLMChain, PromptTemplate, OpenAI
from langchain.chat_models import ChatOpenAI


class LLM:
    def __init__(self, model_name='text-davinci-002', apikey='', temperature=0.):
        if model_name in ['gpt-3.5-turbo', 'gpt-4']:
            self.llm = ChatOpenAI(model_name=model_name, openai_api_key=apikey, temperature=temperature, max_tokens=1000)
        else:
            self.llm = OpenAI(model_name=model_name, openai_api_key=apikey, temperature=temperature, max_tokens=1000)

    def execute(self, method_name, input_dict):
        base_prompt = PromptTemplate(
            input_variables=BASIC_TEMPLATE[method_name]['input_variables'],
            template=BASIC_TEMPLATE[method_name]['template']
        )
        llm_chain = LLMChain(prompt=base_prompt, llm=self.llm)
        llm_ans = llm_chain.run(input_dict)
        return llm_ans