import json
from pathlib import Path
import ollama
from pydantic import BaseModel, Field


# --- Schema for Bangla Taxonomy Extraction ---
class TopicSchema(BaseModel):
    topic_name: str = Field(description="টপিকের নাম (বাংলায়)")
    subtopics: list[str] = Field(description="সাব-টপিকের তালিকা (বাংলায়)")


class ChapterSchema(BaseModel):
    chapter_name: str = Field(description="অধ্যায়ের নাম (বাংলায়)")
    topics: list[TopicSchema] = Field(description="এই অধ্যায়ের অধীনে টপিকের তালিকা")


class TaxonomySchema(BaseModel):
    chapters: list[ChapterSchema] = Field(description="নিষ্কাশিত অধ্যায়গুলির তালিকা")


def map_topics(model_name: str = "qwen2.5:7b"):
    root_dir = Path(__file__).resolve().parent.parent.parent
    md_folder = root_dir / "content" / "documents" / "markdown"
    topics_file = root_dir / "data" / "topics.json"

    md_files = list(md_folder.glob("*.md"))
    if not md_files:
        print("⚠️ No document Markdown files found in content/documents/markdown/")
        return

    all_chapters = []

    for md_file in md_files:
        print(f"🗺️ Mapping Bangla taxonomy for: {md_file.name} using {model_name}...")
        
        with open(md_file, "r", encoding="utf-8") as f:
            text = f.read()

        prompt = f"""
        নিচের ডকুমেন্টটি বিশ্লেষণ করুন এবং বাংলায় অধ্যায়, টপিক এবং সাব-টপিকের কাঠামোগত JSON তৈরি করুন।
        সব টপিক এবং সাব-টপিকের নাম অবশ্যই মূল ডকুমেন্টের বাংলা ভাষায় রাখুন।

        ডকুমেন্টের বিষয়বস্তু (Document Content):
        {text}
        """

        try:
            # Enforce schema constraint via Ollama structured output
            response = ollama.chat(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                format=TaxonomySchema.model_json_schema()
            )

            parsed = json.loads(response["message"]["content"])
            
            for chapter in parsed.get("chapters", []):
                chapter["source_file"] = md_file.name
                all_chapters.append(chapter)

        except Exception as e:
            print(f"❌ Error parsing metadata for {md_file.name}: {e}")

    # Save master taxonomy with unicode support (ensure_ascii=False for Bangla characters)
    topics_file.parent.mkdir(parents=True, exist_ok=True)
    with open(topics_file, "w", encoding="utf-8") as f:
        json.dump({"topics_data": all_chapters}, f, indent=2, ensure_ascii=False)

    print(f"✅ Master Bangla taxonomy published to: {topics_file}")


if __name__ == "__main__":
    map_topics()