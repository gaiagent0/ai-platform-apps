"""
prompts.py — MeetCore v3
Modell-specifikus prompt optimalizáció 8 providerhez.

Tudásfrissítés (2026-06-23):
  - DeepSeek-R1: NO system prompt (rontja a teljesítményt), XML tag-ek, temp=0.6
  - NPU: ultra-kompakt (minden token drága), /no_think prefx
  - Qwen3: /no_think, tömör, magyar
  - Qwen2.5: strukturált, explicit szakaszok
  - Gemma: fejléces, markdown-stílusú
  - Llama 3: explicit szakasz-heading, angol sys + magyar content
  - Claude: XML tag-ek, részletes
"""

from typing import Optional


def get_model_family(model_name: str) -> str:
    """Identify model family for prompt optimization."""
    m = model_name.lower()
    if any(k in m for k in ("deepseek", "qwq")):
        return "reasoning"
    if any(k in m for k in ("omnineural", "omni-neural")):
        return "omnineural"
    if any(k in m for k in ("npu", "nexa", "qat")):
        return "npu"
    if any(k in m for k in ("qwen3", "qwen3.5", "qwq-plus")):
        return "qwen3"
    if any(k in m for k in ("qwen2", "qwen-")):
        return "qwen2"
    if "gemma" in m:
        return "gemma"
    if "llama" in m:
        return "llama"
    if "claude" in m or "sonnet" in m or "haiku" in m:
        return "claude"
    if "gpt" in m or "o1" in m or "o3" in m:
        return "openai"
    return "generic"


def build_extraction_prompts(
    chunk: str,
    model_name: str = "",
    language: str = "hu",
) -> tuple[Optional[str], str]:
    """
    Build (system_prompt, user_prompt) for text extraction.
    Used by local providers (GenieX NPU, Ollama, Nexa).
    Returns (None, user_prompt) for reasoning models.
    """
    family = get_model_family(model_name)
    is_hungarian = language == "hu"
    lang_tag = "MAGYARUL" if is_hungarian else "IN ENGLISH"
    
    base_sections = (
        "RESZTVEVOK: [names and roles]
"
        "OSSZEFOGLALO: [2-3 sentences]
"
        "HATARIDOK: [deadlines and owners, or NINCS]
"
        "DONTESEK: [decisions made, or NINCS]
"
        "TEENDOK: [action items with owners, or NINCS]
"
        "KOVETKEZO LEPESEK: [next steps or meeting, or NINCS]"
    )
    
    if family == "reasoning":
        return None, (
            f"<task>Meeting transcript summary {lang_tag}</task>

"
            f"Fill these 6 sections based on the transcript:
{base_sections}

"
            f"<transcript>
{chunk}
</transcript>"
        )
    
    elif family == "npu":
        return (
            "Meeting summary. Short, concise.",
            f"/no_think\n{lang_tag} summary of this transcript:\n\n{base_sections}\n\
{chunk}"
        )
    
    elif family in ("qwen3", "qwen2"):
        return (
            "Professional meeting summarization assistant. Work in "
            + ("Hungarian." if is_hungarian else "English."),
            f"/no_think\nSummarize {lang_tag} this transcript.\n"
            f"Fill all 6 sections (write NINCS if no data):\n\n{base_sections}\n\n"
            f"<atiras>\n{chunk}\n</atiras>\n\nFill the sections!"
        )
    
    elif family == "gemma":
        return (
            "You are a meeting summary assistant. "
            + ("Answer in Hungarian." if is_hungarian else "Answer in English."),
            f"## Task\n{lang_tag} summarize this meeting transcript.\n\n"
            f"## Output format\nFill these 6 lines (NINCS if no data):\n\n{base_sections}\n\n"
            f"## Transcript\n{chunk}\n\n## Summary"
        )
    
    elif family == "llama":
        return (
            "You are a professional meeting summarization assistant. "
            + ("Work in Hungarian." if is_hungarian else "Work in English."),
            f"Summarize {lang_tag} the following transcript.\n"
            f"Fill all 6 sections (write NINCS if no data):\n\n{base_sections}\n\n"
            f"<transcript>\n{chunk}\n</transcript>"
        )
    
    elif family == "claude":
        return (
            "You are an expert meeting summarizer. Return structured "
            + ("Hungarian" if is_hungarian else "English") + " summaries.",
            f"<task>Summarize {lang_tag} this meeting transcript.</task>\n\n"
            f"<sections>\n{base_sections}\n</sections>\n\n"
            f"<transcript>\n{chunk}\n</transcript>"
        )
    
    else:  # generic / openai
        return (
            "Professional meeting summarization assistant. "
            + ("Hungarian language." if is_hungarian else "English language."),
            f"Summarize {lang_tag} this meeting transcript.\n\n{base_sections}\n\n{chunk}"
        )


def build_json_prompts(
    chunk: str,
    model_name: str = "",
    custom_prompt: str = "",
    language: str = "hu",
) -> tuple[str, str]:
    """
    Build (system_prompt, user_prompt) for JSON mode.
    Used by cloud providers (LiteLLM, OpenAI, etc.).
    """
    is_hungarian = language == "hu"
    lang_note = "in Hungarian" if is_hungarian else "in English"
    context_line = f"\nContext: {custom_prompt}" if custom_prompt else ""
    
    compact_schema = (
        '{"MeetingName":"string","People":{"title":"Participants","blocks":[{"id":"p1","type":"bullet","content":"...","color":""}]},'
        '"SessionSummary":{"title":"Summary","blocks":[{"id":"s1","type":"text","content":"...","color":""}]},'
        '"CriticalDeadlines":{"title":"Deadlines","blocks":[]},'
        '"KeyItemsDecisions":{"title":"Decisions","blocks":[]},'
        '"ImmediateActionItems":{"title":"Action Items","blocks":[]},'
        '"NextSteps":{"title":"Next Steps","blocks":[]},'
        '"MeetingNotes":{"meeting_name":"...","sections":[]}}'
    )
    
    system = (
        "You are a professional meeting summarizer. "
        f"Return ONLY valid JSON {lang_note} — no markdown, no explanation."
    )
    
    user = (
        f"Summarize {lang_note}. Fill this JSON structure:\n{compact_schema}\n\n"
        "Rules: blocks=[] if empty, unique ids (p1,p2... s1...), "
        f"type: text|bullet|heading1|heading2, {lang_note} content."
        f"{context_line}\n\n"
        f"Transcript:\n---\n{chunk}\n---\n\nReturn only JSON."
    )
    
    return system, user


def build_anthropic_prompts(
    chunk: str,
    custom_prompt: str = "",
    language: str = "hu",
) -> tuple[str, str]:
    """Claude-specific prompts with XML tags."""
    is_hungarian = language == "hu"
    system = "You are an expert meeting summarizer. Return ONLY raw JSON — no code blocks."
    compact_schema = (
        '{"MeetingName":"string","People":{"title":"Participants","blocks":[{"id":"p1","type":"bullet","content":"...","color":""}]},'
        '"SessionSummary":{"title":"Summary","blocks":[{"id":"s1","type":"text","content":"...","color":""}]},'
        '"CriticalDeadlines":{"title":"Deadlines","blocks":[]},'
        '"KeyItemsDecisions":{"title":"Decisions","blocks":[]},'
        '"ImmediateActionItems":{"title":"Action Items","blocks":[]},'
        '"NextSteps":{"title":"Next Steps","blocks":[]},'
        '"MeetingNotes":{"meeting_name":"...","sections":[]}}'
    )
    context_part = f"
<context>{custom_prompt}</context>" if custom_prompt else ""
    lang_note = "in Hungarian" if is_hungarian else "in English"
    user = (
        f"<task>Summarize this transcript {lang_note} as JSON.</task>

"
        f"<schema>{compact_schema}</schema>

"
        "<rules>blocks=[] if empty, unique ids, type: text|bullet|heading1|heading2, "
        f"{lang_note} content.</rules>"
        f"{context_part}

"
        f"<transcript>{chunk}</transcript>

Return only JSON."
    )
    return system, user


def text_to_summary(extracted_text: str, chunk_index: int = 0) -> dict:
    """
    Parse text extraction output into SummaryResponse-compatible dict.
    Used by local providers (text → structured JSON).
    """
    import re
    
    sections = {}
    current_label = None
    current_content = []
    
    labels = [
        ("RESZTVEVOK", "People"),
        ("OSSZEFOGLALO", "SessionSummary"),
        ("HATARIDOK", "CriticalDeadlines"),
        ("DONTESEK", "KeyItemsDecisions"),
        ("TEENDOK", "ImmediateActionItems"),
        ("KOVETKEZO LEPESEK", "NextSteps"),
    ]
    
    for line in extracted_text.split("\n"):
        line = line.strip()
        matched = False
        upper = line.upper().rstrip(":")
        for label, key in labels:
            if upper == label or upper.startswith(label + ":"):
                if current_label and current_content:
                    sections[current_label] = "\n".join(current_content)
                current_label = key
                current_content = []
                matched = True
                # Extract content after label if on same line
                content_part = line[line.find(":")+1:].strip() if ":" in line else ""
                if content_part:
                    current_content.append(content_part)
                break
        if not matched and current_label:
            current_content.append(line)
    
    if current_label and current_content:
        sections[current_label] = "\n".join(current_content)
    
    def make_blocks(content: str, prefix: str) -> list:
        items = [i.strip().lstrip("-*\u2022.)") for i in content.split("\n") if i.strip()]
        items = [i for i in items if i.upper() not in ("NINCS", "NONE", "N/A", "")]
        return [
            {"id": f"{prefix}{i+1}", "type": "bullet", "content": item, "color": ""}
            for i, item in enumerate(items)
        ]
    
    name_match = re.search(r"(?:MEETING|MEGBESZELES|ERTEKEZLET)[:\s]+(.+?)[\n.]", extracted_text, re.IGNORECASE)
    meeting_name = name_match.group(1).strip() if name_match else f"Meeting {chunk_index + 1}"
    
    people_blocks = make_blocks(sections.get("People", ""), "p")
    summary_blocks = make_blocks(sections.get("SessionSummary", ""), "s")
    deadline_blocks = make_blocks(sections.get("CriticalDeadlines", ""), "d")
    decision_blocks = make_blocks(sections.get("KeyItemsDecisions", ""), "k")
    action_blocks = make_blocks(sections.get("ImmediateActionItems", ""), "a")
    next_blocks = make_blocks(sections.get("NextSteps", ""), "n")
    
    return {
        "MeetingName": meeting_name,
        "People": {"title": "Participants", "blocks": people_blocks},
        "SessionSummary": {"title": "Summary", "blocks": summary_blocks or []},
        "CriticalDeadlines": {"title": "Deadlines", "blocks": deadline_blocks or []},
        "KeyItemsDecisions": {"title": "Decisions", "blocks": decision_blocks or []},
        "ImmediateActionItems": {"title": "Action Items", "blocks": action_blocks or []},
        "NextSteps": {"title": "Next Steps", "blocks": next_blocks or []},
        "MeetingNotes": {"meeting_name": meeting_name, "sections": []},
    }
