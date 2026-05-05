import sys
sys.path.insert(0,"/home/huangzhenhua/workspace/LearnAgent/checkpoint/MASFactory")
from masfactory import HistoryMemory

history=HistoryMemory()
history.insert("user","hello")
history.insert("assistant","hi")
state=history.get_checkpoint_state()
print("======saved=====")
print(state)

history.insert("user","changed")
print("=======改变后======")
print(history.get_checkpoint_state())

history.load_checkpoint_state(state)
print("=======恢复后=======")
print(history.get_checkpoint_state())