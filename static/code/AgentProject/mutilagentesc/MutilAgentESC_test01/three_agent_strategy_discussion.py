import os
from dotenv import load_dotenv
from masfactory import Agent, OpenAIModel, RootGraph, SimpleKeywordRetriever,NodeTemplate,CustomNode,LogicSwitch

load_dotenv()

model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or None,
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
)

g=RootGraph("three_agent_strategy_discussion")
Agent1=g.create_node(Agent,"Agent1",model=model,instructions="你擅长根据我给你的信息选择心理治疗的策略",prompt_template="这是上下文：{history}\n这是seeker的情绪:{emotion}\n原因:{cause}\n:意图{intention}\n你可以参考的例子:{example}\n请你从8种策略(Question,Restatement or Paraphrasing,Reflection of feelings,Self-disclosure,Affirmation and Reassurance,Providing Suggestions,Information,Others)中选择一种原样输出")
Agent2=g.create_node(Agent,"Agent2",model=model,instructions="你擅长根据我给你的信息选择心理治疗的策略",prompt_template="这是上下文：{history}\n这是seeker的情绪:{emotion}\n原因:{cause}\n:意图{intention}\n你可以参考的例子:{example}\n请你从8种策略(Question,Restatement or Paraphrasing,Reflection of feelings,Self-disclosure,Affirmation and Reassurance,Providing Suggestions,Information,Others)中选择一种原样输出")
Agent3=g.create_node(Agent,"Agent3",model=model,instructions="你擅长根据我给你的信息选择心理治疗的策略",prompt_template="这是上下文：{history}\n这是seeker的情绪:{emotion}\n原因:{cause}\n:意图{intention}\n你可以参考的例子:{example}\n请你从8种策略(Question,Restatement or Paraphrasing,Reflection of feelings,Self-disclosure,Affirmation and Reassurance,Providing Suggestions,Information,Others)中选择一种原样输出")
g.edge_from_entry(Agent1,{"history":"","emotion":"","cause":"","intention":"","example":""})
g.edge_from_entry(Agent2,{"history":"","emotion":"","cause":"","intention":"","example":""})
g.edge_from_entry(Agent3,{"history":"","emotion":"","cause":"","intention":"","example":""})
g.edge_to_exit(Agent1,{"strategy":""})
g.edge_to_exit(Agent2,{"strategy":""})
g.edge_to_exit(Agent3,{"strategy":""})
g.build()

def three_agent_strategy_discussion(message,attributes,emotion,cause,intention,example):
    history=list(attributes.get("history"))
    out,_=g.invoke({"history":history,"emotion":emotion,"cause":cause,"intention":intention,"example":example})
    pred_strategy=out["strategy"]
    return list(set(pred_strategy))  
   




