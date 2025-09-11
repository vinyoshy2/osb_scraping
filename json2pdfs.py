import json
from html_to_markdown import convert_to_markdown
from md2pdf.core import md2pdf
import string 

with open("OSB.json") as f:
    input_data = json.load(f)

output_folder = "output_pdfs/"

def format_case(case):
    title = "# {} #\n".format(case["case_title"])
    tags = "**Tags**: {}  \n".format(", ".join(case["tags"]))
    location = "**Location**: {}  \n".format(case["location"])
    decision = "**Decision**: "
    body = convert_to_markdown(case["content"])
    return "{}{}{}{}{}".format(title, decision, tags, location, body)

def clean_title_word(word):
    word = word.lower()
    trans = str.maketrans("", "", string.punctuation)
    return word.translate(trans)

def gen_filename(case):
    split_title = case["case_title"].split()
    split_title = [clean_title_word(word) for word in split_title]
    num_words = len(split_title)
    return "_".join(split_title[:min(3, num_words)])

def is_summary(case):
    return "Summary decisions examin" in case["content"]

for case in input_data:
    if not is_summary(case):
        case_str = format_case(case)
        filename = gen_filename(case)
        full_path = "{}{}.pdf".format(output_folder, filename)
        md2pdf(pdf_file_path=full_path, md_content=case_str)

