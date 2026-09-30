import httpx
from .config import settings
from .services import get_import_set, stats

SYSTEM = """You are an enterprise data-import assistant. Explain Import Sets, Transform Maps, coalesce, and data-quality results clearly. Do not invent records or counts. Use only the supplied project data. If asked for an action that would modify data, describe the action rather than claiming it was performed."""

def local_answer(question, import_set_id=None):
    s = stats()
    context = get_import_set(import_set_id) if import_set_id else None
    if context:
        latest = context["rows"]
        inserted=sum(r["status"]=="Inserted" for r in latest)
        updated=sum(r["status"]=="Updated" for r in latest)
        ignored=sum(r["status"]=="Ignored" for r in latest)
        errors=sum(r["status"]=="Error" for r in latest)
        return (f"Import Set {context['id']} contains {context['row_count']} rows. "
                f"Current transformation result: {inserted} inserted, {updated} updated, {ignored} ignored, {errors} errors. "
                f"The project uses Employee ID as the coalesce key, so an existing Employee ID is updated rather than duplicated. "
                f"The current target contains {s['total_employees']} employee records.")
    return (f"The target Employee Test dataset currently contains {s['total_employees']} records. "
            f"Across completed transformations: {s['inserted']} inserted, {s['updated']} updated, {s['ignored']} ignored, and {s['errors']} errors. "
            "The local implementation uses Employee ID as the coalesce key.")

async def answer(question, import_set_id=None):
    local = local_answer(question, import_set_id)
    if not settings.gemini_api_key:
        return {"provider":"local-fallback","answer":local}
    payload={"contents":[{"parts":[{"text":SYSTEM+"\n\nProject facts:\n"+local+"\n\nQuestion:\n"+question}]}]}
    url=f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp=await client.post(url, params={"key":settings.gemini_api_key}, json=payload)
            resp.raise_for_status()
            data=resp.json()
            text=data["candidates"][0]["content"]["parts"][0]["text"]
            return {"provider":"gemini","answer":text}
    except Exception as exc:
        return {"provider":"local-fallback","answer":local,"warning":f"LLM unavailable; fallback used: {type(exc).__name__}"}
