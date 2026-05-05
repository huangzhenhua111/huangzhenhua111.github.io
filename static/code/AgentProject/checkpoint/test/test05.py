import sys
sys.path.insert(0, "/home/huangzhenhua/workspace/LearnAgent/checkpoint/MASFactory")
from masfactory import CustomNode,RootGraph,Node,Edge
from masfactory.checkpoint.collector import CheckpointCollector
from masfactory.checkpoint.storage import FileCheckpointStorage
from masfactory.checkpoint.restorer import CheckpointRestorer
def forward1(message,attribute):
    count=message["count"]
    count+=1
    return {"count":count}

def forward2(message,attribute):
    count=message["count"]
    count+=1
    return {"count":count}

g=RootGraph("test04")
n1=g.create_node(CustomNode,"n1",forward1,attributes={"x":1})
n2=g.create_node(CustomNode,"n2",forward2)
e1=g.create_edge(n1,n2,keys={"count":""})

e_entry_n1 = g.edge_from_entry(n1,{"count":""})
e_n2_exit = g.edge_to_exit(n2,{"count":""})
g.build()

storage=FileCheckpointStorage("/home/huangzhenhua/workspace/LearnAgent/test_checkpoint")
checkpoint_state=storage.load("/home/huangzhenhua/workspace/LearnAgent/test_checkpoint/checkpoint001.json")
restorer=CheckpointRestorer()
restorer.restore(g,checkpoint_state)

print("=============恢复后===============")
print(e1.get_checkpoint_state())




