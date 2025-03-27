def extract_suggestions(response):
    """
    Extract suggestions from an Elasticsearch response object.
    Returns a list of suggestion texts if available, otherwise an empty list.
    """
    suggestions = []
    if hasattr(response, "suggest") and response.suggest:
        suggestion_list = response.suggest.suggestions
        if suggestion_list and suggestion_list[0].options:
            suggestions = [option.text for option in suggestion_list[0].options]
    return suggestions
