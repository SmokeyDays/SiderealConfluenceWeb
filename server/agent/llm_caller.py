from abc import abstractmethod
from datetime import time
import random
import asyncio

import openai
from server.agent.prompt_template import load_prompt
from langchain_openai import AzureChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
from server.agent.interface import llm_manager
# from server.agent.parser import buildingStrategies, citizenActionParser
from server.utils.log import logger
import re
from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableLambda

def clean_json_output(output):
    content = output.content if isinstance(output, BaseMessage) else output
    
    # Remove markdown code blocks
    if "```" in content:
        pattern = r"```(?:json)?\s*(.*?)```"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
            
    # Remove inline comments //
    pattern = r'("(?:\\.|[^"\\])*")|(\/\/.*)'
    
    def replace_func(match):
        if match.group(1):
            return match.group(1)
        else:
            return ""
            
    content = re.sub(pattern, replace_func, content)
    
    return content.strip()

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
        vlm = llm_manager.default_api,
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
    self.chain = vlm | RunnableLambda(clean_json_output) | parser
    self.use_multi_chain = False
    if self.use_multi_chain:
      self.chains = [self.chain]
      for alt in llm_manager.multi_api_alts:
        self.chains.append(alt | RunnableLambda(clean_json_output) | parser)

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
    for k, v in chapters:
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

    max_retries = 3
    attempt = 0

    while attempt < max_retries:
      try:
        with get_openai_callback() as cb:
          long_term_plan = self.get_chain().invoke(message)
          
          logger.info(f"""
LLMs Called:
Total tokens: {cb.total_tokens}, Total cost: {cb.total_cost}, 
Prompt tokens: {cb.prompt_tokens}, Completion tokens: {cb.completion_tokens}
Total tokens: {get_LLMs_total_tokens()}, Total cost: {get_LLMs_total_cost()}""")
          add_LLMs_total_tokens(cb.total_tokens)
          add_LLMs_total_cost(cb.total_cost)
        
        logger.info(f"****{self.planner_name}****\n{long_term_plan}")
        return long_term_plan
      except openai.RateLimitError as e:
        logger.warning(f"OpenAI RateLimit hit. Sleeping for 60s before retrying... (Error: {e})")
        time.sleep(60)
        continue 
      except Exception as e:
        attempt += 1
        logger.warning(f"Plan attempt {attempt}/{max_retries} failed: {e}")
        if attempt >= max_retries:
          import traceback
          logger.error(f"Plan failed after {max_retries} attempts: {e}, {traceback.format_exc()}")
          return {}
    
    return long_term_plan

  async def aplan(self, chapters):
    system_message = self.render_system_message()
    human_message = self.render_human_message(chapters)
    message = [system_message, human_message]
    long_term_plan = {}
    
    logger.info(f"****{self.planner_name}****\n{system_message.content}\n{str_msg(human_message)}")
    
    max_retries = 3
    attempt = 0

    while attempt < max_retries:
      try:
        with get_openai_callback() as cb:
          long_term_plan = await self.get_chain().ainvoke(message)
          logger.info(f"""
LLMs Called (Async):
Request tokens: {cb.total_tokens}, Request cost: {cb.total_cost}, 
Prompt tokens: {cb.prompt_tokens}, Completion tokens: {cb.completion_tokens}
Total tokens: {get_LLMs_total_tokens()}, Total cost: {get_LLMs_total_cost()}""")
          add_LLMs_total_tokens(cb.total_tokens)
          add_LLMs_total_cost(cb.total_cost)
          
        logger.info(f"****{self.planner_name}****\n{long_term_plan}")
        return long_term_plan
      except asyncio.CancelledError:
        logger.info(f"Bot calling {self.planner_name} was cancelled.")
        raise 
      except openai.RateLimitError as e:
        logger.warning(f"OpenAI RateLimit hit (Async). Sleeping for 60s... (Error: {e})")
        await asyncio.sleep(60)
        continue
      except Exception as e:
        attempt += 1
        logger.warning(f"Async Plan attempt {attempt}/{max_retries} failed: {e}")
        if attempt >= max_retries:
          import traceback
          logger.error(f"Plan failed after {max_retries} attempts: {e}, {traceback.format_exc()}")
          return {}
    
    return long_term_plan
  
class TurnPlanCaller(BasicCaller):
  def __init__(self,
         model_name = 'gpt-4o-mini',
         max_tokens = 1024,
         temperature = 0,
         vlm = llm_manager.default_api,
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
      vlm = llm_manager.default_api,
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

class DiscardColonyCaller(BasicCaller):
  def __init__(self,
      model_name = 'gpt-4o-mini',
      max_tokens = 1024,
      temperature = 0,
      vlm = llm_manager.default_api,
      parser = JsonOutputParser(pydantic_object=LongtermPlan),
      prompt_file = "discard_colony_plan",
      planner_name = "DiscardCaller",
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


class EconomyCaller(BasicCaller):
  def __init__(self,
      model_name = 'gpt-4o-mini',
      max_tokens = 1024,
      temperature = 0,
      vlm = llm_manager.default_api,
      parser = JsonOutputParser(pydantic_object=LongtermPlan),
      prompt_file = "economy_plan",
      planner_name = "EconomyCaller",
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


class BidCaller(BasicCaller):
  def __init__(self,
      model_name = 'gpt-4o-mini',
      max_tokens = 1024,
      temperature = 0,
      vlm = llm_manager.default_api,
      parser = JsonOutputParser(pydantic_object=LongtermPlan),
      prompt_file = "bid_plan",
      planner_name = "BidCaller",
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

class PickCaller(BasicCaller):
  def __init__(self,
      model_name = 'gpt-4o-mini',
      max_tokens = 1024,
      temperature = 0,
      vlm = llm_manager.default_api,
      parser = JsonOutputParser(pydantic_object=LongtermPlan),
      prompt_file = "pick_plan",
      planner_name = "PickCaller",
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
  wrong_json = """```
{
  "reasoning": "I need to bid ships on both colonies and technology research teams to maximize my chances of acquiring valuable assets. Given my current resources and the available options, I will allocate my ships strategically to ensure I can secure at least one colony and one research team.",
  "goal": "To acquire at least one colony and one technology research team through bidding.", // This is a comment that should be removed
  "long_term_plan": "1. Assess the available colonies and research teams on the auction track. 2. Determine the maximum number of ships I can allocate for bidding without depleting my resources. 3. Allocate ships to bid on the most valuable colony first, ensuring I have enough left to bid on a research team. 4. Monitor other players' bids and adjust my strategy accordingly in real-time."
}```"""
  print(clean_json_output(wrong_json))