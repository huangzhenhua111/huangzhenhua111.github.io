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

model_bad = OpenAIModel(
    api_key="OPENAI_API_KEY 错误在这里！！！",
    base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or None,
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
)

history=HistoryMemory()
history.insert("user","东西是老的")
retriever=SimpleKeywordRetriever({"doc1":"这个也是老的"})

g=RootGraph("test14")

agent1=g.create_node(
    Agent,
    "agent1",
    instructions="你是高斯,你看到count就想把它加1",
    model=model,
    memories=[history],
    retrievers=[retriever]
)
agent2=g.create_node(
    Agent,
    "agent2",
    instructions="你是高斯,你看到count就想把它加1",
    model=model_bad,
    memories=[history],
    retrievers=[retriever]
)

e1=g.edge_from_entry(agent1,{"count":""})
e2=g.create_edge(agent1,agent2,{"count":""})
e3=g.edge_to_exit(agent2,{"count":""})

g.build()

storage=FileCheckpointStorage("/home/huangzhenhua/workspace/LearnAgent/test_checkpoint")
manager=CheckpointManager(g,storage)
manager.attach_hooks()

try:
    out,_=g.invoke({"count":0})
    print(out)
except Exception as err:
    print("错误",err)
    print("最近 checkpoint:", manager.last_checkpoint_path)