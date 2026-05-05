from masfactory import RootGraph, Agent, HistoryMemory, SimpleKeywordRetriever, OpenAIModel
from masfactory.checkpoint.collector import CheckpointCollector
from masfactory.checkpoint.restorer import CheckpointRestorer
from masfactory.checkpoint.manager import CheckpointManager
from masfactory.checkpoint.storage import FileCheckpointStorage
import os
from dotenv import load_dotenv

load_dotenv("/home/huangzhenhua/workspace/LearnAgent/test_checkpoint/.env")

model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or None,
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
)


history=HistoryMemory()
history.insert("user","东西是老的")
retriever=SimpleKeywordRetriever({"doc1":"这个也是老的"})

g=RootGraph("test13")

agent=g.create_node(
    Agent,
    "agent1",
    instructions="你是个agent助手,帮我测试",
    model=model,
    memories=[history],
    retrievers=[retriever]
)

storage=FileCheckpointStorage("/home/huangzhenhua/workspace/LearnAgent/test_checkpoint")
manager=CheckpointManager(g,storage)
path_str=manager.save()

print("======老的自己去看文件======")
print()

history.insert("user","东西是新的")
retriever._documents["doc2"]="这个也是新的"
print("=====新的======")
print(history.get_checkpoint_state())
print(retriever.get_checkpoint_state())

manager.load(path_str)

print("=======是老的吗？======")
print(history.get_checkpoint_state())
print(retriever.get_checkpoint_state())