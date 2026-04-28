from inner_workflow import run_one_target_reply

def history_to_text(history):
    parts = []
    for x in history:
        if x["speaker"] == "seeker":
            parts.append(f"User: {x['text'].strip()}")
        else:
            parts.append(f"Assistant: {x['text'].strip()}")
    return " ".join(parts)

def process(message,attributes):
    
    count=int(attributes.get("count",0))
    history=list(attributes.get("history",[]))
    ret=list(attributes.get("ret",[]))
    dialog=list(message.get("dialog",[]))
    record_seeker_supporter = attributes.get("record_seeker_supporter")
    record_seeker = attributes.get("record_seeker")
    retriever=attributes.get("retriever")
    while count < len(dialog):
        if dialog[count]["speaker"]=="supporter" and count+1<len(dialog) and dialog[count+1]["speaker"]=="supporter" and count!=0:
            save={}
            reference=dialog[count]["text"]+" "+dialog[count+1]["text"]

            save["context"]=history_to_text(history)
            save["reference"]=str(reference)
            save=run_one_target_reply({"save":save},{"count":count,"history":history,"record_seeker_supporter": record_seeker_supporter,"record_seeker": record_seeker,"retriever":retriever})
            ret.append(save)
            history.append(dialog[count])
            history.append(dialog[count+1])
            count+=2
        elif dialog[count]["speaker"]=="supporter" and count!=0:
            save={}
            reference=dialog[count]["text"]

            save["context"]=history_to_text(history)
            save["reference"]=str(reference)
            save=run_one_target_reply({"save":save},{"count":count,"history":history,"record_seeker_supporter": record_seeker_supporter,"record_seeker": record_seeker,"retriever":retriever})
            ret.append(save)
            history.append(dialog[count])
            count+=1
        else:
            history.append(dialog[count])
            count+=1
    return {"history":history,"ret":ret,"count":count}