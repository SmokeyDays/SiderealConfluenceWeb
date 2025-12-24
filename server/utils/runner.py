# server/runner.py
import asyncio
import threading
from server.utils.log import logger

class AsyncBotRunner:
  def __init__(self):
    self.loop = None
    self.thread = None
    self.start()

  def start(self):
    if self.thread is not None:
      return
    self.loop = asyncio.new_event_loop()
    self.thread = threading.Thread(target=self._start_loop, args=(self.loop,), daemon=True)
    self.thread.start()
    logger.info("AsyncBotRunner background loop started.")

  def _start_loop(self, loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

  def run_task(self, coro):
    if self.loop is None:
      logger.error("AsyncBotRunner loop is not running!")
      return None
    
    # run_coroutine_threadsafe 是跨线程调用的关键
    future = asyncio.run_coroutine_threadsafe(coro, self.loop)
    return future

# 全局单例
bot_runner = AsyncBotRunner()