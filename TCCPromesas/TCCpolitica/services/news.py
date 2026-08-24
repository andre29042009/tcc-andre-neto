import re
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "PromessasPoliticas/1.0 (projeto academico; contato local)",
    "Accept-Language": "pt-BR,pt;q=0.9",
}

TRUSTED_SOURCES = {
    "g1", "agência brasil", "agencia brasil", "folha", "estadao", "estadão",
    "valor", "cnn brasil", "bbc brasil", "uol", "metrópoles", "metropoles",
}


def scrape_google_news(query: str, max_results: int = 12) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={quote(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-BR"
    results = []
    try:
        response = requests.get(url, headers=HEADERS, timeout=12)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")
        for item in soup.find_all("item")[:max_results]:
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            source = item.find("source")
            if not title or not link:
                continue
            summary = BeautifulSoup(
                description.get_text(strip=True) if description else "", "html.parser"
            ).get_text(strip=True)[:400]
            results.append({
                "title": title.get_text(strip=True),
                "url": link.get_text(strip=True),
                "summary": summary,
                "site": source.get_text(strip=True) if source else "Google Noticias",
            })
    except requests.RequestException as error:
        print(f"[Google Noticias] {error}")
    return results


def _source_score(article: dict) -> int:
    source = article.get("site", "").lower()
    return 2 if any(known in source for known in TRUSTED_SOURCES) else 1


def retrieve_evidence(promise: str, politician: str, max_results: int = 18) -> list[dict]:
    """Recupera evidências em várias consultas e prioriza fontes identificáveis."""
    queries = [
        f'"{promise}" "{politician}"',
        f'{politician} cumprimento promessa {promise}',
        f'{politician} obra programa medida {promise}',
    ]
    articles = []
    for query in queries:
        articles.extend(scrape_google_news(query, max_results=8))
    unique = []
    seen = set()
    for article in articles:
        if article["url"] not in seen:
            seen.add(article["url"])
            unique.append(article)
    return sorted(unique, key=_source_score, reverse=True)[:max_results]


def scrape_all(query: str) -> list[dict]:
    """Compatibilidade com chamadas antigas; novas checagens usam retrieve_evidence."""
    return scrape_google_news(query)
