import json
import re
from urllib.parse import urljoin

import requests

from config import G1_PROMISES_URL

G1_INDEX_SCRIPT = "https://s3.glbimg.com/v1/AUTH_8b29beb0cbe247a296f902be2fe084b6/2025/html/politica/promessas/script.js"
HEADERS = {"User-Agent": "MAPC/1.0 (projeto academico)", "Accept-Language": "pt-BR,pt;q=0.9"}


def _array_from_script(script: str, variable: str) -> list[dict]:
    match = re.search(rf"const {variable}\s*=\s*(\[[\s\S]*?\]);", script)
    if not match:
        return []
    # O arquivo do G1 usa arrays JSON válidos.
    return json.loads(match.group(1))


def fetch_current_profiles() -> list[dict]:
    response = requests.get(G1_INDEX_SCRIPT, headers=HEADERS, timeout=20)
    response.raise_for_status()
    script = response.content.decode("utf-8", errors="replace")
    profiles = _array_from_script(script, "data2025_2028")
    current = []
    for profile in profiles:
        page_url = profile.get("pÃ¡gina") or profile.get("página")
        if not page_url:
            continue
        current.append({
            "city": profile.get("Cidade", ""),
            "name": profile.get("nome", ""),
            "url": page_url.rstrip("/") + "/",
            "photo": profile.get("foto", ""),
        })
    return current


def fetch_promises(profile_url: str) -> list[dict]:
    page = requests.get(profile_url, headers=HEADERS, timeout=20)
    page.raise_for_status()
    html = page.text
    script_match = re.search(r'<script[^>]+src="([^"]+/sectionconfig\.js)"', html)
    if not script_match:
        return []
    config_url = urljoin(profile_url, script_match.group(1))
    config = requests.get(config_url, headers=HEADERS, timeout=20).text
    json_match = re.search(r"return '([^']+\.json)';", config)
    if not json_match:
        return []
    json_url = urljoin(config_url, json_match.group(1))
    data = requests.get(json_url, headers=HEADERS, timeout=20).json()
    return [{
        "source_id": str(item.get("id", index)),
        "promise": item.get("promessa", "").strip(),
        "summary": item.get("resumo", "").strip(),
        "theme": item.get("tema") or item.get("categoria") or "Geral",
        "source_url": item.get("linkPromessa") or profile_url,
        "g1_status": item.get("status", "nao-avaliada"),
    } for index, item in enumerate(data) if item.get("promessa")]


def split_profile_name(value: str) -> tuple[str, str]:
    match = re.match(r"(.+?)\s*\(([^)]+)\)", value.strip())
    return (match.group(1).strip(), match.group(2).strip()) if match else (value.strip(), "")
