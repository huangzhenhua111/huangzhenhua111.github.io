"""
Main entry point for MultiAgentESC reproduction on MASFactory.
Aligned with source: main.py (lines ~156-285)
"""

import os
import json
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

from masfactory import OpenAIModel, SentenceTransformerEmbedder
from multiagentsc.workflow import create_workflow, process
from multiagentsc.utils import build_dataset, build_retriever


if __name__ == "__main__":
    # Load dataset
    dataset_path = os.path.join(PROJECT_ROOT, "dataset", "ESConv.json")
    with open(dataset_path, "r") as f:
        dataset = json.load(f)
    # Source: processes first 100 samples as test set
    samples = dataset[:3]  # TODO: 改为 [:100] 跑完整测试

    # Create MASFactory LLM model (same as driver.py)
    model = OpenAIModel(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        base_url=os.getenv("OPENAI_BASE_URL") or os.getenv("BASE_URL") or None,
        model_name=os.getenv("OPENAI_MODEL_NAME", "qwen2.5-32b-instruct"),
        invoke_settings={"temperature": 0.0},
    )

    # Build retrieval index from dataset[100:] (same as source get_quadruple)
    record_seeker_supporter, record_seeker = build_dataset(dataset_path, start_id=100)
    embedder = SentenceTransformerEmbedder(model_name="all-roberta-large-v1")
    embedding_fn = embedder.get_embedding_function()
    retriever = build_retriever(record_seeker, embedding_fn)

    # Create all workflow graphs and utility functions
    graphs, utils = create_workflow(model)

    # Process each sample — source: main.py main loop
    ret = []
    for sample in tqdm(samples, desc="Processing dialogs"):
        dialog = sample["dialog"]

        result = process(
            message={"dialog": dialog},
            attributes={
                "count": 0,
                "history": [],
                "ret": [],
                "record_seeker_supporter": record_seeker_supporter,
                "retriever": retriever,
            },
            model=model,
            graphs=graphs,
            utils=utils,
        )
        ret.extend(result["ret"])

    # Save results
    save_path = "results.json"
    with open(save_path, "w") as f:
        json.dump(ret, f, indent=4)
    print(f"Saved {len(ret)} results to {save_path}")
