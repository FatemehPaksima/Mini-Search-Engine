import json
import re

input_file = "../drdr41.json"
output_file = "../data_dict.json"

data_dict = {}

def remove_html_tags(text):
    clean = re.compile("<.*?>")
    text = re.sub(clean, " ", text)
    return text.strip()

with open(input_file, "r", encoding="utf-8") as json_file:
    for line in json_file:
        entry = json.loads(line)
        url = entry["url"]
        html_content = entry["html"]
        paragraphs = re.findall(r'<p>(.*?)<\/p>', html_content, re.DOTALL)
        cleaned_paragraphs = [remove_html_tags(p) for p in paragraphs]
        data_dict[url] = cleaned_paragraphs

with open(output_file, "w", encoding="utf-8") as dict_file:
    json.dump(data_dict, dict_file, ensure_ascii=False, indent=4)

print("Data dictionary built successfully!")
