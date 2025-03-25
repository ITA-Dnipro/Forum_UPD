from typing import Optional, List, Dict, Any

from elasticsearch_dsl import AsyncSearch, Q
from fastapi import HTTPException

from ..config import logger


async def build_search_query(
        es_client,
        index_name: str,
        query: Optional[str],
        filters: List[Q],
        sort_by: Optional[str],
        search_fields: List[str],
        sort_order: str,
        page: int,
        page_size: int,
        include_suggestions: bool,
        suggest_filed: str
) -> (int, List[Dict[str, Any]]):
    """
    Build and execute an Elasticsearch DSL search query with pagination.
    """
    s = AsyncSearch(using=es_client, index=index_name)
    if query:
        if len(search_fields) == 1:
            field = search_fields[0]
            s = s.query("match", **{field: {"query": query, "fuzziness": "AUTO"}})
        else:
            s = s.query("multi_match", query=query, fields=search_fields, fuzziness="AUTO")

        if include_suggestions:
            s = s.suggest("suggestions", query, term={"field": suggest_filed})
    else:
        s = s.query("match_all")
    if filters:
        s = s.filter("bool", filter=filters)
    s = s.sort({sort_by: {"order": sort_order}})

    offset = (page - 1) * page_size
    s = s.extra(from_=offset, size=page_size)

    try:
        response = await s.execute()
        total_records = response.hits.total.value
        records = [hit.to_dict() for hit in response]
    except Exception as e:
        logger.error(f"Elasticsearch query error for {index_name}: {e}")
        raise HTTPException(status_code=500, detail="Search failed")
    return total_records, records, response


async def generic_search(
        es_client,
        index_name: str,
        query: Optional[str],
        filters: List[Q],
        sort_by: str,
        search_fields: List[str],
        sort_order: str,
        page: int,
        page_size: int,
        include_suggestions: bool,
        suggest_filed: str
):
    """
    Generic search helper that wraps build_search_query.
    """
    return await build_search_query(
        es_client=es_client,
        index_name=index_name,
        query=query,
        filters=filters,
        sort_by=sort_by,
        search_fields=search_fields,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
        include_suggestions=include_suggestions,
        suggest_filed=suggest_filed
    )
