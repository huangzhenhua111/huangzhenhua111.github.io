from masfactory import VectorMemory
import numpy as np
def fake_embedding(text: str):
    return np.array([len(text), 1.0, 2.0])
vm=VectorMemory(fake_embedding)

vm.insert("k1","hello")
state=vm.get_checkpoint_state()

print("=====东西是老的=====")
print(state)

vm.insert("k2","world")
print("=====东西是新的=====")
print(vm.get_checkpoint_state())

vm.load_checkpoint_state(state)
print("======是不是老的？=====")
print(vm.get_checkpoint_state())
