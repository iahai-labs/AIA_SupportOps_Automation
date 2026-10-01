from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["demo-ui"])

_DEMO_INDEX = Path(__file__).resolve().parent.parent / "static" / "demo" / "index.html"


@router.get("/demo", response_class=HTMLResponse, include_in_schema=False)
def demo_page(request: Request) -> HTMLResponse:
    html = _DEMO_INDEX.read_text(encoding="utf-8")
    root_path = request.scope.get("root_path", "").rstrip("/")
    html = html.replace("__APP_BASE__", root_path)
    return HTMLResponse(html)
