"""
run_pipeline.py
Batch converts PDFs into Markdown using Docling.
"""

from pathlib import Path
from content.converters.pdf_to_md import convert_pdf_to_md
from content.converters.question_pdf_to_md import convert_question_pdf_to_md


def run_pipeline():
    base_dir = Path(__file__).resolve().parent

    print("🚀 Starting PDF Conversion Pipeline...\n")
    processed_count = 0

    # 1. Process Document PDFs (inside content/documents)
    doc_folders = [
        base_dir / "content" / "documents" / "raw_pdf",
        base_dir / "content" / "documents" / "image_pdf",
    ]

    print("--- Checking Document Folders ---")
    for folder in doc_folders:
        print(f"📁 Checking: {folder}")
        if not folder.exists():
            print(f"   ⚠️ Folder does not exist: {folder}")
            continue

        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            print("   ℹ️ No PDF files found in this folder.")
            continue

        for pdf_file in pdf_files:
            print(f"   📄 Processing: {pdf_file.name}")
            convert_pdf_to_md(pdf_file.name)
            processed_count += 1

    # 2. Process Question Paper PDFs (inside content/questions)
    question_folders = [
        base_dir / "content" / "questions" / "question_pdf",
        base_dir / "content" / "questions" / "question_image_pdf",
    ]

    print("\n--- Checking Question Paper Folders ---")
    for folder in question_folders:
        print(f"📁 Checking: {folder}")
        if not folder.exists():
            print(f"   ⚠️ Folder does not exist: {folder}")
            continue

        pdf_files = list(folder.glob("*.pdf"))
        if not pdf_files:
            print("   ℹ️ No PDF files found in this folder.")
            continue

        for pdf_file in pdf_files:
            print(f"   📄 Processing: {pdf_file.name}")
            convert_question_pdf_to_md(pdf_file.name)
            processed_count += 1

    print(f"\n🎉 Finished! Total converted files: {processed_count}")


if __name__ == "__main__":
    run_pipeline()