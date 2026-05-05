import sys
sys.path.insert(0, "/home/huangzhenhua/workspace/LearnAgent/checkpoint/MASFactory")
from masfactory import CustomNode,RootGraph,Node,Edge
from masfactory.checkpoint.storage import FileCheckpointStorage
from pathlib import Path 

storage=FileCheckpointStorage(str(Path(__file__).parent))

def forward(message,attributes):
    message["count"]=1
    return message
g=RootGraph("test01")
n1=g.create_node(CustomNode,"n1",forward,attributes={"x":1})
old_state=n1.get_checkpoint_state()
checkpoint_path=storage.save(old_state)


print("旧状态:")
print(old_state)
n1.attributes["x"]=999
print("changed:")
print(n1.get_checkpoint_state())


old_state=storage.load(checkpoint_path)
n1.load_checkpoint_state(old_state)


print("恢复后：")
print(n1.get_checkpoint_state())