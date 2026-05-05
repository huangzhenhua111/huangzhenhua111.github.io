import sys
sys.path.insert(0, "/home/huangzhenhua/workspace/LearnAgent/checkpoint/MASFactory")
from masfactory import CustomNode,RootGraph,Node,Edge
from masfactory.checkpoint.collector import CheckpointCollector
from masfactory.checkpoint.storage import FileCheckpointStorage
def forward1(message,attribute):
    count=message["count"]
    count+=1
    return {"count":count}

def forward2(message,attribute):
    count=message["count"]
    count+=1
    return {"count":count}

def hook_func(node, result, outer_env=None):
    
    state=collector.collect(g)
    storage.save(state)

collector=CheckpointCollector()
storage=FileCheckpointStorage(".")
g=RootGraph("test04")
n1=g.create_node(CustomNode,"n1",forward1,attributes={"x":1})
n2=g.create_node(CustomNode,"n2",forward2)
e1=g.create_edge(n1,n2,keys={"count":""})

e_entry_n1 = g.edge_from_entry(n1,{"count":""})
e_n2_exit = g.edge_to_exit(n2,{"count":""})
g.build()

# n1.hook_register(Node.Hook.EXECUTE.AFTER,hook_func)
# n2.hook_register(Node.Hook.EXECUTE.AFTER,hook_func)
g.hook_register(
    Node.Hook.EXECUTE.AFTER,
    hook_func,
    recursion=True,
)


out,_=g.invoke({"count":0})
print(f'count:{out["count"]}')