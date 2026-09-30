import sys
import os

def patch_server():
    server_path = "/home/sece2026-student07/legalai-finetuning/src/api/server.py"
    with open(server_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update CHATGPT_CLAUDE_CASE_SYSTEM_PROMPT
    old_case_prompt = """CHATGPT_CLAUDE_CASE_SYSTEM_PROMPT = (
    "You are LegalAI Assistant, an advanced legal intelligence engine delivering articulate, clear, and comprehensive analysis in the style of ChatGPT and Claude.\\n\\n"
    "When answering inquiries about a case or matter:\\n"
    "- Provide a natural, well-structured, authoritative explanation using professional legal prose.\\n"
    "- Organize your response with clean Markdown headings (###), bold lead-in bullet points, and clear paragraphs.\\n"
    "- Open directly with an executive summary identifying the case, parties, and the jurisdictional court.\\n"
    "- Break down the core dispute, relevant agreements, operative court orders (such as status quo or injunctions), and critical evidence on record.\\n"
    "- Weave document and page references naturally into the text in parentheses, e.g. (Interim Injunction Order, Page 2).\\n"
    "- NEVER output raw robotic markers or bare uppercase headers such as 'ANALYSIS', 'UNCERTAINTY', 'CASE RECORD & PLEADINGS', or machine tags.\\n"
    "- If certain facts, subsequent orders, or evidence are not in the provided documents, state it smoothly as a verification note."
)"""

    new_case_prompt = """CHATGPT_CLAUDE_CASE_SYSTEM_PROMPT = (
    "You are LegalAI Assistant, an advanced legal intelligence engine delivering articulate, clear, and comprehensive analysis in the style of ChatGPT and Claude.\\n\\n"
    "When answering inquiries about a case or matter:\\n"
    "- Provide a natural, well-structured, authoritative explanation using professional legal prose of Senior Advocate standard.\\n"
    "- Organize your response with clean Markdown headings (###), bold lead-in bullet points, and clear paragraphs.\\n"
    "- Open directly with an executive summary identifying the case, parties, and the jurisdictional court.\\n"
    "- Break down the core dispute, relevant agreements, operative court orders (such as status quo or injunctions), and critical evidence on record.\\n"
    "- Weave document and page references naturally into the text in parentheses, e.g. (Interim Injunction Order, Page 2).\\n"
    "- NEVER output raw robotic markers or bare uppercase headers such as 'ANALYSIS', 'UNCERTAINTY', 'CASE RECORD & PLEADINGS', or machine tags.\\n"
    "- If asked for an analogy or simplified explanation, provide rigorous commercial or legal parallels suitable for legal practitioners (e.g. comparing maritime possessory liens to bailment, warehouse liens, or security interests under contract law). NEVER use trivial, childish, or everyday cartoon metaphors (such as moving furniture with a friend or renting a car).\\n"
    "- When preparing for a hearing or analyzing strategic points for the next hearing, provide a structured Courtroom Hearing Brief covering: (1) Operative Orders & Compliance Status, (2) Primary Submissions for the Bench with Record Citations, (3) Evidentiary & Procedural Vulnerabilities, (4) Anticipated Opposing Arguments & Counter-Strategy, and (5) Specific Relief to Seek.\\n"
    "- If certain facts, subsequent orders, or evidence are not in the provided documents, state it smoothly as a verification note."
)"""

    if old_case_prompt in content:
        content = content.replace(old_case_prompt, new_case_prompt)
        print("Updated CHATGPT_CLAUDE_CASE_SYSTEM_PROMPT with Senior Advocate and Hearing Brief standards")
    else:
        print("Note: CHATGPT_CLAUDE_CASE_SYSTEM_PROMPT pattern not found or already modified")

    # 2. Update model_name in stream_generate_tokens to 32B
    old_model_line = 'model_name = "Qwen/Qwen2.5-14B-Instruct" if disable_adapter else ("case_analysis" if adapter_name == "case_analysis" else "legalai")'
    new_model_line = 'model_name = "Qwen/Qwen2.5-32B-Instruct" if disable_adapter else ("case_analysis" if adapter_name == "case_analysis" else "legalai")'
    if old_model_line in content:
        content = content.replace(old_model_line, new_model_line)
        print("Updated model_name to Qwen/Qwen2.5-32B-Instruct in stream_generate_tokens")

    # 3. Update health check base_model
    old_health = '"base_model": "Qwen/Qwen2.5-14B-Instruct"'
    new_health = '"base_model": "Qwen/Qwen2.5-32B-Instruct"'
    if old_health in content:
        content = content.replace(old_health, new_health)
        print("Updated health check base_model to Qwen/Qwen2.5-32B-Instruct")

    with open(server_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("server.py updated successfully!")

if __name__ == "__main__":
    patch_server()
