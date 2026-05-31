from typing import List, Dict, Optional
from .ai_openai import search_restaurants_openai


def search_places(
    lat: float,
    lng: float,
    term: str,
    radius_m: int,
    open_now: Optional[bool],
    price_range: Optional[str],
    limit: int,
) -> List[Dict]:
    return search_restaurants_openai(
        lat=lat,
        lng=lng,
        term=term,
        radius_m=radius_m,
        open_now=open_now,
        price_range=price_range,
        limit=limit,
    )