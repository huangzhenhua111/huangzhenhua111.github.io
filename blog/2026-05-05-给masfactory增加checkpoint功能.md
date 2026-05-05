# 项目目标：给masfactory增加checkpoint功能

## 项目背景：

进科研主线了

## 项目状态：

第一版已提交pr

## Quick Start

#### 这里说明用法，完整示例见:
huangzhenhua111.github.io/static/code/AgentProject/checkpoint/test/test17_run.py和test17_resume.py

### 第一次跑代码用的文件：
```
from masfactory.checkpoint.manager import CheckpointManager
from masfactory.checkpoint.storage import FileCheckpointStorage
from pathlib import Path

你的图代码

g.build()

*这三行是第一次run的时候保存用的：
storage=FileCheckpointStorage(str(Path(__file__).parent))
manager=CheckpointManager(g,storage)
manager.attach_hooks()

out,_=g.invoke({"count":0})
```

### 断点续跑用的文件：
```
from masfactory.checkpoint.manager import CheckpointManager
from masfactory.checkpoint.storage import FileCheckpointStorage
from pathlib import Path

你的图代码

g.build()

*这五行是接着上次保存的checkpoint文件状态接着跑，同时也会继续保存，第二次还断了可以接着用这些代码
storage=FileCheckpointStorage(str(Path(__file__).parent))
manager=CheckpointManager(g,storage)
manager.attach_hooks()
manager.load_last()
out,_=manager.resume()
```


## 实现

### 思路：

1.每个类都能保存和恢复自己的状态
2.能收集，保存和恢复整张图的状态
3.能从最近保存的状态中resume


### 详细实现过程：

1.写Checkpointable类

    a.因为每一个类都要实现get和load这两个操作
    b.于是把这两操作抽象成统一接口Checkpointable类
    c.强制每个类必须实现这俩抽象方法


2.先对Node和Edge继承并实现Checkpointable类

    a.实现get和load两个抽象函数
    b.对照Node和Edge类看需要保存和恢复哪些信息
    

3.写一个test01.py测试

    a.测Node和Edge的get和load
    b.对node就挂执行结束的勾子
    c.对edge就send静态检测


4.写storage.py

    a.这个是存储层
    b.定义一个FileCheckpointStorage类用来读写文件
    c.把断点保存到本地json文件


5.写test02测试

    a.测我的storage能不能正常读写文件


6.写test03测试

    a.把2和4联合起来测一下
    b.测我的node.get->storage.save->storage.load->node.load全链路有没有问题


7.写collector.py
    
    a.第一版先只收集root_graph和第一层的nodes,edges


8.写test04测试

    a.4,7联合起来测一下，每个节点执行完后保存一个文件


9.写storage.py

    a.先按collector的逆过程来写
    b.后面再改成严格版


10.写test05测试

    a.4,9联合起来测
    b.用存储层的load把state捞上来
    c.再用恢复层恢复


11.写manager.py

    a.让一个manager管理一个图
    b.用户自己给存储层
    c.写保存函数，挂勾子

12.写test06测试

    a.用manager实现保存和恢复


13.给manager.py补充resume方法

    a.参考graph的_forward


14.写test07测试


15.给memory.py加get和load方法


16.写test08测HistoryMemory


17.写test09测VectorMemory


18.给retrieval写get和load


19.写test10测SimpleKeywordRetriever


20.写test11测VectorRetriever


21.在collector和restorer的文件里补新加的memory和检索

    a.先只对agent补这两个，因为这两个主要是agent用
    b.顺手加上对CustomNode的支持


22.写test12测memory和retriever的收集和恢复

    a.先用假模型
    b.单独测这两个的collector和restore
    c.这一步是最小测试，下一步接完整链路

23.写test13测完整链路

    a.manager到真agent的最小链路已经通了
    b.这个是手动改，图没跑起来

24.写test14模拟完整真实场景

    a.故意把agent2的api_key写错
    b.到这里已经是最小闭环啦！！！
    c.后面还需要 
        Ⅰ.补FileSystemRetriever和各种子类的get,load方法
        Ⅱ.把命名变严格
    d.这一步发现了一个bug：(想要验证这个问题可以跑我的test_openai.py)
        原文本：
            {"role": "assistant", "content": "{\"count\": \"1\"}"}
        经过OpenAIModel转换后：
            {
                "role": "assistant",
                "content": [
                    {"type": "input_text", "text": "{\"count\": \"1\"}"}
                ]
            }
        openai对上下文的预期输入是 user对input_text ；assistant对output_text
        但是openai看到 assistant对上的是input_text ，直接报错
    

25.给manager加自动找最新断点文件加载的方法

    a.给storage加get最新断点文件路径的方法
    b.把这个路径喂进原来的load里，套壳命名成新方法


26.写test15

    a.复制一份test14_resume
    b.替换掉手动加载文件路径


27.给FileSystemRetriever补get和load方法


28.写test16测FileSystemRetriever


29.完善collector对图结构的递归收集

    a.之前写的collector只是收集第一层也就是根节点的图，节点，边，工具
    b.对restorer相应完善


30.写test17测完整闭环
    
    a.测完就可以准备pr了


31.补resume

    a.测test17的时候发现正常保存了但是没有正常resume
    b.原来是之前的resume只跑了第一层的
    c.得改成递归版

32.再跑test17

    a.测试通过了
    b.让codex再跑一些其他测试
    c.ok都过了，开始提pr