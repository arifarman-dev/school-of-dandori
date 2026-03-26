from pathlib import Path
import json
from extract_data import parse_course_pdf

def parse_all_courses(folder_path):
    results = []
    pdf_files = Path(folder_path).glob("*.pdf")
    
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file.name}")
        course = parse_course_pdf(str(pdf_file))
        results.append(course)
    
    return results

courses = parse_all_courses("data")

with open("courses.json", "w", encoding="utf-8") as f:
    json.dump(courses, f, indent=2, ensure_ascii=False)