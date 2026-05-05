import os
from pathlib import Path
from dotenv import load_dotenv

from masfactory import Agent, HistoryMemory, OpenAIModel


load_dotenv(Path(__file__).parent/".env")

model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or None,
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
)

history = HistoryMemory()

agent = Agent(
    "chat_agent",
    instructions=(
        "你是一个测试助手。"
        "你必须只输出严格 JSON，例如 {\"answer\": \"...\"}。"
    ),
    model=model,
    memories=[history],
    max_retries=1,
)

print("===== 第一轮开始 =====")
out1 = agent.step({"message": "请回复 answer 为 hello"})
print("第一轮输出:")
print(out1)

print("第一轮后的 HistoryMemory:")
print(history.get_checkpoint_state())

print("===== 第二轮开始 =====")
try:
    out2 = agent.step({"message": "请回复 answer 为 world"})
    print(out2)
except Exception as err:
    print("外层错误类型:", type(err))
    print("外层错误:", repr(err))

    if hasattr(err, "last_attempt"):
        real_err = err.last_attempt.exception()
        print("真实错误类型:", type(real_err))
        print("真实错误:", repr(real_err))

