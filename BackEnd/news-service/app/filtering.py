import re

keyword_categories = {
    "investment": [r"інвест\w*", r"акціонер\w*", r"капітал\w*"],  
    "finance": [r"фінанс\w*", r"фонд\w*"], 
    "economy": [r"економ\w*", r"ввп", r"державн\w* фінанс\w*"], 
    "banking": [r"банк\w*", r"депозит\w*"],
    "credit": [r"кредит\w*", r"іпотек\w*", r"позик\w*"],
    "currency": [r"валют\w*"],
    "budget": [r"бюджет\w*", r"дефіцит\w*", r"розподіл\w* фінанс\w*"],
    "business": [r"бізнес\w*", r"стартап\w*"],
    "profit": [r"прибут\w*", r"дохід\w*", r"маржа\w*"],
    "tax": [r"подат\w*", r"оподаткуван\w*", r"акциз\w*", r"мито\w*"],
    "market": [r"ринок\w*", r"конкуренц\w*", r"продаж\w*"],
    "stocks": [r"акці\w*", r"бірж\w*", r"цінн\w* папер\w*"],
    "trade": [r"торгів\w*", r"експорт\w*", r"імпорт\w*", r"митниц\w*"],
    "inflation": [r"інфляц\w*", r"знецін\w*", r"індекс цін\w*"],
    "technologies": [r"криптовалют\w*", r"новітн\w*"]
}

# Compile regex for each category
compiled_patterns = {
    category: re.compile(r"\b(" + "|".join(words) + r")\b", re.IGNORECASE | re.UNICODE)
    for category, words in keyword_categories.items()
}

def is_business_news(article_text: str, article_title: str) -> bool:
    """Checks if an article contains at least TWO distinct business-related keyword categories."""
    matched_categories = set()

    for category, pattern in compiled_patterns.items():
        if pattern.search(article_text) or pattern.search(article_title):
            matched_categories.add(category)  # Add the matched category

        if len(matched_categories) >= 2:  # Stop early if 2 distinct categories found
            return True

    return False  # Not enough distinct categories found
