import json
import re
import time
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

# تابع تمیز کردن متن
def clean_text(text):
    text = re.sub(r"[^\w\s]", "", text)  # حذف کاراکترهای اضافی
    text = text.replace("ي", "ی").replace("ك", "ک")  # نرمال‌سازی فارسی
    return text

# اتصال به Elasticsearch
es = Elasticsearch(["http://localhost:9200"], request_timeout=120)
if es.ping():
    print("Connected to Elasticsearch!")
else:
    print("Elasticsearch connection failed!")
    exit()

# نام ایندکسی که می‌خواهید ایجاد کنید
index_name = "drdrwebpages"  # ایندکس باید به حروف کوچک باشد


# ایجاد ایندکس همراه با مپینگ و تنظیمات بهبود یافته
mapping = {
    "mappings": {
        "properties": {
            "url": {"type": "keyword"},
            "title": {"type": "text", "analyzer": "custom_analyzer"},
            "body": {
                "type": "text",
                "analyzer": "custom_analyzer",
                "term_vector": "with_positions_offsets",
            },
            "suggest": {
                "type": "completion",
                "analyzer": "simple",
                "preserve_separators": False  # عدم جدا کردن واژگان با فاصله
            }
        }
    },
    "settings": {
        "analysis": {
            "filter": {
                "shingle_filter": {
                    "type": "shingle",
                    "min_shingle_size": 2,
                    "max_shingle_size": 3,
                    "output_unigrams": True
                }
            },
            "analyzer": {
                "custom_analyzer": {
                    "tokenizer": "standard",
                    "filter": ["lowercase", "shingle_filter"]
                }
            }
        }
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)
    print(f"Index '{index_name}' created with mapping and settings!")
else:
    print(f"Index '{index_name}' already exists!")

# تابع همگام‌سازی داده‌ها به صورت بلک
def bulk_sync(dictionaries, index_name):
    actions = [
        {
            "_index": index_name,
            "_source": record,
        }
        for record in dictionaries
    ]
    bulk(es, actions, refresh=True)  # افزودن پارامتر refresh برای به‌روزرسانی سریع

# تابع ایندکس کردن داده‌ها از فایل JSON و ساخت دیکشنری کلمات از عنوان‌ها
def index_documents(file_path):
    bulk_data = []
    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            data = json.loads(line)
            url = data["url"]
            html_content = data["html"]

            # استخراج عنوان از HTML
            title = re.search(r"<title>(.*?)<\/title>", html_content)
            title_text = clean_text(title.group(1)) if title else ""
            body = re.sub(r"<.*?>", "", html_content)  # حذف تگ‌های HTML
            body = clean_text(body)

            # استخراج کلمات از عنوان برای دیکشنری
            words = re.findall(r'\b\w+\b', title_text)

            # ساخت مستند و ایندکس کردن آن در Elasticsearch
            doc = {
                "url": url,
                "title": title_text,
                "body": body,
                "suggest": {
                    "input": words
                }
            }
            bulk_data.append(doc)

            # اگر تعداد مستندات به 1000 رسید، آن‌ها را به صورت بلک ارسال کنید
            if len(bulk_data) >= 1000:
                bulk_sync(bulk_data, index_name)
                bulk_data = []

    # ارسال باقی‌مانده مستندات
    if bulk_data:
        bulk_sync(bulk_data, index_name)


# فراخوانی تابع برای ایندکس کردن
start_time = time.time()
index_documents("../drdr41.json")  # بررسی مسیر فایل JSON
time = time.time() - start_time
print(f"Indexing completed in {time} seconds , {time/60} minutes")
