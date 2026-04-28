import os
import json
from outer_process import process
from get_top_k import build_dateset
from dotenv import load_dotenv
from masfactory import Agent, OpenAIModel, RootGraph, SimpleKeywordRetriever,NodeTemplate,CustomNode,LogicSwitch,VectorRetriever,SentenceTransformerEmbedder
load_dotenv()
model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or None,
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
)

record_seeker_supporter, record_seeker=build_dateset(dataset_path=os.path.expanduser("~/workspace/Internship/AgentProject/MutilAgentESC_test01/dataset/ESConv.json"))
embedder=SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")#之后换成all-roberta-large-v1;弱的：all-MiniLM-L6-v2
embedding_fn=embedder.get_embedding_function()
retriever=VectorRetriever(documents=record_seeker,embedding_function=embedding_fn,similarity_threshold=-1,context_label="MutilAgentESC")

g=RootGraph("sb",attributes={"count":0,"history":[],"save":{},"ret":[],"reference":[],"record_seeker_supporter":record_seeker_supporter,"record_seeker":record_seeker,"retriever":retriever})
processer=g.create_node(CustomNode,
                        name="process",
                        forward=process,
                        pull_keys={"history":"","ret":"","count":"","record_seeker_supporter": "","record_seeker": "","retriever":""},
                        push_keys={"history":"","ret":"","count":""},
                        )
g.edge_from_entry(processer,{"dialog":""})
g.edge_to_exit(processer,{"count":""})

g.build()

dialog = [
    {
        "speaker": "seeker",
        "text": "Lately I have been feeling trapped and exhausted because everything in my life seems to be piling up at once."
    },
    {
        "speaker": "supporter",
        "text": "That sounds really heavy. Can you tell me a little more about what has been happening?"
    },
    {
        "speaker": "seeker",
        "text": "My workload has increased a lot, and at the same time I am trying to take care of my family, so I feel like I never get a break."
    },
    {
        "speaker": "supporter",
        "text": "I can see why that would make you feel overwhelmed."
    },
    {
        "speaker": "seeker",
        "text": "What scares me most is that no matter which responsibility I focus on, I feel guilty for neglecting the others."
    },
    {
        "speaker": "seeker",
        "text": "I keep thinking that if I slow down at work I might fall behind, but if I keep pushing like this I am going to burn out completely."
    },
    {
        "speaker": "supporter",
        "text": "It sounds like you are stuck between pressure, guilt, and fear of burnout."
    },
    {
        "speaker": "supporter",
        "text": "Would it help to think together about one small change that could reduce some of this pressure today?"
    },
]

out,attrs=g.invoke({"dialog":dialog})

print("count =", attrs["count"])

print("\nhistory =")
print(json.dumps(attrs["history"], ensure_ascii=False, indent=2))

print("\nret =")
print(json.dumps(attrs["ret"], ensure_ascii=False, indent=2))