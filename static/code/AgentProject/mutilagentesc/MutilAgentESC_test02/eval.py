"""
评估脚本：对齐论文 MultiAgentESC (EMNLP 2025) Table 1 的7个指标
D-1, D-2: Distinct-1/2（多样性）
B-1, B-2, B-3: BLEU-1/2/3（n-gram 相似度）
F1: BERTScore F1（语义相似度）
R-L: ROUGE-L（最长公共子序列）

源码 Qwen2.5-32b 的 MultiAgentESC 结果：
  D-1=6.78, D-2=35.15, B-1=17.66, B-2=5.38, B-3=2.35, F1=18.30, R-L=14.66
"""
import json
import os
import re
from collections import Counter

import nltk
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt", quiet=True)
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)

from nltk.util import ngrams as _ngrams
from nltk.translate.bleu_score import corpus_bleu
from rouge_score import rouge_scorer
from bert_score import score as bert_score


# ============ Ground Truth 对齐 ============

def load_gt(dataset_path="dataset/ESConv.json", n_samples=100):
    """从 ESConv.json 提取 ground truth reference，按出现顺序对齐 results.json"""
    with open(dataset_path) as f:
        dataset = json.load(f)

    gt_references = []
    for sample in dataset[:n_samples]:
        dialog = sample["dialog"]
        count = 0
        history = []
        while count < len(dialog):
            if count != 0 and dialog[count]["speaker"] == "supporter":
                is_single = (count < len(dialog) - 1 and dialog[count + 1]["speaker"] != "supporter") or (count == len(dialog) - 1)
                gt_references.append(dialog[count]["content"].strip())
                history.append({"content": dialog[count]["content"].strip(), "role": "assistant"})
                count += 1 if is_single else 2
            else:
                history.append({
                    "content": dialog[count]["content"].strip(),
                    "role": "user" if dialog[count]["speaker"] == "seeker" else "assistant"
                })
                count += 1
    return gt_references


def load_results(path="results.json"):
    with open(path) as f:
        return json.load(f)


def clean_response(resp):
    """清理 response：去掉 Reasoning 残留、"Refined response:" 等"""
    if not resp or resp == "None":
        return ""
    # 去掉 Reasoning 部分
    if "Reasoning:" in resp:
        resp = resp.split("Reasoning:")[0].strip()
    # 去掉 Refined response: 前缀
    for prefix in ["Refined response:", "refined response:",
                   "Original response:", "original response:"]:
        if resp.startswith(prefix):
            resp = resp[len(prefix):].strip()
    return resp.strip()


# ============ 指标计算 ============

def compute_distinct(preds):
    """Distinct-1 / Distinct-2：多样性指标"""
    if not preds:
        return 0.0, 0.0
    unigrams, bigrams = [], []
    for p in preds:
        tokens = p.split()
        unigrams.extend(tokens)
        bigrams.extend(_ngrams(tokens, 2))
    d1 = len(set(unigrams)) / max(len(unigrams), 1) * 100
    d2 = len(set(bigrams)) / max(len(bigrams), 1) * 100
    return d1, d2


def compute_bleu(preds_list, refs_list):
    """BLEU-1/2/3：corpus-level BLEU"""
    # refs_list: list of reference strings
    # preds_list: list of candidate strings
    hyps = [p.split() for p in preds_list]
    refs = [[r.split()] for r in refs_list]

    scores = {}
    for n in [1, 2, 3]:
        try:
            scores[f"B-{n}"] = corpus_bleu(refs, hyps, weights=tuple(1.0 / n for _ in range(n))) * 100
        except Exception:
            scores[f"B-{n}"] = 0.0
    return scores


def compute_rouge_l(preds_list, refs_list):
    """ROUGE-L"""
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    scores = []
    for pred, ref in zip(preds_list, refs_list):
        s = scorer.score(ref, pred)
        scores.append(s["rougeL"].fmeasure * 100)
    return sum(scores) / max(len(scores), 1)


def compute_bert_score(preds_list, refs_list, model_name="microsoft/deberta-xlarge-mnli"):
    """BERTScore F1 — 需要下载模型，失败则跳过"""
    try:
        _, _, f1 = bert_score(preds_list, refs_list, model_type=model_name, lang="en", rescale_with_baseline=True)
        return float(f1.mean()) * 100
    except Exception as e:
        print(f"  [BERTScore 失败: {e}]")
        return None


# ============ 主评估 ============

def evaluate(n_samples=None):
    # 加载
    results = load_results()
    gt_refs = load_gt(n_samples=n_samples or len(results))
    n = min(len(results), len(gt_refs))

    print(f"对齐样本数: {n} (results={len(results)}, gt={len(gt_refs)})")
    print()

    # 清理 responses
    preds = [clean_response(r.get("response", "")) for r in results[:n]]
    refs = [r for r in gt_refs[:n]]

    # 过滤空 response（BLEU/ROUGE 需要有效文本）
    valid_idx = [i for i, p in enumerate(preds) if p]
    valid_preds = [preds[i] for i in valid_idx]
    valid_refs = [refs[i] for i in valid_idx]
    print(f"有效响应: {len(valid_preds)}/{n}")

    # 1. Distinct
    d1, d2 = compute_distinct(valid_preds)
    print(f"\n[Distinct-1]  {d1:.2f}  (源码 Qwen 6.78)")
    print(f"[Distinct-2]  {d2:.2f}  (源码 Qwen 35.15)")

    # 2. BLEU
    bleu_scores = compute_bleu(valid_preds, valid_refs)
    print(f"\n[BLEU-1]     {bleu_scores['B-1']:.2f}  (源码 Qwen 17.66)")
    print(f"[BLEU-2]     {bleu_scores['B-2']:.2f}  (源码 Qwen 5.38)")
    print(f"[BLEU-3]     {bleu_scores['B-3']:.2f}  (源码 Qwen 2.35)")

    # 3. ROUGE-L
    rl = compute_rouge_l(valid_preds, valid_refs)
    print(f"\n[ROUGE-L]    {rl:.2f}  (源码 Qwen 14.66)")

    # # 4. BERTScore F1
    # print(f"\n[BERTScore F1] ", end="")
    # bf1 = compute_bert_score(valid_preds, valid_refs)
    # if bf1 is not None:
    #     print(f"{bf1:.2f}  (源码 Qwen 18.30)")
    # else:
    #     print("失败（需网络下载模型，可忽略）")

    # 5. 策略分布对比
    print("\n--- 策略分布 ---")
    from collections import Counter
    pred_strats = Counter(r.get("pred_strategy", "None") for r in results[:n])

    # GT strategy: extract from same dialogs using same logic as workflow
    _ds_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "ESConv.json")
    with open(_ds_path) as f:
        dataset = json.load(f)
    gt_strats_for_n = []
    _count = 0
    for sample in dataset:
        dialog = sample["dialog"]
        c = 0
        while c < len(dialog):
            if c != 0 and dialog[c]["speaker"] == "supporter":
                is_single = (c < len(dialog) - 1 and dialog[c + 1]["speaker"] != "supporter") or (c == len(dialog) - 1)
                gt_strats_for_n.append(dialog[c]["annotation"]["strategy"])
                c += 1 if is_single else 2
                _count += 1
                if _count >= n:
                    break
            else:
                c += 1
        if _count >= n:
            break

    print(f"{'策略':<30} {'预测':>6} {'GT':>6}")
    gt_counter = Counter(gt_strats_for_n)
    all_strats = set(list(pred_strats.keys()) + list(gt_counter.keys()))
    for s in sorted(all_strats, key=lambda x: pred_strats.get(x, 0), reverse=True):
        print(f"  {s:<28} {pred_strats.get(s, 0):>6} {gt_counter.get(s, 0):>6}")

    print("\n注: 源码 Qwen2.5-32b 性能:")
    print("  D-1=6.78, D-2=35.15, B-1=17.66, B-2=5.38, B-3=2.35, F1=18.30, R-L=14.66")


if __name__ == "__main__":
    evaluate()
