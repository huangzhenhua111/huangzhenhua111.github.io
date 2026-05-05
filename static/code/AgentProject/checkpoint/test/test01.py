import sys
sys.path.insert(0, "/home/huangzhenhua/workspace/LearnAgent/checkpoint/MASFactory")
from masfactory import CustomNode,RootGraph,Node,Edge
# def forward1(message,attribute):
#     count=message["count"]
#     count+=1
#     return {"count":count}

# def forward2(message,attribute):
#     count=message["count"]
#     count+=1
#     return {"count":count}

# def hook_func(node, result, outer_env=None):
#     # print(f'{node.name}保存的信息:\n{node.get_checkpoint_state()}')
#     print(f'======{node.name}执行结束之后======')

#     print("入边:")
#     print(e_entry_n1.get_checkpoint_state())

#     print("中间那条边:")
#     print(e1.get_checkpoint_state())

#     print("出边:")
#     print(e_n2_exit.get_checkpoint_state())


# g=RootGraph("test01")
# n1=g.create_node(CustomNode,"n1",forward1,attributes={"x":1})
# n2=g.create_node(CustomNode,"n2",forward2)
# e1=g.create_edge(n1,n2,keys={"count":""})

# e_entry_n1 = g.edge_from_entry(n1,{"count":""})
# e_n2_exit = g.edge_to_exit(n2,{"count":""})
# g.build()

# # n1.hook_register(Node.Hook.EXECUTE.AFTER,hook_func)
# # n2.hook_register(Node.Hook.EXECUTE.AFTER,hook_func)
# g.hook_register(
#     Node.Hook.EXECUTE.AFTER,
#     hook_func,
#     recursion=True,
# )


# out,_=g.invoke({"count":0})
# print(f'count:{out["count"]}')

def forward(message,attributes):
    message["count"]=1
    return message
g=RootGraph("test01")
n1=g.create_node(CustomNode,"n1",forward,attributes={"x":1})
old_state=n1.get_checkpoint_state()
print("旧状态:")
print(old_state)
n1.attributes["x"]=999
print("changed:")
print(n1.get_checkpoint_state())
n1.load_checkpoint_state(old_state)
print("恢复后：")
print(n1.get_checkpoint_state())

n2=g.create_node(CustomNode,"n2",forward,attributes={"x":1})
e1=g.create_edge(n1,n2,keys={"count":""})
e_old_state=e1.get_checkpoint_state()
print("边的旧状态：")
print(e_old_state)
e1.send_message({"count":123})
print("边的新状态：")
print(e1.get_checkpoint_state())
e1.load_checkpoint_state(e_old_state)
print("恢复后的边状态：")
print(e1.get_checkpoint_state())