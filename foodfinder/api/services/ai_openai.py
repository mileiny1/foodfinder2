import os 
import json 
import requests
from typing import List, Dict, Optional


OPENAI_URL = "https://api.openai.com/v1/responses"


class SearchProviderError(Exception):
    def __init__(self, message: str, code: str = "search_provider_error", status_code: int = 503):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code


def _mock_fallback_enabled() -> bool:
    return os.getenv("ENABLE_MOCK_SEARCH_FALLBACK", "1").strip().lower() in {"1", "true", "yes", "on"}


def _build_mock_restaurants(
    lat: float,
    lng: float,
    term: str,
    limit: int,
    open_now: Optional[bool],
    price_range: Optional[str],
) -> List[Dict]:
    query = (term or "food").strip() or "food"
    names = [
        f"{query.title()} Corner",
        f"Golden {query.title()} Kitchen",
        f"{query.title()} House",
        f"Urban {query.title()} Spot",
        f"{query.title()} Garden",
    ]
    offsets = [
        (0.0042, 0.0011),
        (0.0026, -0.0017),
        (-0.0031, 0.0024),
        (-0.0014, -0.0032),
        (0.0019, 0.0036),
    ]
    ratings = [4.6, 4.4, 4.3, 4.5, 4.2]
    prices = [1, 2, 2, 3, 1]
    normalized_price = None
    if price_range:
        try:
            normalized_price = int(str(price_range).split(",")[0])
        except (TypeError, ValueError):
            normalized_price = None

    mock_results = []
    for idx, (name, (lat_offset, lng_offset)) in enumerate(zip(names, offsets), start=1):
        mock_results.append({
            "name": name,
            "address": f"{100 + idx} Market St, San Francisco, CA",
            "lat": round(lat + lat_offset, 6),
            "lng": round(lng + lng_offset, 6),
            "distance_m": None,
            "rating": ratings[idx - 1],
            "price_level": normalized_price or prices[idx - 1],
            "is_open_now": True if open_now is not False else False,
            "provider_place_id": f"mock-{query.lower().replace(' ', '-')}-{idx}",
            "provider": "mock",
        })
    return mock_results[:max(limit, 1)]


def _fallback_or_raise(
    message: str,
    code: str,
    status_code: int,
    lat: float,
    lng: float,
    term: str,
    limit: int,
    open_now: Optional[bool],
    price_range: Optional[str],
) -> List[Dict]:
    if _mock_fallback_enabled():
        return _build_mock_restaurants(
            lat=lat,
            lng=lng,
            term=term,
            limit=limit,
            open_now=open_now,
            price_range=price_range,
        )
    raise SearchProviderError(message=message, code=code, status_code=status_code)

def expand_food_query(query: str) -> List[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    if not api_key:
        return _fallback_terms(query)
    system = (
        "You expand a user's food craving into short, keyword phrases suitable for restaurant search APIs."
        " Return ONLY JSON with this shape {\"terms\": [\"...\", ...]}."
        " Max 6 terms. No extra keys."
    )
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Food query: {query}"}
        ],
        "text": {"format": {"type": "json_object"}}
    }

    try:
        r = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",  # fix: capital T
            },
            json=payload,
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        return _fallback_terms(query)  # fix: handle timeout gracefully
    except requests.exceptions.HTTPError as e:
        return _fallback_terms(query)  # fix: handle 4xx/5xx gracefully
    except Exception:
        return _fallback_terms(query)  # fix: catch all other errors

    text_parts = []
    for item in data.get("output", []):
        if item.get("type") == "message":
            for c in item.get("content", []):
                if c.get("type") == "output_text":
                    text_parts.append(c.get("text", ""))

    joined = " ".join(text_parts).strip()
    if not joined:
        return _fallback_terms(query)

    try:
        obj = json.loads(joined)
        terms = obj.get("terms", [])
        return _clean_terms(query, terms)
    except Exception:
        return _fallback_terms(query)


def _fallback_terms(query: str) -> List[str]:
    q = query.strip()
    base = [q, f"{q} restaurant", f"best {q}", f"{q} near me"]  # fix: more useful fallback terms
    return list(dict.fromkeys([t for t in base if t]))


def _clean_terms(original: str, terms: List[str]) -> List[str]:
    cleaned = []
    for t in (terms or [])[:6]:
        t = (t or "").strip()
        if t:
            cleaned.append(t)
    if not cleaned:
        return _fallback_terms(original)
    return list(dict.fromkeys(cleaned))


def search_restaurants_openai(
    lat: float,
    lng: float,
    term: str,
    radius_m: int,
    open_now: Optional[bool],
    price_range: Optional[str],
    limit: int,
) -> List[Dict]:
    """Search for restaurants using OpenAI based on location and search term."""
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    
    if not api_key:
        return _fallback_or_raise(
            message="OpenAI API key is missing. Set OPENAI_API_KEY or enable mock fallback.",
            code="openai_api_key_missing",
            status_code=503,
            lat=lat,
            lng=lng,
            term=term,
            limit=limit,
            open_now=open_now,
            price_range=price_range,
        )
    
    # Build the prompt for OpenAI
    filters_desc = []
    if radius_m:
        filters_desc.append(f"within {radius_m}m radius")
    if isinstance(open_now, bool):
        filters_desc.append("open now" if open_now else "may be closed")
    if price_range:
        filters_desc.append(f"price range: {price_range}")
    
    filters_str = ", ".join(filters_desc) if filters_desc else "no specific filters"
    
    system = (
        "You are a restaurant recommendation AI. Given a location and search criteria, "
        "recommend realistic restaurants that match the search term. "
        "Return ONLY valid JSON with this exact shape: "
        '{\"restaurants\": [{"name": "...", "address": "...", "lat": 0.0, "lng": 0.0, "rating": 4.5, "price_level": 2, "is_open_now": true, "provider_place_id": "..."}, ...]}'
        "Return between 5-15 restaurants. No additional keys or explanation."
    )
    
    user_prompt = (
        f"Find restaurants for '{term}' near coordinates ({lat}, {lng}). "
        f"Filters: {filters_str}. "
        f"Return {limit} results."
    )
    
    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": user_prompt},
        ],
        "text": {"format": {"type": "json_object"}},
    }
    
    try:
        r = requests.post(
            OPENAI_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=20,
        )
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.Timeout:
        return _fallback_or_raise(
            message="OpenAI request timed out while searching for restaurants.",
            code="openai_timeout",
            status_code=504,
            lat=lat,
            lng=lng,
            term=term,
            limit=limit,
            open_now=open_now,
            price_range=price_range,
        )
    except requests.exceptions.HTTPError as exc:
        response = exc.response
        status_code = response.status_code if response is not None else 503
        message = "OpenAI request failed while searching for restaurants."
        code = "openai_http_error"
        if response is not None:
            try:
                payload = response.json()
                error = payload.get("error", {})
                message = error.get("message") or message
                code = error.get("code") or code
            except ValueError:
                message = response.text or message
        return _fallback_or_raise(
            message=message,
            code=code,
            status_code=status_code,
            lat=lat,
            lng=lng,
            term=term,
            limit=limit,
            open_now=open_now,
            price_range=price_range,
        )
    except requests.exceptions.RequestException:
        return _fallback_or_raise(
            message="OpenAI could not be reached for restaurant search.",
            code="openai_connection_error",
            status_code=503,
            lat=lat,
            lng=lng,
            term=term,
            limit=limit,
            open_now=open_now,
            price_range=price_range,
        )
    
    try:
        text_parts = []
        for item in data.get("output", []):
            if item.get("type") == "message":
                for c in item.get("content", []):
                    if c.get("type") == "output_text":
                        text_parts.append(c.get("text", ""))

        content = " ".join(text_parts).strip()
        if not content:
            return _fallback_or_raise(
                message="OpenAI returned an empty restaurant response.",
                code="openai_empty_response",
                status_code=502,
                lat=lat,
                lng=lng,
                term=term,
                limit=limit,
                open_now=open_now,
                price_range=price_range,
            )
        
        result = json.loads(content)
        restaurants = result.get("restaurants", [])
        if not restaurants:
            return _fallback_or_raise(
                message="OpenAI returned no restaurants for this search.",
                code="openai_no_results",
                status_code=502,
                lat=lat,
                lng=lng,
                term=term,
                limit=limit,
                open_now=open_now,
                price_range=price_range,
            )
        
        # Normalize the data to match expected format
        normalized = []
        for r in restaurants[:limit]:
            normalized.append({
                "name": r.get("name", ""),
                "address": r.get("address", ""),
                "lat": r.get("lat"),
                "lng": r.get("lng"),
                "distance_m": None,
                "rating": r.get("rating"),
                "price_level": r.get("price_level"),
                "is_open_now": r.get("is_open_now"),
                "provider_place_id": r.get("provider_place_id", ""),
                "provider": "openai"
            })
        
        return normalized
    except (TypeError, ValueError, json.JSONDecodeError):
        return _fallback_or_raise(
            message="OpenAI returned an invalid restaurant payload.",
            code="openai_invalid_payload",
            status_code=502,
            lat=lat,
            lng=lng,
            term=term,
            limit=limit,
            open_now=open_now,
            price_range=price_range,
        )


            

                    







                    
                                                                         

        

            
        



    
    



                
                


   

    
    
 
