import json
from masfactory import (
    RootGraph,                   # 最外层图
    CustomNode,                  # 自定义 Python 节点
    NodeTemplate,                # 节点模板
    Shared,                      # 共享大对象，避免被模板重复拷贝
    VectorRetriever,             # 向量检索器
    SentenceTransformerEmbedder, # sentence-transformers 的封装
)
from masfactory.adapters.context.types import ContextQuery

def build_dateset(dataset_path,start_id=100):
    with open(dataset_path,"r",encoding="UTF-8") as f:
        dataset=json.load(f)

    record_seeker_supporter={}
    record_seeker={}
    for id in range(start_id,min(start_id+100,len(dataset))):#后面再改回len(dataset)；弱的：min(start_id+100,len(dataset))
        dialog=dataset[id]["dialog"]
        for turn in range(len(dialog)-1):
            if dialog[turn]["speaker"]=="seeker" and dialog[turn+1]["speaker"]=="supporter":
                doc_id=f"s{id}_t{turn}"
                record_seeker_supporter[doc_id]={"seeker":dialog[turn]["content"],"supporter":dialog[turn+1]["content"],"strategy":dialog[turn+1]["annotation"]["strategy"]}
                record_seeker[doc_id]=dialog[turn]["content"]
    return record_seeker_supporter,record_seeker

def get_top_k(record_seeker_supporter,record_seeker,retriever,post):
    blocks=retriever.get_blocks(ContextQuery(query_text=post),top_k=3)#后面再改回top_k=10
    top_pairs=[]
    for block in blocks:
        doc_id=block.metadata["doc_id"]
        top_pairs.append({"doc_id":doc_id,"example":record_seeker_supporter[doc_id]})
    return top_pairs
        
