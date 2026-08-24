import json
import re

import requests

from config import GROQ_API_KEY, GROQ_MODEL


def _prompt(articles: list[dict], theme: str, politician: str) -> str:
    context = "\n\n".join(
        f"[ARTIGO {index}] Site: {article['site']}\nTitulo: {article['title']}\nResumo: {article['summary']}"
        for index, article in enumerate(articles)
    )
    return f"""Voce e um verificador de promessas politicas. Analise somente os artigos abaixo sobre {politician} e o tema '{theme}'.
{context}

Nao invente promessas, fatos ou fontes. So inclua uma promessa se ela estiver explicitamente mencionada. Se nao houver evidencia suficiente, use 'nao verificada'. Para cada item, informe fonte_artigo_id usando apenas um numero dos artigos fornecidos.
Responda somente JSON valido neste formato:
{{"promessas":[{{"promessa":"...","area":"...","status":"cumprida|parcialmente cumprida|nao cumprida|em andamento|nao verificada","explicacao":"...","fonte_artigo_id":0}}],"resumo_geral":"..."}}"""


def verify_promises(articles: list[dict], theme: str, politician: str) -> dict:
    if not GROQ_API_KEY:
        return {"error": "GROQ_API_KEY nao configurada no ambiente."}
    if not articles:
        return {"error": "Nenhuma noticia encontrada para esta busca."}
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "user", "content": _prompt(articles[:12], theme, politician)}],
                "max_tokens": 3000,
                "temperature": 0.1,
            },
            timeout=45,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        match = re.search(r"\{[\s\S]*\}", re.sub(r"```json|```", "", raw))
        if not match:
            return {"error": "A IA nao retornou JSON valido."}
        parsed = json.loads(match.group())
    except requests.RequestException as error:
        return {"error": f"Falha de conexao com a IA: {error}"}
    except (KeyError, ValueError, json.JSONDecodeError) as error:
        return {"error": f"Resposta invalida da IA: {error}"}

    promises = []
    for promise in parsed.get("promessas", []):
        source_id = promise.get("fonte_artigo_id")
        source = articles[source_id] if isinstance(source_id, int) and 0 <= source_id < len(articles) else None
        if source is None:
            promise["status"] = "nao verificada"
        promise["fonte"] = source or {}
        promise.pop("fonte_artigo_id", None)
        promises.append(promise)
    parsed["promessas"] = promises
    parsed["total_artigos_analisados"] = len(articles)
    parsed["sites_consultados"] = sorted({article["site"] for article in articles})
    return parsed


def assess_promise(articles: list[dict], promise: str, politician: str) -> dict:
    """Avalia uma promessa do G1 usando somente evidencias recuperadas."""
    if not GROQ_API_KEY:
        return {"error": "GROQ_API_KEY nao configurada no ambiente."}
    if not articles:
        return {"status": "nao verificada", "explicacao": "Nenhuma evidencia recente foi encontrada."}
    context = "\n\n".join(
        f"[ARTIGO {index}] {article['site']} | {article['title']}\n{article['summary']}"
        for index, article in enumerate(articles[:12])
    )
    prompt = f"""Avalie a promessa oficial abaixo para {politician} usando apenas os artigos recuperados.
PROMESSA: {promise}
{context}
Considere uma fonte mais confiavel quando houver concordancia entre veículos independentes. Não trate ausência de notícia como cumprimento. Não invente fatos. Se a evidência for insuficiente ou contraditória, use nao verificada.
Retorne somente JSON: {{"status":"cumprida|parcialmente cumprida|nao cumprida|em andamento|nao verificada","explicacao":"..."}}.
"""
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 800, "temperature": 0.1},
            timeout=45,
        )
        response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        match = re.search(r"\{[\s\S]*\}", re.sub(r"```json|```", "", raw))
        return json.loads(match.group()) if match else {"status": "nao verificada", "explicacao": "Resposta sem formato valido."}
    except (requests.RequestException, KeyError, ValueError, json.JSONDecodeError) as error:
        return {"error": str(error)}
