from masfactory import VectorRetriever
import numpy as np
def fake_embedding(text: str):
    return np.array([len(text), 1.0, 2.0])
retriever=VectorRetriever({"doc1":"开门"},fake_embedding)

state=retriever.get_checkpoint_state()
print("====老的====")
print(state)

retriever._documents["doc2"]="下去沉淀"
print("====新的====")
print(retriever.get_checkpoint_state())

retriever.load_checkpoint_state(state)
print("===是老的吗====")
print(retriever.get_checkpoint_state())