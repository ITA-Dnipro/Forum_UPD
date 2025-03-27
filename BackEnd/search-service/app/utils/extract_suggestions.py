def extract_suggestions(response):
    """
    Extracts suggestions from an Elasticsearch response object.
    Returns a dictionary where each suggestion key maps to a list of suggestion texts.
    """
    suggestions = {}
    if hasattr(response, "suggest") and response.suggest:
        for s_id, suggestion_list in response.suggest.items():
            texts = []
            for suggestion in suggestion_list:
                if "options" in suggestion and suggestion["options"]:
                    texts.extend([option["text"] for option in suggestion["options"]])
            if texts:
                suggestions[s_id] = texts
    return suggestions
