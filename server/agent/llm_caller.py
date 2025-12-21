from abc import abstractmethod
import random
from server.agent.prompt_template import load_prompt
from langchain_openai import AzureChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from server.agent.interface import langchain_llms_api, langchain_vlm_api, langchain_llms_api_alts
# from server.agent.parser import buildingStrategies, citizenActionParser
from server.utils.log import logger
LLMs_total_tokens = 0
LLMs_total_cost = 0

def add_LLMs_total_tokens(tokens):
  global LLMs_total_tokens
  LLMs_total_tokens += tokens

def add_LLMs_total_cost(cost):
  global LLMs_total_cost
  LLMs_total_cost += cost

def get_LLMs_total_tokens():
  global LLMs_total_tokens
  return LLMs_total_tokens

def get_LLMs_total_cost():
  global LLMs_total_cost
  return LLMs_total_cost

class LongtermPlan(BaseModel):
  reasoning: str = Field(description="reasoning")
  goal: str = Field(description="goal")
  long_term_plan: str = Field(description="long-term-plan")

def str_msg(msg):
  res = ""
  for item in msg.content:
    if item['type'] == 'text':
      res += item['text']
  return res
class BasicCaller():
  def __init__(self,
        model_name = 'gpt-4o-mini',
        max_tokens = 1024,
        temperature = 0,
        vlm = langchain_llms_api,
        parser = JsonOutputParser(pydantic_object=LongtermPlan),
        prompt_file = "turn_plan",
        planner_name = "BasicCaller",
        vision = False,):
    
    self.model_name = model_name
    self.max_tokens = max_tokens
    self.temperature = temperature
    self.vision = vision

    self.prompt_file = prompt_file
    self.planner_name = planner_name
    self.chain = vlm | parser
    self.use_multi_chain = False
    if self.use_multi_chain:
      self.chains = [self.chain]
      for alt in langchain_llms_api_alts:
        self.chains.append(alt | parser)

  def get_chain(self):
    if self.use_multi_chain:
      return random.choice(self.chains)
    return self.chain

  def render_system_message(self):
    system_prompt = load_prompt(self.prompt_file)
    return SystemMessage(content=system_prompt)

  def render_human_message(self, chapters, verbose = True):
    content = []
    text = ""
    for k, v in chapters.items():
      text += f"### {k}\n"
      text += v
      text += "\n"
    content.append({"type": "text", "text": text})

    human_message = HumanMessage(content=content)

    return human_message


  def plan(self, chapters):

    system_message = self.render_system_message()
    human_message = self.render_human_message(chapters)

    message = [system_message, human_message]
    long_term_plan = {}
    logger.info(f"****{self.planner_name}****\n{system_message.content}\n{str_msg(human_message)}")
    try:
      with get_openai_callback() as cb:
        long_term_plan = self.get_chain().invoke(message)
        logger.info(f"""
LLMs Called:
Total tokens: {cb.total_tokens}, Total cost: {cb.total_cost}, 
Prompt tokens: {cb.prompt_tokens}, Completion tokens: {cb.completion_tokens}""")
        logger.info(f"LLMs total tokens: {LLMs_total_tokens}")
        logger.info(f"LLMs total cost: {LLMs_total_cost}")
        total_tokens = cb.total_tokens
        add_LLMs_total_tokens(total_tokens)
        total_cost = cb.total_cost
        add_LLMs_total_cost(total_cost)
      logger.info(f"****{self.planner_name}****\n{long_term_plan}")
    except Exception as e:
      import traceback
      logger.error(f"Plan failed: {e}, {traceback.format_exc()}")
    
    return long_term_plan
  
class TurnPlanCaller(BasicCaller):
  def __init__(self,
         model_name = 'gpt-4o-mini',
         max_tokens = 1024,
         temperature = 0,
         vlm = langchain_llms_api,
         parser = JsonOutputParser(pydantic_object=LongtermPlan),
         prompt_file = "turn_plan",
         planner_name = "TurnPlanCaller",
         vision = False,):
      super().__init__(
        model_name,
        max_tokens, 
        temperature, 
        vlm = vlm, 
        parser = parser,
        prompt_file = prompt_file,
        planner_name = planner_name,
        vision = vision
      )

class TradeCaller(BasicCaller):
  def __init__(self,
      model_name = 'gpt-4o-mini',
      max_tokens = 1024,
      temperature = 0,
      vlm = langchain_llms_api,
      parser = JsonOutputParser(pydantic_object=LongtermPlan),
      prompt_file = "trade_plan",
      planner_name = "TradeCaller",
      vision = False,):
    super().__init__(
      model_name,
                  max_tokens, 
                  temperature, 
                  vlm = vlm, 
                  parser = parser,
                  prompt_file = prompt_file,
                  planner_name = planner_name,
                  vision = vision)


if __name__ == '__main__':
  turnPlanCaller = TurnPlanCaller()
  observation = ""
  handler = ""
  print(turnPlanCaller.plan("", observation, handler))
  # test_longterm_planner()
  # test_building_planner()
  # test_citizen_planner()
  # test_city_expansion_planner()