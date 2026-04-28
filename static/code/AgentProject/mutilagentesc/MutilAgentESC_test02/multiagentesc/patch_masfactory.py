"""
Patch MASFactory Agent to remove prompt wrapping and JSON format requirements.

Problem:
    MASFactory wraps user prompts in "MESSAGE TO YOU:" and adds
    "RESPONSE FORMAT REQUIREMENTS: output JSON" instructions. These conflict
    with MultiAgentESC's prompt format (Response: [strategy] text), causing
    the model to output JSON instead of the expected text format.

Solution (all in project code, MASFactory package untouched):
    1. PlainTextFormatter - accepts plain text output, no format requirements
    2. Monkey-patch Agent._input_prompt - removes "MESSAGE TO YOU" wrapper
    3. Monkey-patch Agent._output_keys_prompt - removes format requirement instructions
"""

import ast
import json as _json
import re

from masfactory.components.agents.agent import Agent
from masfactory.core.message.base import StatefulFormatter


class PlainTextFormatter(StatefulFormatter):
    """Custom formatter: clean prompts in, plain text out.

    Replaces MASFactory's default (ParagraphMessageFormatter + JsonMessageFormatter).

    dump():  single-key dict -> just the value string (no "key:\n" prefix)
             multi-key dict  -> standard paragraph format
    format(): accepts any model output (text or JSON), wraps as {output_key: raw_text}
    """

    def __init__(self):
        super().__init__()
        self._is_input_formatter = True
        self._is_output_formatter = True
        self._agent_introducer = ""

    # ------------------------------------------------------------------
    # dump: serialize prompt to send to model
    # ------------------------------------------------------------------

    def dump(self, message):
        """Serialize user payload without key wrapper.

        Single-key dict (e.g. {"input": "prompt text"}) -> "prompt text"
        Multi-key dict                                   -> standard paragraph format
        """
        if isinstance(message, str):
            return message

        if isinstance(message, dict):
            if len(message) == 1:
                val = next(iter(message.values()))
                if isinstance(val, str):
                    return val
            lines = []
            for key, val in message.items():
                if val is None:
                    continue
                rendered = val if isinstance(val, str) else str(val)
                lines.append(f"{key}:\n{rendered}")
            return "\n\n".join(lines)

        return str(message)

    # ------------------------------------------------------------------
    # format: parse model output
    # ------------------------------------------------------------------

    def format(self, message):
        """Accept any model output, wrap plain text as {output_key: raw_text}.

        Handles:
        - Plain text response            -> {"response": "raw text"}
        - JSON {"response": "text"}     -> {"response": "text"}
        - Markdown code blocks           -> stripped to raw text
        - Malformed / empty             -> {"<output_key>": ""}
        """
        raw = message
        if isinstance(raw, dict):
            return self._normalize_dict(raw)

        text = str(raw)

        # Strip think blocks
        text = re.sub(r"<think.*?</think\s*>", "", text, flags=re.DOTALL).strip()

        output_key = list(self._field_keys.keys())[0] if self._field_keys else "output"

        # Try JSON from fenced code block
        for cand in re.findall(r"```json\s*(.*?)```", text, flags=re.DOTALL):
            cand = cand.strip()
            try:
                parsed = _json.loads(cand)
                return self._normalize_dict(parsed)
            except Exception:
                pass

        # Try bare JSON
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = _json.loads(text[start:end + 1])
                return self._normalize_dict(parsed)
            except Exception:
                pass

        # Fallback: raw text
        return {output_key: text.strip()}

    # ------------------------------------------------------------------
    # internal
    # ------------------------------------------------------------------

    def _normalize_dict(self, d):
        """Ensure parsed dict has the expected output key; fill with raw text on mismatch."""
        output_key = list(self._field_keys.keys())[0] if self._field_keys else "output"
        result = {output_key: ""}
        if output_key in d:
            result[output_key] = d[output_key]
        else:
            for v in d.values():
                if isinstance(v, str):
                    result[output_key] = v
                    break
        return result


# ----------------------------------------------------------------------
# Monkey-patches — applied at import time so all Agent instantiations
# are affected.
# ----------------------------------------------------------------------

_original_input_prompt = Agent._input_prompt


def _patched_input_prompt(self):
    """Remove 'MESSAGE TO YOU' wrapper: return {"input": prompt}."""
    formatted_input = self._prompt_template_format(self._prompt_template)
    return {"input": formatted_input}


_original_output_keys_prompt = Agent._output_keys_prompt


def _patched_output_keys_prompt(self):
    """Suppress MASFactory's auto-generated format requirements.

    Without this patch, user message contains:
        RESPONSE FORMAT REQUIREMENTS: !IMPORTANT!: output JSON...
        REQUIRED OUTPUT FIELDS: {"response": ""}

    These instructions conflict with MultiAgentESC prompts that expect
    "Response: [strategy] text" plain-text output.
    """
    return {}


Agent._input_prompt = _patched_input_prompt
Agent._output_keys_prompt = _patched_output_keys_prompt
