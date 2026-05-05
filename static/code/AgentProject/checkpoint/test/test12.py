from masfactory import Model
from masfactory import RootGraph, Agent, HistoryMemory, SimpleKeywordRetriever, Model
from masfactory.checkpoint.collector import CheckpointCollector
from masfactory.checkpoint.restorer import CheckpointRestorer

class DummyModel(Model):
    def invoke(self, messages, tools=None, settings=None, **kwargs):
        return {
            "type": "content",
            "content": "{}",
        }

history=HistoryMemory()
history.insert("uesr","东西是老的")
retriever=SimpleKeywordRetriever({"doc1":"这个也是老的"})

g=RootGraph("test12")

agent=g.create_node(
    Agent,
    "agent1",
    instructions="你是个der",
    model=DummyModel(),
    memories=[history],
    retrievers=[retriever]
)

collector=CheckpointCollector()
state=collector.collect(g)
print("======老的=====")
print(state)

history.insert("user","东西是新的")
retriever._documents["doc2"]="这个也是新的"
print("=====新的======")
print(history.get_checkpoint_state())
print(retriever.get_checkpoint_state())

restorer=CheckpointRestorer()
restorer.restore(g,state)
print("=======是老的吗？======")
print(history.get_checkpoint_state())
print(retriever.get_checkpoint_state())