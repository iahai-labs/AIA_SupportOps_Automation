from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["demo-ui"])

_DEMO_INDEX = Path(__file__).resolve().parent.parent / "static" / "demo" / "index.html"


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo_page() -> HTMLResponse:
    return HTMLResponse(_DEMO_INDEX.read_text(encoding="utf-8"))
