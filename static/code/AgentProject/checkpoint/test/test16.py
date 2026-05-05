from pathlib import Path
from tempfile import TemporaryDirectory
from masfactory import FileSystemRetriever
import numpy as np

def fake_embedding(text: str):
    return np.array([
        float(len(text)),
        float(text.count("苹果")),
        float(text.count("香蕉")),
    ])

with TemporaryDirectory() as tmp:
    docs_dir = Path(tmp) / "docs"
    docs_dir.mkdir()
    (docs_dir / "doc1.txt").write_text("我喜欢吃苹果和香蕉")
    (docs_dir / "doc2.txt").write_text("我喜欢吃苹果")
    retriever=FileSystemRetriever(str(docs_dir),fake_embedding)
    state=retriever.get_checkpoint_state()
    print("=======老的========")
    print(state)
    retriever._documents["doc3.txt"]="东西是新的"
    retriever._doc_embeddings["doc3.txt"]=np.array([666,666,666])
    retriever._similarity_threshold=999
    print("========新的=======")
    print(retriever.get_checkpoint_state())
    retriever.load_checkpoint_state(state)
    print("=========恢复了吗？=======")
    print(retriever.get_checkpoint_state())


