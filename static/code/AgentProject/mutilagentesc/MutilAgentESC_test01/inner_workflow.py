import os,re
from dotenv import load_dotenv
from masfactory import Agent, OpenAIModel, RootGraph, SimpleKeywordRetriever,NodeTemplate,CustomNode,LogicSwitch
from get_top_k import get_top_k
from three_agent_strategy_discussion import three_agent_strategy_discussion

load_dotenv()

model = OpenAIModel(
    api_key=os.getenv("OPENAI_API_KEY", ""),
    base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or None,
    model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
)

def is_complex(message,attributes):
    save=message.get("save")
    context=save["context"]
    g=RootGraph("is_complex")
    is_complex_Agent=g.create_node(Agent,"is_complex_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="请你阅读{context}判断用户当前对话是否已经体现了情感,原因和意图,如果是则严格输出字符串'yes',否则输出'no'")
    g.edge_from_entry(is_complex_Agent,{"context":""})
    g.edge_to_exit(is_complex_Agent,{"isComplex":""})
    g.build()
    out,_=g.invoke({"context":context})
    isComplex=out["isComplex"]
    print(f"isComplex:{isComplex}")
    if isComplex and isComplex.strip().lower() == "yes":
        return True
    else:
        return False

def vote(reflection_result):
    count={}
    strat2response = {}

    for result in reflection_result:
        try:
            response_part, _ = result.split("\nReasoning", 1)
            strategy, response = re.findall(
                r"Response:\s*\[([a-zA-Z ]+)\](.*)",
                response_part
            )[0]

            strategy = strategy.strip()
            response = response.strip()

            if strategy not in count:
                count[strategy] = 0
            count[strategy] += 1

            if strategy not in strat2response:
                strat2response[strategy] = response

        except Exception:
            continue
    
    if len(count)==0:
        return ["None"],["None"]

    max_count=max(count.values())
    max_strategy=[k for k,v in count.items() if v==max_count]
    responses=[strat2response[s] for s in max_strategy]
    return max_strategy,responses

def run_self_reflection(context, pred_strategy, ori_response):
    g = RootGraph("self_reflection")

    self_reflection_Agent = g.create_node(
        Agent,
        "self_reflection_Agent",
        model=model,
        instructions=(
            "你是经验丰富的心理治疗专家。"
            "你擅长检查另一个 supporter 对 seeker 的回复，"
            "并在必要时给出更合适的修改版本。"
        ),
        prompt_template=(
            "这是上下文：{context}\n\n"
            "这是当前选中的策略：{pred_strategy}\n\n"
            "这是当前候选回复：[{pred_strategy}] {ori_response}\n\n"
            "请你检查这条回复是否满足 3 个条件：\n"
            "1. 是否和当前对话一致\n"
            "2. 是否符合这个 strategy\n"
            "3. 是否真的有助于缓解用户情绪压力\n\n"
            "如果满足，就原样返回；"
            "如果不满足，就修改并给出 refined version。"
            "refined version 必须少于 30 个词。\n\n"
            "严格按下面格式输出：\n"
            "Response: [strategy] [response]\n"
            "Reasoning: [reasoning]"
        )
    )

    g.edge_from_entry(self_reflection_Agent, {
        "context": "",
        "pred_strategy": "",
        "ori_response": "",
    })
    g.edge_to_exit(self_reflection_Agent, {
        "reflection_text": "",
    })
    g.build()

    out, _ = g.invoke({
        "context": context,
        "pred_strategy": pred_strategy,
        "ori_response": ori_response,
    })

    reflection_text = out["reflection_text"]

    m = re.findall(
        r"Response:\s*\[([a-zA-Z ]+)\](.*?)(?:\nReasoning:|\Z)",
        reflection_text,
        flags=re.S
    )

    if m:
        _returned_strategy = m[0][0].strip()   # 源码里这个返回策略其实会被忽略
        refined_response = m[0][1].strip()
        return refined_response

    return reflection_text.strip()

def run_one_target_reply(message,attributes):
    save=message.get("save")
    context=save["context"]
    response=""
    if int(attributes.get("count",0))<5 or not is_complex(message,attributes):
        g=RootGraph("inner_group")
        Zero_Shot_Agent=g.create_node(Agent,"Zero_Shot_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="你扮演 Assistant,根据{context}生成 response")
        g.edge_from_entry(Zero_Shot_Agent,{"context":""})
        g.edge_to_exit(Zero_Shot_Agent,{"response":""})
        g.build()
        out,_=g.invoke({"context":context})
        response=out["response"]
        save["response"]=response
        return save
    else:
        g=RootGraph("inner_group")
        emotion_Agent=g.create_node(Agent,"emotion_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="请你阅读上下文：{context}，并输出用户当前情感状态")
        cause_Agent=g.create_node(Agent,"cause_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="请你阅读上下文：{context}和用户当前情感状态{emotion},并输出用户寻求帮助的原因")
        intention_Agent=g.create_node(Agent,"intention_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="请你阅读上下文：{context}，用户当前情感状态{emotion}和用户寻求帮助的原因{cause},并输出用户的意图")
        g.edge_from_entry(emotion_Agent,{"context":""})
        g.create_edge(emotion_Agent,cause_Agent,{"context":"","emotion":""})
        g.create_edge(cause_Agent,intention_Agent,{"context":"","emotion":"","cause":""})
        g.edge_to_exit(intention_Agent,{"context":"","emotion":"","cause":"","intention":""})
        g.build()
        out,_=g.invoke({"context":context})
        emotion=out["emotion"]
        cause=out["cause"]
        intention=out["intention"]
        save["emotion"]=emotion
        save["cause"]=cause
        save["intention"]=intention
        history=list(attributes.get("history"))
        if history[-1]["speaker"]=="seeker":
            post=history[-1]["text"]

        record_seeker_supporter = attributes.get("record_seeker_supporter")
        record_seeker = attributes.get("record_seeker")
        retriever= attributes.get("retriever")
        top_pairs=get_top_k(record_seeker_supporter,record_seeker,retriever,post)

        print("query post =", post)
        print("top_pairs =", top_pairs[:3])
        print("检索成功啦！！！！！！！！")

        example=""
        for e in top_pairs:
            example+=f'seeker:{e["example"]["seeker"]}\n[{e["example"]["strategy"]}] supporter:{e["example"]["supporter"]}\n\n'
        pred_strategy=three_agent_strategy_discussion(message,attributes,emotion,cause,intention,example)

        print(f"pred_strategy:{pred_strategy}")
        print("讨论出策略啦！！！！！！！！")

        

        if len(pred_strategy)==0:
            g=RootGraph("Zero_Shot_group")
            Zero_Shot_Agent=g.create_node(Agent,"Zero_Shot_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="这是上下文：{history}\n这是seeker的情绪:{emotion}\n原因:{cause}\n:意图{intention}\n你可以参考的例子:{example}\n请你对用户的话作出回应")
            g.edge_from_entry(Zero_Shot_Agent,{"context":"","emotion":"","cause":"","intention":"","example":""})
            g.edge_to_exit(Zero_Shot_Agent,{"response":""})
            g.build()
            out,_=g.invoke({"context":context,"emotion":emotion,"cause":cause,"intention":intention,"example":example})
            response=out["response"]
            save["response"]=response
            save["pred_strategy"] = "None"
            return save
        elif len(pred_strategy)==1:
            new_top_pairs=[]
            for e in top_pairs:
                if e["example"]["strategy"]==pred_strategy[0]:
                    s=f'seeker:{e["example"]["seeker"]}\n[{e["example"]["strategy"]}] supporter:{e["example"]["supporter"]}\n\n'
                    new_top_pairs.append(s)
            example="\n\n".join(new_top_pairs)        
            g=RootGraph("Zero_Shot_group")
            Zero_Shot_Agent=g.create_node(Agent,"Zero_Shot_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="这是上下文：{context}\n这是seeker的情绪:{emotion}\n原因:{cause}\n意图:{intention}\n策略:{pred_strategy[0]}\n你可以参考的例子:{example}\n请你对用户的话作出回应")
            g.edge_from_entry(Zero_Shot_Agent,{"context":"","emotion":"","cause":"","intention":"","pred_strategy[0]":"","example":""})
            g.edge_to_exit(Zero_Shot_Agent,{"response":""})
            g.build()
            out,_=g.invoke({"context":context,"emotion":emotion,"cause":cause,"intention":intention,"pred_strategy[0]":pred_strategy[0],"example":example})
    
            ori_response=out["response"]
            save["ori_response"]=ori_response
            save["pred_strategy"]=pred_strategy[0]

            
            g=RootGraph("self_reflection")
            self_reflection_Agent=g.create_node(Agent,"self_reflection_Agent",model=model,instructions="你是经验丰富的心理治疗专家,你擅长检查另一个supporter对seeker说的话并给出正确的修改",prompt_template="这是上下文：{context}\n策略:{pred_strategy[0]}\n上一个supporter的回复:{ori_response}\n请你检查这条回复是否满足 3 个条件:1.是否和当前对话一致 2.是否符合这个 strategy 3.是否真的有助于缓解用户情绪压力.如果满足，就原样返回；如果不满足，就修改并给出 refined version，而且还要求 refined version 少于 30 个词")
            g.edge_from_entry(self_reflection_Agent,{"context":"","pred_strategy[0]":"","ori_response":""})
            g.edge_to_exit(self_reflection_Agent,{"response":""})
            g.build()
            out,_=g.invoke({"context":context,"pred_strategy[0]":pred_strategy[0],"ori_response":ori_response})
            response=out["response"]
            save["response"]=response
            return save
        else:

            g=RootGraph("response_graph")
            response_Agent=g.create_node(Agent,"response_Agent",model=model,instructions="你是经验丰富的心理治疗专家",prompt_template="这是上下文：{context}\n这是seeker的情绪:{emotion}\n原因:{cause}\n意图:{intention}\n策略:{pred_strategy[0]}\n你可以参考的例子:{example}\n请你对用户的话作出回应")
            g.edge_from_entry(response_Agent,{"context":"","emotion":"","cause":"","intention":"","pred_strategy[0]":"","example":""})
            g.edge_to_exit(response_Agent,{"response":""})
            g.build()
            
            responses=[]
            debate_history=[]
            for strat in pred_strategy:
                example=""
                for e in top_pairs:
                    if e["example"]["strategy"]==strat:
                        example+=f'seeker:{e["example"]["seeker"]}\n[{e["example"]["strategy"]}] supporter:{e["example"]["supporter"]}\n\n'
                out,_=g.invoke({"context":context,"emotion":emotion,"cause":cause,"intention":intention,"pred_strategy[0]":strat,"example":example})
                response=out["response"]
                responses.append(f"[{strat}] {response}")

                g=RootGraph("debate")
                s_debate_history="\n".join(debate_history)
                debater_Agent=g.create_node(Agent,"debater_Agent",model=model,instructions="你是经验丰富的心理治疗专家,你擅于通过辩论来为seeker选一个最好的回复",prompt_template="这是上下文：{context}\n这是seeker的情绪:{emotion}\n原因:{cause}\n意图:{intention}\n你可以参考的例子:{example}\n在你前面的辩论对话:{s_debate_history}\n这是你倾向于支持的策略和回复:[{strategy}] {response}\n请你充分参考上述内容给出你的观点,格式是'我支持[{strategy}] {response},理由是....'")
                g.edge_from_entry(debater_Agent,{"context":"","emotion":"","cause":"","intention":"","example":"","s_debate_history":"","strategy":"","response":""})
                g.edge_to_exit(debater_Agent,{"opinion":""})
                g.build()
                out,_=g.invoke({"context":context,"emotion":emotion,"cause":cause,"intention":intention,"example":example,"s_debate_history":s_debate_history,"strategy":strat,"response":response})
                debate_history.append(out["opinion"])

            reflection_result=[]
            for i in range(len(pred_strategy)):
                strat=pred_strategy[i]
                response=responses[i]

                g=RootGraph("reflect")
                s_debate_history="\n".join(debate_history)
                reflect_Agent=g.create_node(Agent,"reflect_Agent",model=model,instructions="你是经验丰富的心理治疗专家,你擅于通过分析辩论历史来决定最终支持哪个回复",prompt_template="这是上下文：{context}\n这是seeker的情绪:{emotion}\n原因:{cause}\n意图:{intention}\n你可以参考的例子:{example}\n这是你原来支持的策略和回复:{response}\n请你现在充分参考{s_debate_history}，认真分析上面不同观点，并反思自己的看法。如果你认为别人更有道理，你可以改变立场。请最终选择你现在认为最合适的一条回复，并说明理由。严格按下面格式输出：Response: [strategy] [response]\nReasoning: [reasoning]")
                g.edge_from_entry(reflect_Agent,{"context":"","emotion":"","cause":"","intention":"","example":"","s_debate_history":"","strategy":"","response":""})
                g.edge_to_exit(reflect_Agent,{"reflection":""})
                g.build()
                out,_=g.invoke({"context":context,"emotion":emotion,"cause":cause,"intention":intention,"example":example,"s_debate_history":s_debate_history,"strategy":strat,"response":response})
                reflection_result.append(out["reflection"])

            max_strategy,responses=vote(reflection_result=reflection_result)

            if len(max_strategy)==1 and max_strategy[0]!="None":
                pred_strategy=max_strategy[0]
                response=responses[0]
            else:
                candidate_items = []
                for strat, resp in zip(max_strategy, responses):
                    candidate_items.append(f"[{strat}] {resp}")
                candidate_responses = "\n\n".join(candidate_items)

                g = RootGraph("judge")
                judge_Agent = g.create_node(
                    Agent,
                    "judge_Agent",
                    model=model,
                    instructions="你是经验丰富的心理治疗专家，你擅长在多个候选回复中选出最适合 seeker 的一个。",
                    prompt_template=(
                        "这是上下文：{context}\n\n"
                        "下面是不同策略生成的候选回复：\n{candidate_responses}\n\n"
                        "请你选出最合适的一条回复，并说明理由。\n"
                        "严格按下面格式输出：\n"
                        "Response: [strategy] [response]\n"
                        "Reasoning: [reasoning]"
                    )
                )

                g.edge_from_entry(judge_Agent, {
                    "context": "",
                    "candidate_responses": "",
                })
                g.edge_to_exit(judge_Agent, {
                    "judgement": "",
                })
                g.build()
                out, _ = g.invoke({
                    "context": context,
                    "candidate_responses": candidate_responses,
                })
                judge_text = out["judgement"]
                m = re.findall(r"Response:\s*\[([a-zA-Z ]+)\](.*)", judge_text)
                if m:
                    pred_strategy = m[0][0].strip()
                    response = m[0][1].strip()
                else:
                    pred_strategy, response = "None", "None"
                
                save["ori_response"] = response
                save["pred_strategy"] = pred_strategy
                response = run_self_reflection(
                    context=context,
                    pred_strategy=pred_strategy,
                    ori_response=response,
                )
     

            save["response"]=response 

            print("final_response =", save["response"])
            
            return save

    
        
