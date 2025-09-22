import json
from html_to_markdown import convert_to_markdown
from pypdf import PdfReader, PdfWriter
from io import BytesIO
import string 
import requests
import hashlib
import os

with open("SC.json") as f:
    input_data = json.load(f)

def setup_folder(case, src_folder):
    cur_output_folder =  "{}{}".format(src_folder, case["source"])
    if not os.path.exists(cur_output_folder):
        os.makedirs(cur_output_folder)
    return cur_output_folder

def get_pdf(url, src_folder):
    encoded_url = url.encode("utf-8")
    hashed_url = hashlib.sha1(encoded_url).hexdigest()
    filename = "{}/full/{}.pdf".format(src_folder, hashed_url)
    return filename

def move_pdf(cur_file, case, tgt_folder):
    new_loc = "{}/{}.pdf".format(tgt_folder, case["case_id"])
    os.rename(cur_file, new_loc)
    return new_loc

def pdf2md(filename):
    print("Parsing: ", filename)
    reader = PdfReader(filename);
    return "".join([page.extract_text() for page in reader.pages])


src_folder = "output_pdfs/sc/"

new_json = []
for case in input_data:
    new_json_entry = {}
    new_json_entry["case_id"] = case["case_id"]
    if "short_description" in case:
        new_json_entry["short_description"] = case["short_description"]
    new_json_entry["case_title"] = case["case_title"]
    tgt_folder = setup_folder(case, src_folder)
    cur_file = get_pdf(case["file_urls"][0], src_folder)
    if os.path.exists(cur_file):
        new_file = move_pdf(cur_file, case, tgt_folder)
        md = pdf2md(new_file)
        new_json_entry["content"] = md
        new_json.append(new_json_entry)
    else:
        if os.path.exists("{}html".format(cur_file[:-3])):
            print("Have HTML not PDF for: ", cur_file[:-3])
        else:
            print("Can't find: ", cur_file)

with open("SC_clean.json", "w+") as f:
    f.write(json.dumps(new_json, indent=4))
    

