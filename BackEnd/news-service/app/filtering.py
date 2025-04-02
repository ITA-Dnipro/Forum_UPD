import re

keyword_categories = {
    "investment": [r"інвест\w*", r"акціонер\w*", r"капітал\w*", r"актив\w*"],  
    "finance": [r"фінанс\w*", r"фонд\w*", r"грош\w*"], 
    "economy": [r"економ\w*", r"ввп", r"державне фінансування", r"економічн\w* розвит\w*", r"зростання цін\w*"], 
    "banking": [r"банк\w*", r"депозит\w*", r"регулятор\w*"],
    "credit": [r"кредит\w*", r"іпотек\w*", r"позик\w*", r"борг\w*", r"заборгованіст\w*"],
    "currency": [r"валют\w*", r"обмінний курс*", r"девальвац\w*", r"ревальвац\w*"],
    "budget": [r"бюджет\w*", r"дефіцит\w*", r"розподіл\w* фінанс\w*"],
    "business": [r"бізнес\w*", r"стартап\w*", r"корпорац\w*", r"партнерств\w*"],
    "profit": [r"прибут\w*", r"дохід\w*", r"маржа\w*", r"рентабельн\w*"],
    "tax": [r"податк\w*", r"оподаткуван\w*", r"акциз\w*", r"мито\w*"],
    "market": [r"ринок\w*", r"конкуренц\w*", r"продаж\w*", r"монопол\w*"],
    "stocks": [r"акці\w*", r"бірж\w*", r"цінн\w* папер\w*", r"облігац\w*", r"фондовий ринок"],
    "trade": [r"торгів\w*", r"експорт\w*", r"імпорт\w*", r"митниц\w*", r"товар\w*"],
    "inflation": [r"інфляц\w*", r"знецін\w*", r"індекс цін\w*"],
    "technologies": [r"криптовалют\w*", r"новітн\w*", r"штучний інтелект", r"блокчейн\w*"]
}

compiled_patterns = {
    category: re.compile(r"\b(" + "|".join(words) + r")\b", re.IGNORECASE | re.UNICODE)
    for category, words in keyword_categories.items()
}

def get_business_news_categories(article_text: str, article_title: str) -> set:
    return {
        category for category, pattern in compiled_patterns.items()
        if pattern.search(article_text) or pattern.search(article_title)
    }

def is_business_news(article_text: str, article_title: str, min_categories: int = 3) -> bool:
    return len(get_business_news_categories(article_text, article_title)) >= min_categories