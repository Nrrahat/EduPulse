"""
content/mapper/topic_mapper.py
Reads document Markdown, extracts taxonomy via Ollama, 
and publishes content/metadata/chapter_metadata.json & data/topics.json
"""

import json
from pathlib import Path
import ollama

def map_topics(model_name: str = "moondream"):
    root_dir = Path(__file__).resolve().parent.parent.parent
    md_folder = root_dir / "content" / "documents" / "markdown"
    meta_file = root_dir / "content" / "metadata" / "chapter_metadata.json"
    runtime_topics_file = root_dir / "data" / "topics.json"

    md_files = list(md_folder.glob("*.md"))
    if not md_files:
        print("⚠️ No document Markdown files found in content/documents/markdown/")
        return

    all_chapters = []

    for md_file in md_files:
        print(f"🗺️ Mapping taxonomy for: {md_file.name} using {model_name}...")
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()

        prompt = f"""
Analyze this document text and organize it strictly into a structured JSON hierarchy:
Chapter -> Topics -> Subtopics.

Text:
{text[:4000]}

Return valid JSON with key "chapter_name", "topics" (list containing topic_name and subtopics list).
"""

        response = ollama.chat(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            format="json"
        )

        try:
            parsed = json.loads(response["message"]["content"])
            parsed["source_file"] = md_file.name
            all_chapters.append(parsed)
        except Exception as e:
            print(f"❌ Error parsing metadata for {md_file.name}: {e}")

    # Write to metadata
    meta_file.parent.mkdir(parents=True, exist_ok=True)
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump({"chapters": all_chapters}, f, indent=2, ensure_ascii=False)

    # Write to data/topics.json
    runtime_topics_file.parent.mkdir(parents=True, exist_ok=True)
    with open(runtime_topics_file, "w", encoding="utf-8") as f:
        json.dump({"topics_data": all_chapters}, f, indent=2, ensure_ascii=False)

    print(f"✅ Published taxonomy to: {runtime_topics_file}")