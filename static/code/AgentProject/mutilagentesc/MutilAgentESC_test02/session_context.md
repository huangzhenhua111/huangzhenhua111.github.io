---
name: full session context
description: Complete project context for MultiAgentESC reproduction. Read this to restore full memory.
type: project
---

## 项目概况

实习生将 MultiAgentESC (EMNLP 2025) 复现到 MASFactory 框架。
- 源码仓库: https://github.com/MindIntLab-HFUT/MultiAgentESC
- MASFactory 仓库: https://github.com/BUPT-GAMMA/MASFactory
- 用户 GitHub: huangzhenhua111
- PR 已提交: https://github.com/BUPT-GAMMA/MASFactory/pull/13

## 项目状态：PR 已提交到官方仓库

### PR 文件（13个）
路径: `MASFactory/applications/multiagentesc/`
```
main.py                    # 入口
workflow.py                # 图创建 + 对话处理循环
prompts.py                 # 11 个 prompt 模板（英文原文，含源码拼写错误）
strategy.py                # 8 种策略定义
utils.py                   # 检索、解析、策略清洗
patch_masfactory.py        # 纯文本输出格式化（去掉 MASFactory 的 JSON 包裹）
eval.py                    # 评估脚本（7个指标）
README.md                  # 项目说明 + 结果对比表
components/
    strategy_discussion.py # 3-agent 策略讨论 (MeshGraph round-robin)
    debate.py              # 多 agent 辩论
    reflect.py             # 多 agent 反思
```

### 开发目录（不在 PR 中）
路径: `MutilAgentESC_test02/`（当前工作目录）
- `multiagentsc/` — 开发版代码（PR 文件从此清理而来）
- `main.py`, `eval.py` — 开发版入口和评估
- `dataset/ESConv.json` — 数据集
- `results.json` — 最新运行结果
- `source_results.json` — 源码基线结果（[:1]）
- `source_eval_report.md` — 源码 vs 复现版对比报告
- `run_source_baseline.py` — 源码基线脚本（autogen，OOM 限制只能 [:1]）
- `MultiAgentESC_source/` — 源码备份
- `embeddings.txt` — 预计算的检索 embedding

## 技术细节

### 环境配置
- LLM: qwen2.5-32b-instruct（阿里云 DashScope API）
- Embedding: all-roberta-large-v1
- 本地内存: 7.4GB（跑源码基线只能 [:1]，OOM exit 137）
- `.env`: OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL_NAME

### Pipeline 流程
1. is_complex 判断 → 不复杂走 zero-shot
2. 复杂路径: emotion → cause → intention 分析
3. 检索 top-k 相似案例（all-roberta-large-v1 embedding）
4. 3-agent 策略讨论（MeshGraph round-robin）
5. 单策略 → 直接生成；多策略 → debate → reflect → vote → judge
6. self_reflection 最终质量检查

### 8种标准策略
Question, Restatement or Paraphrasing, Reflection of feelings, Self-disclosure,
Affirmation and Reassurance, Providing Suggestions, Information, Others

### 模型参数
- temperature=0.0 全局
- max_tokens=100: is_complex, zero_shot, response_gen
- max_tokens=400: emotion, cause, intention, judge, self_reflection, strategy discussion, debate, reflect

## 评估结果

### 最终结果（is_complex 修复后，[:3]=54turns）
| 指标 | 论文 | 源码(autogen)[:1] | 复现版(MASFactory)[:3] |
|------|------|-------------------|------------------------|
| D-1  | 6.78 | 65.31             | 41.77                  |
| D-2  | 35.15| 92.97             | 80.12                  |
| B-1  | 17.66| 10.29             | 10.33                  |
| B-2  | 5.38 | 2.45              | 2.25                   |
| B-3  | 2.35 | 1.12              | 0.81                   |
| R-L  | 14.66| 12.20             | 10.46                  |

### 核心结论
1. 复现版 B-1=10.33 ≈ 源码 B-1=10.29 → 框架对齐正确
2. 两者都远低于论文 17.66 → 差距来自 API 模型版本，非代码问题
3. 论文数据在当前 DashScope API 上无法复现

### 策略分布（复现版 [:3]）
- None=18, AR=16, Reflection of feelings=7, Others=4
- 源码 [:1] 也出现 6/11 None（is_complex 判断很多对话不够复杂）

## 已完成的对齐/修复

1. **11个 prompt 完全一致** — 保留源码拼写错误（如 "differnet", "explaination"）
2. **is_complex 恢复** — 之前因 gpt-4o-mini 总返回 NO 而禁用，现在用 qwen2.5-32b 正常工作
3. **Counter fallback** — 策略讨论正则失败时从 examples Counter 投票（减少 None）
4. **clean_strategy 过滤** — vote/judge 后过滤无效策略名（如 "Combined Approach"）
5. **self_reflection wrapper** — 多层 fallback 解析，去掉 "Reasoning:" 残留
6. **parse_single_response** — gpt-4o-mini 不输出 "Response:" 时用原始文本
7. **patch_masfactory** — 去掉 MASFactory 的 "MESSAGE TO YOU" 包裹和 JSON 格式要求

## 待做

1. **上服务器跑 [:10] 或 [:100]** — 本地 7.4GB 内存不够，需要租阿里云 ECS（4核16GB，约1元/小时）
2. **跑源码基线 [:3] 以上** — 用 autogen 跑更大样本量，证明源码性能也一样
3. **等 PR review** — https://github.com/BUPT-GAMMA/MASFactory/pull/13
4. **考虑跑完整 100 样本评估** — main.py 里改成 dataset[:100]

## 用户偏好
- 不喜欢被问问题，直接做
- 要求简洁直接
- 严格对照源码，不能猜
- prompt 必须英文原文一字不差
- 不想在小细节上继续折腾，准备提交了

## MASFactory 关键技术点
- RootGraph: 单 agent 图，用于 is_complex/zero_shot/emotion 等
- MeshGraph: 多 agent round-robin 图，用于策略讨论
- PlainTextFormatter: 自定义 formatter，替代默认的 JSON 格式
- Monkey-patch Agent._input_prompt 和 _output_keys_prompt 去掉包裹
- VectorRetriever + SentenceTransformerEmbedder: 检索相似案例
- cache_seed=2024 MASFactory 不支持，temperature=0.0 保证基本确定性
