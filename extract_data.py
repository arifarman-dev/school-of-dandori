from pdfminer.high_level import extract_text
from pprint import pprint

def clean_line(line):
    return line.lstrip("•·").strip()

def parse_course_pdf(pdf_path):
    text = extract_text(pdf_path)

    lines = [clean_line(line) for line in text.splitlines() if clean_line(line)]
    course = {}

    course["title"] = lines[0]
    course["class_id"] = lines[len(lines)-2].split("Class ID:")[-1].strip().split("|")[0].strip()
    print(course["class_id"])

    field_map = {
        "Instructor:": "instructor",
        "Course Type:": "course_type",
        "Location:": "location",
        "Cost:": "cost"
    }

    SECTION_HEADINGS = {"learning objectives", "provided materials", 
                    "skills developed", "course description"}
    
    for i, line in enumerate(lines):
        for key, field in field_map.items():
            if line == key and i + 1 < len(lines):
                course[field] = lines[i + 1]

    def extract_section(lines, heading):
        items = []
        in_section = False
        for line in lines:
            if line == heading:
                in_section = True
                continue
            if in_section:
                if line.strip().lower() in SECTION_HEADINGS:
                    break
                else:
                    items.append(line)
        return items
    
    course["learning_objectives"] = extract_section(lines, "Learning Objectives")
    course["provided_materials"] = extract_section(lines, "Provided Materials")
    
    def extract_skills(lines):
        skills = []
        in_section = False
        for line in lines:
            if line == "Skills Developed":
                in_section = True
                continue
            if in_section:
                if line.endswith(":"):
                    break
                if line == "Course Description":
                    break
                skills.append(line)
        return skills
    
    course["skills"] = extract_skills(lines)
    
    def extract_description(lines):
        desc = []
        in_section = False
        for line in lines:
            if line == "Course Description":
                in_section = True
                continue
            if in_section:
                if line.startswith("Class ID:"):
                    break
                desc.append(line)
        return " ".join(desc)
    
    course["description"] = extract_description(lines)
    return course

