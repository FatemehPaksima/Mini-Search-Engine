from flask import Flask, request, jsonify, render_template, redirect, url_for
import re
import time
import json
from elasticsearch import Elasticsearch

# اتصال به Elasticsearch
es = Elasticsearch(["http://localhost:9200"])
if es.ping():
    print("Connected to Elasticsearch!")
else:
    print("Elasticsearch connection failed!")
    exit()

index_name = "drdrwebpages"

# لود کردن دیکشنری کلمات فارسی
with open("title_dict.json", "r", encoding="utf-8") as dict_file:
    dictionary = json.load(dict_file)
# لود کردن دیکشنری برای ذخیره کوئری‌های کاربران
try:
    with open("user_queries.json", "r", encoding="utf-8") as user_queries_file:
        user_queries = json.load(user_queries_file)
except FileNotFoundError:
    user_queries = {}

# لود کردن دیکشنری از پیش ساخته‌شده
with open("../data_dict.json", "r", encoding="utf-8") as dict_file:
    data_dict = json.load(dict_file)


# تابع نرمال‌سازی متن
def normalize_text(text):
    text = re.sub(r"[^\w\s]", "", text)  # حذف کاراکترهای اضافی
    return text


# تابع حذف تگ‌های HTML، جایگزینی با فاصله و حذف بخش‌های انگلیسی
def remove_html_tags_and_english(text):
    clean = re.compile("<.*?>")
    text = re.sub(clean, " ", text)  # جایگزینی تگ‌ها با فاصله
    text = re.sub(r"[a-zA-Z]", " ", text)  # جایگزینی بخش‌های انگلیسی با فاصله
    text = re.sub(r"\s+", " ", text)  # حذف فاصله‌های اضافی
    return text.strip()


# تابع محدود کردن تعداد کاراکترها و حفظ نشانه‌گذاری‌ها
def limit_text(text, max_chars=300):
    if len(text) > max_chars:
        text = text[:max_chars]
        if not text.endswith("."):
            text += "..."
    return text


# با هر جستجوی کاربر کلمات را به آن اضافه میکنیم
def update_user_queries(query, corrections, results):
    # بررسی کوئری و اصلاحات پیشنهاد شده
    if corrections or len(results) == 0:
        # اگر اصلاحاتی وجود داشت، کوئری را ذخیره نکنید
        return
    if query in user_queries:
        user_queries[query] += 1
    else:
            user_queries[query] = 1
    # ذخیره دیکشنری به صورت دائمی
    with open("user_queries.json", "w", encoding="utf-8") as user_queries_file:
        json.dump(user_queries, user_queries_file, ensure_ascii=False, indent=4)


# تابع برای جستجو در دیکشنری و پیدا کردن پاراگراف‌های شامل کلمات کوئری و قرار دادن آن‌ها کنار هم
def search_in_dict(url, data, query):
    if url in data:
        paragraphs = data[url]
        combined_paragraphs = []
        combined_length = 0
        query_words = set(query.split())
        for paragraph in paragraphs:
            if any(word in paragraph for word in query_words):
                combined_paragraphs.append(paragraph.strip())
                combined_length += len(paragraph.strip())
            if combined_length >= 300:
                break
        if combined_paragraphs:
            return " ".join(combined_paragraphs) + " ."
    return None


# تابع جستجو در HTML با استفاده از Elasticsearch و دیکشنری
def search_html_query(es, index_name, query, data, size=10):
    normalized_query = normalize_text(query)
    body = {
        "query": {
            "bool": {
                "should": [
                    {
                        "match": {
                            "title": {
                                "query": normalized_query,
                                "boost": 10,  # امتیاز بیشتر برای انطباق در عنوان
                                "fuzziness": "AUTO",
                                "operator": "and",                            }
                        }
                    },
                    {
                        "multi_match": {
                            "query": normalized_query,
                            "fields": ["url^10", "body^1"],
                            "fuzziness": "AUTO",
                            "operator": "and",
                        }
                    },
                ]
            }
        },
        "size": size,
        "_source": ["url", "title", "body"],
        "highlight": {"fields": {"body": {}, "title": {}}},
        "suggest": {
            "text": query,
            "simple_phrase": {
                "phrase": {
                    "field": "body",  # اطمینان حاصل کنید که فیلد درست است
                    "size": 2,  # تعداد پیشنهادات
                    "direct_generator": [
                        {
                            "field": "body",
                            "suggest_mode": "always",
                            "min_word_length": 1,
                            "prefix_length": 1,
                        }
                    ],
                    "highlight": {"pre_tag": "<em>", "post_tag": "</em>"},
                }
            },
        },
    }

    response = es.search(index=index_name, body=body)
    seen_urls = set()
    results = []

    for hit in response["hits"]["hits"]:
        url = hit["_source"]["url"]
        if url not in seen_urls:
            seen_urls.add(url)
            snippet = search_in_dict(url, data, query)
            if not snippet:
                snippet = (
                    limit_text(
                        remove_html_tags_and_english(
                            "".join(
                                hit["highlight"].get(
                                    "body", [hit["_source"].get("body", "")[:200]]
                                )
                            )
                        )
                    )
                    if "highlight" in hit
                    else limit_text(
                        remove_html_tags_and_english(
                            hit["_source"].get("body", "")[:200]
                        )
                    )
                )
            result = {
                "url": url,
                "title": remove_html_tags_and_english(
                    hit["_source"].get("title", "No Title")
                ),
                "snippet": snippet,
                "score": hit["_score"],
            }
            results.append(result)
            if len(results) >= size:
                break
    corrections = []
    if "suggest" in response:
        for suggest in response["suggest"]["simple_phrase"]:
            for option in suggest["options"]:
                corrections.append(option["text"])
    
    return results, corrections


# تابع برای پیشنهادات بلادرنگ
def autocomplete_suggestions(query, num_suggestions=7):
    words = query.split()
    last_word = words[-1] if words else ""

    suggestions = []

    # جستجو در دیکشنری کوئری‌های کاربران
    for user_query in user_queries:
        if user_query.startswith(query) and user_query not in [
            s["suggestion"] for s in suggestions
        ]:
            suggestions.append({"type": "query", "suggestion": user_query})
            if len(suggestions) >= num_suggestions:
                break

    # جستجو در دیکشنری کلمات عنوان‌ها
    if len(suggestions) < num_suggestions:
        for word in dictionary:
            if word.startswith(last_word) and word not in [
                s["suggestion"] for s in suggestions
            ]:
                suggestions.append({"type": "word", "suggestion": word})
                if len(suggestions) >= num_suggestions:
                    break

    return suggestions


# راه‌اندازی Flask
app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def search():
    results = []
    corrections = []
    query = ""
    total_results = 0
    search_time = 0

    if request.method == "POST":
        query = request.form.get("query")
        size = int(request.form.get("size", 10))
        if not query:
            return render_template(
                "search.html",
                error="Query parameter is required",
                results=results,
                query=query,
                total_results=total_results,
                corrections=corrections,
                search_time=search_time,
            )

        start_time = time.time()
        results, corrections = search_html_query(es, index_name, query, data_dict, size)
        search_time = time.time() - start_time
        total_results = len(results)

        # به‌روزرسانی کوئری‌های کاربران در صورت نبود اصلاحات
        update_user_queries(query, corrections, results)

    return render_template(
        "search.html",
        results=results,
        query=query,
        total_results=total_results,
        corrections=corrections,
        search_time=search_time,
    )


@app.route("/autocomplete", methods=["GET"])
def autocomplete():
    query = request.args.get("query")
    if not query:
        return jsonify([])  # اگر کوئری خالی باشد، پیشنهادات خالی برگردانده شود

    suggestions = autocomplete_suggestions(query)

    formatted_suggestions = []
    for suggestion in suggestions:
        formatted_suggestions.append(
            {"suggestion": suggestion["suggestion"], "type": suggestion["type"]}
        )  # ارسال پارامترهای suggestion و type

    return jsonify(formatted_suggestions[:7])  # محدود کردن تعداد پیشنهادات به 7 عدد


@app.route("/suggest", methods=["GET"])
def suggest():
    query = request.args.get("query")
    start_time = time.time()  # ثبت زمان شروع جستجو
    size = int(request.args.get("size", 10))  # دریافت تعداد نتایج جستجو از کاربر
    results, corrections = search_html_query(es, index_name, query, data_dict, size)
    search_time = time.time() - start_time  # محاسبه زمان جستجو
    return render_template(
        "search.html",
        results=results,
        query=query,
        total_results=len(results),
        corrections=corrections,
        search_time=search_time,
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
