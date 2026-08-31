"""
content/mapper/question_mapper.py
Reads question Markdown files, extracts structured JSON via Ollama,
and publishes data/questions.json, data/mappings.json, and metadata.
"""

import json
from pathlib import Path
import ollama

def map_questions(model_name: str = "qwen2-vl"):
    root_dir = Path(__file__).resolve().parent.parent.parent
    q_md_folder = root_dir / "content" / "questions" / "markdown"
    topics_file = root_dir / "data" / "topics.json"
    
    q_meta_file = root_dir / "content" / "metadata" / "question_metadata.json"
    runtime_questions = root_dir / "data" / "questions.json"
    runtime_mappings = root_dir / "data" / "mappings.json"

    q_files = list(q_md_folder.glob("*.md"))
    if not q_files:
        print("⚠️ No question Markdown files found in content/questions/markdown/")
        return

    topics_context = ""
    if topics_file.exists():
        with open(topics_file, "r", encoding="utf-8") as f:
            topics_context = f.read()

    parsed_questions = []
    mappings = []

    for q_file in q_files:
        print(f"🗺️ Mapping questions for: {q_file.name}...")
        with open(q_file, "r", encoding="utf-8") as f:
            q_text = f.read()

        prompt = f"""
Parse the following questions text into structured JSON format.
For each question, extract:
- question_text
- options (list of strings)
- correct_answer
- topic (matched against available topics context: {topics_context[:1000]})
- cognitive_level (1 to 4)
- difficulty (Easy, Medium, Hard)

Text:
{q_text}

Return JSON with key "questions".
"""

        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )

        try:
            res_data = json.loads(response["message"]["content"])
            questions_list = res_data.get("questions", [])

            for idx, q in enumerate(questions_list, start=1):
                q_id = f"{q_file.stem}_q{idx}"
                q["question_id"] = q_id
                parsed_questions.append(q)

                mappings.append({
                    "question_id": q_id,
                    "matched_topic": q.get("topic", "General"),
                    "source_question_file": q_file.name
                })
        except Exception as e:
            print(f"❌ Error parsing question file {q_file.name}: {e}")

    # 1. Save metadata
    q_meta_file.parent.mkdir(parents=True, exist_ok=True)
    with open(q_meta_file, "w", encoding="utf-8") as f:
        json.dump({"questions_metadata": parsed_questions}, f, indent=2)

    # 2. Save runtime data/questions.json
    runtime_questions.parent.mkdir(parents=True, exist_ok=True)
    with open(runtime_questions, "w", encoding="utf-8") as f:
        json.dump({"questions": parsed_questions}, f, indent=2)

    # 3. Save runtime data/mappings.json
    with open(runtime_mappings, "w", encoding="utf-8") as f:
        json.dump({"mappings": mappings}, f, indent=2)

    print(f"✅ Published: {runtime_questions}")
    print(f"✅ Published: {runtime_mappings}")
