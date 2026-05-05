from masfactory import SimpleKeywordRetriever

retriever=SimpleKeywordRetriever({"doc1":"开门"})

state=retriever.get_checkpoint_state()
print("====老的====")
print(state)

retriever._documents["doc2"]="下去沉淀"
print("====新的====")
print(retriever.get_checkpoint_state())

retriever.load_checkpoint_state(state)
print("===是老的吗====")
print(retriever.get_checkpoint_state())