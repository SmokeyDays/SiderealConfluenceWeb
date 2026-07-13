import asyncio
import json
import random
import re
import time

import openai
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

from server.agent.interface import llm_manager
from server.agent.prompt_template import load_prompt
from server.utils.config import get_config
from server.utils.log import logger
from server.agent.handler_schemas import SCHEMAS

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
    self.vlm = vlm
    self.chain = vlm | RunnableLambda(clean_json_output) | parser
    self.fc_available = None
    self.fc_stats = {
      "attempts": 0,
      "successes": 0,
      "failures": 0,
    }
    self.use_multi_chain = False
    if self.use_multi_chain:
      self.chains = [self.chain]
      self.vlms = [self.vlm]
      for alt in llm_manager.multi_api_alts:
        self.chains.append(alt | RunnableLambda(clean_json_output) | parser)
        self.vlms.append(alt)

  def get_chain(self):
    if self.use_multi_chain:
      return random.choice(self.chains)
    return self.chain
  
  def get_vlm(self):
    if self.use_multi_chain:
      return random.choice(self.vlms)
    return self.vlm

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

  @staticmethod
  def _guess_json_type(hint: str):
    lowered = hint.lower()
    if "int" in lowered:
      return "integer"
    if "bool" in lowered:
      return "boolean"
    if "dict" in lowered or "map" in lowered or "object" in lowered:
      return "object"
    if "list" in lowered or "array" in lowered or lowered.strip().startswith("["):
      return "array"
    if "float" in lowered or "double" in lowered or "number" in lowered:
      return "number"
    return "string"
  
  @staticmethod
  def _guess_array_items_schema(hint: str):
    lowered = hint.lower()
    if "dict[" in lowered or "list[dict" in lowered or "list<object" in lowered:
      return {"type": "object", "additionalProperties": True}
    if "list[int" in lowered or "array[int" in lowered:
      return {"type": "integer"}
    if "list[number" in lowered or "list[float" in lowered or "array[number" in lowered:
      return {"type": "number"}
    if "list[bool" in lowered or "array[bool" in lowered:
      return {"type": "boolean"}
    # Common cases like "[player1, player2, ...]" or List[str]
    return {"type": "string"}

  def _build_property_schema(self, hint: str):
    json_type = self._guess_json_type(hint)
    schema = {
      "type": json_type,
      "description": hint
    }
    if json_type == "array":
      # OpenAI tool schema requires `items` for every array type.
      schema["items"] = self._guess_array_items_schema(hint)
    elif json_type == "object":
      # Keep object permissive because many handlers use free-form payloads.
      schema["additionalProperties"] = True
    return schema

  def _build_function_tools(self, handlers_map):
    if not handlers_map:
      return []
    tools = []
    for fn_name, fn in handlers_map.items():
      doc = (fn.__doc__ or "").strip()
      doc_lines = [line.strip() for line in doc.splitlines() if line.strip()]
      description = doc if doc_lines else f"Call {fn_name}"
      # If an explicit schema is registered for this handler, prefer it.
      explicit = SCHEMAS.get(fn_name)
      if explicit:
        parameters = explicit
      else:
        properties = {}
        for line in doc_lines[1:]:
          if not line.startswith("- "):
            continue
          content = line[2:].strip()
          if ":" not in content:
            continue
          key, hint = content.split(":", 1)
          key = key.strip()
          hint = hint.strip()
          if not key:
            continue
          properties[key] = self._build_property_schema(hint)

        if not properties:
          properties = {
            "data": {
              "type": "object",
              "description": "Data payload for this action.",
              "additionalProperties": True
            }
          }

        parameters = {
          "type": "object",
          "properties": properties,
          "additionalProperties": True
        }

      tools.append({
        "type": "function",
        "function": {
          "name": fn_name,
          "description": description,
          "parameters": parameters
        }
      })
    # logger.info(f"===Functional Calling=== Tools schema: {json.dumps(tools, ensure_ascii=False)[:2000]}")
    return tools

  @staticmethod
  def _normalize_action_args(args):
    if not isinstance(args, dict):
      return {}
    if "data" in args and isinstance(args["data"], dict):
      return args["data"]
    return args

  def _build_fc_response(self, ai_msg):
    response = {}
    raw_content = ai_msg.content if hasattr(ai_msg, "content") else ""
    if isinstance(raw_content, str):
      cleaned = clean_json_output(raw_content)
      if cleaned:
        try:
          parsed = json.loads(cleaned)
          if isinstance(parsed, dict):
            response.update(parsed)
        except Exception:
          # Keep non-JSON text as reasoning fallback.
          response["reasoning"] = cleaned

    tool_calls = getattr(ai_msg, "tool_calls", []) or []
    logger.info(f"===Functional Calling=== Raw tool calls from model: {tool_calls}")
    actions = []
    for call in tool_calls:
      name = call.get("name")
      args = self._normalize_action_args(call.get("args", {}))
      if not name:
        continue
      actions.append({"func": name, "data": args})

    if actions:
      response["actions"] = actions
    else:
      response.setdefault("actions", [])
    try:
      logger.info(f"===Functional Calling=== Built FC response: {json.dumps(response, ensure_ascii=False)[:1000]}")
    except Exception:
      logger.info("===Functional Calling=== Built FC response (non-serializable)\n")
    return response

  def _is_fc_enabled(self):
    mode = str(get_config("agent_function_calling_mode")).lower()
    if mode == "off":
      return False
    if mode == "on":
      return True
    # auto mode
    return self.fc_available is not False

  def _invoke_legacy(self, message):
    return self.get_chain().invoke(message)

  async def _ainvoke_legacy(self, message):
    return await self.get_chain().ainvoke(message)

  def _invoke_with_fc(self, message, handlers_map):
    tools = self._build_function_tools(handlers_map)
    if not tools or not self._is_fc_enabled():
      return self._invoke_legacy(message)
    self.fc_stats["attempts"] += 1
    try:
      logger.info(f"===Functional Calling=== {self.planner_name} attempting FC invoke. Tools: {len(tools)}")
      llm_with_tools = self.get_vlm().bind_tools(tools, tool_choice="auto")
      ai_msg = llm_with_tools.invoke(message)
      self.fc_available = True
      response = self._build_fc_response(ai_msg)
      self.fc_stats["successes"] += 1
      try:
        logger.info(f"===Functional Calling=== {self.planner_name} FC invoke succeeded. Actions: {len(response.get('actions', []))}")
      except Exception:
        logger.info(f"===Functional Calling=== {self.planner_name} FC invoke succeeded.")
      return response
    except Exception as e:
      self.fc_stats["failures"] += 1
      logger.warning(f"{self.planner_name} FC invoke failed, fallback to legacy mode: {e}")
      logger.info(f"===Functional Calling=== {self.planner_name} FC invoke failed, falling back to legacy mode")
      # In auto mode, disable FC after first incompatibility.
      if str(get_config("agent_function_calling_mode")).lower() == "auto":
        self.fc_available = False
      return self._invoke_legacy(message)

  async def _ainvoke_with_fc(self, message, handlers_map):
    tools = self._build_function_tools(handlers_map)
    if not tools or not self._is_fc_enabled():
      return await self._ainvoke_legacy(message)
    self.fc_stats["attempts"] += 1
    try:
      logger.info(f"===Functional Calling=== {self.planner_name} attempting async FC invoke. Tools: {len(tools)}")
      llm_with_tools = self.get_vlm().bind_tools(tools, tool_choice="auto")
      ai_msg = await llm_with_tools.ainvoke(message)
      self.fc_available = True
      response = self._build_fc_response(ai_msg)
      self.fc_stats["successes"] += 1
      try:
        logger.info(f"===Functional Calling=== {self.planner_name} async FC invoke succeeded. Actions: {len(response.get('actions', []))}")
      except Exception:
        logger.info(f"===Functional Calling=== {self.planner_name} async FC invoke succeeded.")
      return response
    except Exception as e:
      self.fc_stats["failures"] += 1
      logger.warning(f"{self.planner_name} async FC invoke failed, fallback to legacy mode: {e}")
      logger.info(f"===Functional Calling=== {self.planner_name} async FC invoke failed, falling back to legacy mode")
      if str(get_config("agent_function_calling_mode")).lower() == "auto":
        self.fc_available = False
      return await self._ainvoke_legacy(message)

  def plan(self, chapters, handlers_map=None):
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
          long_term_plan = self._invoke_with_fc(message, handlers_map)
          
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

  async def aplan(self, chapters, handlers_map=None):
    system_message = self.render_system_message()
    if get_config("agent_function_calling_mode") == "on" or (str(get_config("agent_function_calling_mode") == "auto") and self.fc_available is not False):
      # remove key "Actions"
      chapters = [(k, v) for k, v in chapters if k != "Actions"]
    human_message = self.render_human_message(chapters)
    message = [system_message, human_message]
    long_term_plan = {}
    
    logger.info(f"****{self.planner_name}****\n{system_message.content}\n{str_msg(human_message)}")
    
    max_retries = 3
    attempt = 0

    while attempt < max_retries:
      try:
        with get_openai_callback() as cb:
          long_term_plan = await self._ainvoke_with_fc(message, handlers_map)
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
        logger.warning(f"Async Plan attempt against model {self.model_name} {attempt}/{max_retries} failed: {e}")
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


def _healthcheck_tool(payload: str, api_name: str = ""):
  """Echo a payload to verify function calling.

  - payload: string payload to echo back
  - api_name: string API label for the report
  """


def _render_healthcheck_chapters(api_name: str):
  return [
    ("API", f"当前正在测试 {api_name} 的基础连通性和函数调用能力。"),
    (
      "Task",
      "请先用一句话确认你已收到测试请求，然后如果支持函数调用，请调用 healthcheck_tool，"
      "并把 payload 设置为 'fc-ok:' 加上当前 API 名称。"
    ),
  ]


def _message_to_text(value):
  if isinstance(value, BaseMessage):
    value = value.content
  if isinstance(value, list):
    return json.dumps(value, ensure_ascii=False)
  if isinstance(value, dict):
    return json.dumps(value, ensure_ascii=False)
  if value is None:
    return ""
  return str(value)


def run_llm_api_healthcheck():
  targets = []
  for model_name, api in llm_manager.registry.items():
    targets.append((model_name, api))
  report = []
  print("=== LLM API Healthcheck Start ===")
  print(f"Default bot type: {get_config('default_bot_type')}")
  print(f"Function calling mode: {get_config('agent_function_calling_mode')}")

  for api_name, api in targets:
    caller = BasicCaller(
      vlm=api,
      planner_name=f"Healthcheck[{api_name}]",
      prompt_file="turn_plan",
    )
    chapters = _render_healthcheck_chapters(api_name)
    message = [caller.render_system_message(), caller.render_human_message(chapters)]

    item = {
      "api_name": api_name,
      "provider": type(api).__name__,
      "legacy": {
        "ok": False,
        "content": "",
        "tokens": 0,
        "cost": 0,
        "error": "",
      },
      "fc": {
        "ok": False,
        "actions": [],
        "content": "",
        "tokens": 0,
        "cost": 0,
        "error": "",
      },
    }

    try:
      with get_openai_callback() as cb:
        legacy_response = caller.get_vlm().invoke(message)
      item["legacy"]["ok"] = True
      item["legacy"]["content"] = _message_to_text(legacy_response)
      item["legacy"]["tokens"] = cb.total_tokens
      item["legacy"]["cost"] = cb.total_cost
    except Exception as exc:
      item["legacy"]["error"] = str(exc)

    try:
      with get_openai_callback() as cb:
        fc_response = caller._invoke_with_fc(message, {"healthcheck_tool": _healthcheck_tool})
      item["fc"]["tokens"] = cb.total_tokens
      item["fc"]["cost"] = cb.total_cost
      if isinstance(fc_response, dict):
        item["fc"]["actions"] = fc_response.get("actions", []) or []
        item["fc"]["content"] = _message_to_text(fc_response)
        item["fc"]["ok"] = len(item["fc"]["actions"]) > 0
      else:
        item["fc"]["content"] = _message_to_text(fc_response)
        item["fc"]["ok"] = bool(item["fc"]["content"])
    except Exception as exc:
      item["fc"]["error"] = str(exc)

    report.append(item)

    print(f"\n[{api_name}] {item['provider']}")
    print(f"  legacy: {'PASS' if item['legacy']['ok'] else 'FAIL'}")
    if item["legacy"]["error"]:
      print(f"    error: {item['legacy']['error']}")
    else:
      print(f"    content: {item['legacy']['content'][:240]}")
    print(f"    tokens/cost: {item['legacy']['tokens']} / {item['legacy']['cost']}")

    print(f"  fc: {'PASS' if item['fc']['ok'] else 'FAIL'}")
    if item["fc"]["error"]:
      print(f"    error: {item['fc']['error']}")
    else:
      print(f"    actions: {json.dumps(item['fc']['actions'], ensure_ascii=False)}")
      print(f"    content: {item['fc']['content'][:240]}")
    print(f"    tokens/cost: {item['fc']['tokens']} / {item['fc']['cost']}")

  legacy_pass_count = sum(1 for item in report if item["legacy"]["ok"])
  fc_pass_count = sum(1 for item in report if item["fc"]["ok"])

  summary = {
    "total": len(report),
    "legacy_pass": legacy_pass_count,
    "legacy_fail": len(report) - legacy_pass_count,
    "fc_pass": fc_pass_count,
    "fc_fail": len(report) - fc_pass_count,
    "report": report,
  }

  print("\n=== Summary ===")
  print(f"Legacy pass: {legacy_pass_count}/{len(report)}")
  print(f"FC pass: {fc_pass_count}/{len(report)}")
  # Simple table: API | LEGACY | FC
  header = f"{'API':30} {'LEGACY':7} {'FC':7}"
  print('\n' + header)
  print('-' * len(header))
  for it in report:
    api_label = it['api_name'][:30]
    legacy_status = 'PASS' if it['legacy']['ok'] else 'FAIL'
    fc_status = 'PASS' if it['fc']['ok'] else 'FAIL'
    print(f"{api_label:30} {legacy_status:7} {fc_status:7}")
  return summary


if __name__ == '__main__':
  run_llm_api_healthcheck()
