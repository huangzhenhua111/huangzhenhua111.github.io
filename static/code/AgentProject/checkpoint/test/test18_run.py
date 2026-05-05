from masfactory import RootGraph, Agent, HistoryMemory, SimpleKeywordRetriever, OpenAIModel,Graph
from masfactory.checkpoint.manager import CheckpointManager
from masfactory.checkpoint.storage import FileCheckpointStorage

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent/".env")

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

g=RootGraph("test18")
inner0=g.create_node(
    Graph,
    "inner0"
)

inner=g.create_node(
    Graph,
    "inner"
)

agent1=inner.create_node(
    Agent,
    "agent1",
    instructions="你是高斯,你看到count就想把它加1",
    model=model,
    memories=[history],
    retrievers=[retriever]
)
agent2=inner.create_node(
    Agent,
    "agent2",
    instructions="你是高斯,你看到count就想把它加1",
    model=model_bad,
    memories=[history],
    retrievers=[retriever]
)

g.edge_from_entry(inner0,{"count":""})

inner0.edge_from_entry(inner0._exit,{"count":""})

g.create_edge(inner0,inner,{"count":""})

inner.edge_from_entry(agent1,{"count":""})
inner.create_edge(agent1,agent2,{"count":""})
inner.edge_to_exit(agent2,{"count":""})

g.edge_to_exit(inner,{"count":""})

g.build()

storage=FileCheckpointStorage(str(Path(__file__).parent))
manager=CheckpointManager(g,storage,"graph")
manager.attach_hooks()

try:
    out,_=g.invoke({"count":0})
    print(out)
except Exception as err:
    print("错误",err)
    print("最近 checkpoint:", manager.last_checkpoint_path)