"""
Strategy discussion component using MeshGraph for round-robin 3-agent discussion.
Aligned with source: multiagent.py select_strategy_by_group()

Source uses autogen GroupChat (admin + 3 agents, round-robin, max_round=4).
MeshGraph provides equivalent round-robin with shared HistoryMemory:
- Controller routes to agents in round-robin order
- Shared HistoryMemory accumulates the discussion (admin prompt + agent responses)
- Each agent sees prior discussion as chat history from shared memory
"""

import re
from collections import Counter
from masfactory import Agent, OpenAIModel, NodeTemplate, MeshGraph
from masfactory.adapters.memory import HistoryMemory
from ..patch_masfactory import PlainTextFormatter
from ..prompts import get_prompt


def create_strategy_discussion_graph(model: OpenAIModel):
    """Build MeshGraph for 3-agent strategy discussion.

    Source config (from multiagent.py select_strategy_by_group):
    - admin prompt: select_strategy template (context, emotion, cause, intention, examples)
    - 3 agents, each: instructions="You are a psychological counseling expert."
    - temperature: 0.0, max_tokens: 400
    - max_round: agent_num + 1 = 4 (1 admin + 3 agents)

    MeshGraph equivalent:
    - admin prompt passed via invoke input, referenced as {admin_prompt} in prompt_template
    - max_iterations=3 (3 agents, each speaks once)
    - shared HistoryMemory auto-accumulates discussion history
    """
    shared_memory = HistoryMemory(top_k=100, memory_size=100)

    # Source: agent system_message = "You are a psychological counseling expert."
    # Source: agent_1 has no extra hint; agent_2/3 get "Try to choose a different strategy from others"
    agents = [
        NodeTemplate(
            Agent,
            role_name="agent_0",
            instructions="You are a psychological counseling expert.",
            prompt_template="{message}",
            model_settings={"max_tokens": 400},
            formatters=PlainTextFormatter(),
        ),
        NodeTemplate(
            Agent,
            role_name="agent_1",
            instructions="You are a psychological counseling expert.",
            prompt_template="{message}",
            model_settings={"max_tokens": 400},
            formatters=PlainTextFormatter(),
        ),
        NodeTemplate(
            Agent,
            role_name="agent_2",
            instructions="You are a psychological counseling expert.",
            prompt_template="{message}",
            model_settings={"max_tokens": 400},
            formatters=PlainTextFormatter(),
        ),
    ]

    graph = MeshGraph(
        name="strategy_discussion",
        agents=agents,
        model=model,
        shared_memory=shared_memory,
        max_iterations=3,
        # Don't terminate early — let all 3 agents speak
        terminate_condition_function=lambda _m, _a: False,
    )

    graph.build()
    return graph


def run_strategy_discussion(graph, context, emo_and_reason, cau_and_reason, int_and_reason, examples):
    """Invoke strategy discussion graph. Returns list of strategies.

    Source: multiagent.py select_strategy_by_group()
    - Builds admin prompt from select_strategy template
    - Runs 3-agent round-robin discussion
    - Parses strategies from discussion history
    """
    # Build admin prompt from source template
    admin_prompt = get_prompt("select_strategy").format(
        context=context,
        emo_and_reason=emo_and_reason,
        cau_and_reason=cau_and_reason,
        int_and_reason=int_and_reason,
        examples=examples,
    )

    # Reset shared memory for fresh discussion
    graph._shared_memory.reset()

    # Invoke: admin_prompt flows to each agent via controller's message cache
    # MeshGraph (Loop) edges use default key "message", so wrap input accordingly
    graph._forward({"message": admin_prompt})

    # Extract assistant responses from shared memory
    messages = graph._shared_memory.get_messages(top_k=0)
    discussion_history = [
        msg["content"] for msg in messages if msg["role"] == "assistant"
    ]

    # Parse strategies from discussion — same regex as source
    # Source fallback: if regex fails, extract strategies from examples via Counter
    strategies = re.findall(
        r"Strategy:\s*\[?([a-zA-Z ]+)\]?", "\n".join(discussion_history)
    )
    if not strategies:
        strategies = re.findall(r'\[([a-zA-Z ]+)\]', examples)
        counter = Counter(strategies)
        most_common = counter.most_common(3)
        strategies = [item[0] for item in most_common]

    # Deduplicate while preserving order
    cleaned = []
    for s in strategies:
        s = s.strip()
        if s and s not in cleaned:
            cleaned.append(s)

    return cleaned
