import json
import re

input_file = "../drdr41.json"
output_file = "../title_dict.json"

word_set = set()

# تابع تمیز کردن متن
def clean_text(text):
    text = re.sub(r"[^\w\s]", "", text)  # حذف کاراکترهای اضافی
    text = text.replace("ي", "ی").replace("ك", "ک")  # نرمال‌سازی فارسی
    return text

with open(input_file, "r", encoding="utf-8") as json_file:
    for line in json_file:
        data = json.loads(line)
        html_content = data["html"]

        # استخراج عنوان از HTML
        title = re.search(r"<title>(.*?)<\/title>", html_content)
        title_text = clean_text(title.group(1)) if title else ""

        # استخراج کلمات از عنوان برای دیکشنری
        words = re.findall(r'\b\w+\b', title_text)
        for word in words:
            word_set.add(word)

# تبدیل مجموعه کلمات به لیست برای ذخیره در فایل JSON
title_words_list = list(word_set)

with open(output_file, "w", encoding="utf-8") as dict_file:
    json.dump(title_words_list, dict_file, ensure_ascii=False, indent=4)

print("Title words dictionary built successfully!")
