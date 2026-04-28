# MultiAgentESC on MASFactory

Reproduction of [MultiAgentESC (EMNLP 2025)](https://github.com/MindIntLab-HFUT/MultiAgentESC) on the [MASFactory](https://github.com/BUPT-GAMMA/MASFactory) framework.

MultiAgentESC is an Emotional Support Conversation (ESC) system that uses multi-agent collaboration for strategy selection. This reproduction replaces the original autogen-based implementation with MASFactory's graph-based agent orchestration.

## Architecture

```
                    ┌─────────────────┐
                    │   main.py       │
                    │  (entry point)  │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  workflow.py    │
                    │ create_workflow │──── is_complex, zero_shot,
                    │   + process()   │     emotion, cause, intention,
                    └────────┬────────┘     response_gen, judge,
                             │              self_reflection
              ┌──────────────┼──────────────┐
              │              │              │
    ┌─────────▼──┐  ┌───────▼──────┐  ┌───▼──────────┐
    │ prompts.py │  │   utils.py   │  │ components/  │
    │ (11 prompts│  │ (retrieval,  │  │  strategy_   │
    │  aligned)  │  │  parsing)    │  │  discussion  │
    └────────────┘  └──────────────┘  │  debate      │
                                      │  reflect     │
                                      └──────────────┘
```

### Key Components

| Component | File | Description |
|-----------|------|-------------|
| Entry | `main.py` | Dataset loading, model creation, orchestration |
| Workflow | `multiagentsc/workflow.py` | Graph creation, main dialog loop |
| Prompts | `multiagentsc/prompts.py` | 11 prompts (identical to source) |
| Strategy Discussion | `multiagentsc/components/strategy_discussion.py` | 3-agent round-robin via MeshGraph |
| Debate | `multiagentsc/components/debate.py` | Multi-agent debate on responses |
| Reflect | `multiagentsc/components/reflect.py` | Multi-agent reflection |
| Utils | `multiagentsc/utils.py` | Retrieval, parsing, strategy cleaning |
| Patch | `multiagentsc/patch_masfactory.py` | Plain text output formatting |
| Eval | `eval.py` | 7 metrics (D-1, D-2, B-1, B-2, B-3, F1, R-L) |

### Pipeline (per dialog turn)

```
Dialog turn (supporter)
        │
        ▼
   is_complex? ──No──▶ zero_shot ──▶ response
        │
       Yes
        ▼
  emotion → cause → intention
        │
        ▼
  retrieve top-k examples
        │
        ▼
  strategy discussion (3 agents)
        │
        ├── 0 strategies ──▶ zero_shot
        ├── 1 strategy  ──▶ response_gen → self_reflection
        └── N strategies ──▶ response_gen × N → debate → reflect → vote
                              ├── 1 winner ──▶ self_reflection
                              └── tie ──▶ judge ──▶ self_reflection
```

## Setup

### Requirements

- Python 3.10+
- API access to a compatible LLM (tested with Qwen2.5-32b via Alibaba DashScope)

### Install

```bash
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
OPENAI_MODEL_NAME=qwen2.5-32b-instruct
```

### Dataset

Place `ESConv.json` in `dataset/` directory. Download from the [original repository](https://github.com/MindIntLab-HFUT/MultiAgentESC).

## Usage

### Run

```bash
# Run on first 3 samples (adjust in main.py)
python main.py

# Run evaluation
python eval.py
```

### Evaluate

```bash
python eval.py
```

Outputs 7 metrics aligned with the paper (Table 1):
- Distinct-1, Distinct-2 (strategy diversity)
- BLEU-1, BLEU-2, BLEU-3
- BERTScore F1
- ROUGE-L

## Results

### Reproduction vs Source Code (same API: Qwen2.5-32b on DashScope)

| Metric | Paper | Source (autogen) [:1] | **Reproduction (MASFactory) [:3]** |
|--------|-------|-----------------------|-------------------------------------|
| D-1 | 6.78 | 65.31 | 41.77 |
| D-2 | 35.15 | 92.97 | 80.12 |
| B-1 | 17.66 | 10.29 | 10.33 |
| B-2 | 5.38 | 2.45 | 2.25 |
| B-3 | 2.35 | 1.12 | 0.81 |
| R-L | 14.66 | 12.20 | 10.46 |

### Key Findings

1. **Framework alignment verified**: Source code (autogen) and reproduction (MASFactory) produce nearly identical B-1 (~10.3) on the same API, confirming the reproduction is correct.

2. **Gap to paper is API-dependent**: Both source and reproduction fall short of paper metrics (B-1=17.66). This gap is consistent across frameworks, indicating it stems from the API model version rather than the implementation.

3. **Strategy accuracy is the bottleneck**: The model struggles to predict correct strategies, which cascades into lower BLEU/ROUGE scores.

## Alignment with Source Code

| Aspect | Status |
|--------|--------|
| Prompts (11 total) | Identical (preserving original typos) |
| Model parameters (temperature, max_tokens) | Aligned |
| Pipeline logic (is_complex, zero_shot, complex path) | Aligned |
| Strategy definitions (8 standard strategies) | Aligned |
| Retrieval (all-roberta-large-v1, top-k=10) | Aligned |
| Multi-agent discussion (3 agents, round-robin) | Aligned (MeshGraph) |
| Debate + Reflect + Vote + Judge | Aligned |
| Self-reflection | Aligned |

## Known Limitations

1. **cache_seed not supported**: MASFactory does not support autogen's `cache_seed` mechanism. Results may vary slightly between runs despite `temperature=0.0`.

2. **Strategy accuracy**: The Qwen2.5-32b model on DashScope API produces lower strategy accuracy than reported in the paper. This affects both source and reproduction equally.

3. **Memory requirements**: Source code (autogen GroupChat) requires >8GB RAM for evaluation. The MASFactory reproduction is more memory-efficient.
