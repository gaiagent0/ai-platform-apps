"""
prompts.py -- MeetCore v3
Modell-specifikus prompt optimalizacio 8 providerhez.
"""

from typing import Optional


def get_model_family(model_name: str) -> str:
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


def build_extraction_prompts(chunk: str, model_name: str = "", language: str = "hu") -> tuple:
    family = get_model_family(model_name)
    is_hungarian = language == "hu"
    lang_tag = "MAGYARUL" if is_hungarian else "IN ENGLISH"
    base = ("RESZTVEVOK: [names and roles]\n"
            "OSSZEFOGLALO: [2-3 sentences]\n"
            "HATARIDOK: [deadlines and owners, or NINCS]\n"
            "DONTESEK: [decisions made, or NINCS]\n"
            "TEENDOK: [action items with owners, or NINCS]\n"
            "KOVETKEZO LEPESEK: [next steps or meeting, or NINCS]")
    if family == "reasoning":
        return None, (f"<task>Meeting transcript summary {lang_tag}</task>\n\n"
                      f"Fill these 6 sections:\n{base}\n\n"
                      f"<transcript>\n{chunk}\n</transcript>")
    elif family == "npu":
        return ("Meeting summary. Short, concise.",
                f"/no_think\n{lang_tag} summary:\n\n{base}\n\n{chunk}")
    elif family in ("qwen3", "qwen2"):
        sys = "Professional meeting summarization assistant. Work in " + ("Hungarian." if is_hungarian else "English.")
        return (sys, f"/no_think\nSummarize {lang_tag}.\n{base}\n\n<atiras>\n{chunk}\n</atiras>")
    elif family == "gemma":
        sys = "You are a meeting summary assistant. " + ("Answer in Hungarian." if is_hungarian else "Answer in English.")
        return (sys, f"## Task\n{lang_tag} summarize.\n## Format\n{base}\n## Transcript\n{chunk}\n## Summary")
    elif family == "llama":
        sys = "Professional meeting summarization assistant. " + ("Work in Hungarian." if is_hungarian else "Work in English.")
        return (sys, f"Summarize {lang_tag}.\n{base}\n\n<transcript>\n{chunk}\n</transcript>")
    elif family == "claude":
        sys = "Expert meeting summarizer. Return structured " + ("Hungarian" if is_hungarian else "English") + " summaries."
        return (sys, f"<task>Summarize {lang_tag}</task>\n<sections>\n{base}\n</sections>\n<transcript>\n{chunk}\n</transcript>")
    else:
        sys = "Professional meeting summarizer. " + ("Hungarian language." if is_hungarian else "English language.")
        return (sys, f"Summarize {lang_tag}.\n\n{base}\n\n{chunk}")


def build_json_prompts(chunk: str, model_name: str = "", custom_prompt: str = "", language: str = "hu") -> tuple:
    is_hungarian = language == "hu"
    lang_note = "in Hungarian" if is_hungarian else "in English"
    context = f"\nContext: {custom_prompt}" if custom_prompt else ""
    schema = (
        '{"MeetingName":"string","People":{"title":"Participants","blocks":[{"id":"p1","type":"bullet","content":"...","color":""}]},'
        '"SessionSummary":{"title":"Summary","blocks":[{"id":"s1","type":"text","content":"...","color":""}]},'
        '"CriticalDeadlines":{"title":"Deadlines","blocks":[]},'
        '"KeyItemsDecisions":{"title":"Decisions","blocks":[]},'
        '"ImmediateActionItems":{"title":"Action Items","blocks":[]},'
        '"NextSteps":{"title":"Next Steps","blocks":[]},'
        '"MeetingNotes":{"meeting_name":"...","sections":[]}}'
    )
    system = f"Professional meeting summarizer. Return ONLY valid JSON {lang_note} -- no markdown."
    user = (f"Summarize {lang_note}. Fill: {schema}\n\n"
            f"Rules: blocks=[] if empty, unique ids, Hungarian content.{context}\n\n"
            f"Transcript:\n{chunk}\n\nReturn only JSON.")
    return system, user


def build_anthropic_prompts(chunk: str, custom_prompt: str = "", language: str = "hu") -> tuple:
    is_hungarian = language == "hu"
    lang_note = "in Hungarian" if is_hungarian else "in English"
    context = f"\n<context>{custom_prompt}</context>" if custom_prompt else ""
    schema = (
        '{"MeetingName":"string","People":{"title":"Participants","blocks":[{"id":"p1","type":"bullet","content":"...","color":""}]},'
        '"SessionSummary":{"title":"Summary","blocks":[{"id":"s1","type":"text","content":"...","color":""}]},'
        '"CriticalDeadlines":{"title":"Deadlines","blocks":[]},'
        '"KeyItemsDecisions":{"title":"Decisions","blocks":[]},'
        '"ImmediateActionItems":{"title":"Action Items","blocks":[]},'
        '"NextSteps":{"title":"Next Steps","blocks":[]},'
        '"MeetingNotes":{"meeting_name":"...","sections":[]}}'
    )
    system = "You are an expert meeting summarizer. Return ONLY raw JSON."
    user = (f"<task>Summarize {lang_note} as JSON.</task>\n"
            f"<schema>{schema}</schema>\n"
            "<rules>blocks=[] if empty, unique ids, Hungarian content.</rules>"
            f"{context}\n"
            f"<transcript>{chunk}</transcript>\n"
            "Return only JSON.")
    return system, user


def text_to_summary(extracted_text: str, chunk_index: int = 0) -> dict:
    """Parse text extraction output into structured JSON."""
    import re
    sections = {}
    current_label = None
    current_content = []
    labels = [("RESZTVEVOK", "People"), ("OSSZEFOGLALO", "SessionSummary"),
              ("HATARIDOK", "CriticalDeadlines"), ("DONTESEK", "KeyItemsDecisions"),
              ("TEENDOK", "ImmediateActionItems"), ("KOVETKEZO LEPESEK", "NextSteps")]
    for line in extracted_text.split("\n"):
        line = line.strip()
        upper = line.upper().rstrip(":")
        matched = False
        for label, key in labels:
            if upper == label or upper.startswith(label + ":"):
                if current_label and current_content:
                    sections[current_label] = "\n".join(current_content)
                current_label = key
                current_content = []
                matched = True
                part = line[line.find(":")+1:].strip() if ":" in line else ""
                if part:
                    current_content.append(part)
                break
        if not matched and current_label:
            current_content.append(line)
    if current_label and current_content:
        sections[current_label] = "\n".join(current_content)
    def make_blocks(content: str, prefix: str) -> list:
        items = [i.strip().lstrip("-*.)") for i in content.split("\n") if i.strip()]
        items = [i for i in items if i.upper() not in ("NINCS", "NONE", "N/A", "")]
        return [{"id": f"{prefix}{i+1}", "type": "bullet", "content": item, "color": ""} for i, item in enumerate(items)]
    name_match = re.search(r"(?:MEETING|MEGBESZELES|ERTEKEZLET)[:\s]+(.+?)[\n.]", extracted_text, re.IGNORECASE)
    meeting_name = name_match.group(1).strip() if name_match else f"Meeting {chunk_index + 1}"
    return {
        "MeetingName": meeting_name,
        "People": {"title": "Participants", "blocks": make_blocks(sections.get("People", ""), "p")},
        "SessionSummary": {"title": "Summary", "blocks": make_blocks(sections.get("SessionSummary", ""), "s") or []},
        "CriticalDeadlines": {"title": "Deadlines", "blocks": make_blocks(sections.get("CriticalDeadlines", ""), "d") or []},
        "KeyItemsDecisions": {"title": "Decisions", "blocks": make_blocks(sections.get("KeyItemsDecisions", ""), "k") or []},
        "ImmediateActionItems": {"title": "Action Items", "blocks": make_blocks(sections.get("ImmediateActionItems", ""), "a") or []},
        "NextSteps": {"title": "Next Steps", "blocks": make_blocks(sections.get("NextSteps", ""), "n") or []},
        "MeetingNotes": {"meeting_name": meeting_name, "sections": []},
    }
