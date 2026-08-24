from datetime import datetime, timezone

from config import GROQ_API_KEY
from db import Assessment, AssessmentArticle, Politician, Promise, db
from services.ai import assess_promise
from services.g1 import fetch_current_profiles, fetch_promises, split_profile_name
from services.news import retrieve_evidence


def sync_g1_promises():
    """Importa somente a edição atual do G1 e preserva o histórico local."""
    profiles = fetch_current_profiles()
    for profile in profiles:
        name, party = split_profile_name(profile["name"])
        city, state = (profile["city"].rsplit("(", 1) + [""])[:2] if "(" in profile["city"] else (profile["city"], "")
        state = state.replace(")", "").strip()
        politician_id = "g1-" + profile["url"].rstrip("/").split("/")[-1]
        politician = db.session.get(Politician, politician_id) or Politician(id=politician_id)
        politician.name = name
        politician.category = "prefeitos"
        politician.office = "Prefeito"
        politician.party = party
        politician.state = state
        politician.started_at = "2025"
        politician.source_url = profile["url"]
        db.session.add(politician)
        for item in fetch_promises(profile["url"]):
            promise = Promise.query.filter_by(politician_id=politician_id, source_id=item["source_id"]).first()
            if not promise:
                promise = Promise(politician_id=politician_id, source_id=item["source_id"])
            promise.promise = item["promise"]
            promise.summary = item["summary"]
            promise.theme = item["theme"]
            promise.source_url = item["source_url"]
            promise.g1_status = item["g1_status"]
            if not promise.current_status:
                promise.current_status = "nao verificada"
            db.session.add(promise)
    db.session.commit()
    return len(profiles)


def check_active_promises(limit: int = 100):
    if not GROQ_API_KEY:
        return 0
    checked = 0
    promises = Promise.query.filter(Promise.current_status != "cumprida").limit(limit).all()
    for promise in promises:
        politician = promise.politician
        articles = retrieve_evidence(promise.promise, politician.name)
        result = assess_promise(articles, promise.promise, politician.name)
        if result.get("error"):
            continue
        assessment = Assessment(
            promise_id=promise.id,
            status=result.get("status", "nao verificada"),
            explanation=result.get("explicacao", ""),
        )
        db.session.add(assessment)
        for article in articles:
            db.session.add(AssessmentArticle(
                assessment=assessment,
                title=article["title"], url=article["url"], site=article.get("site"), summary=article.get("summary"),
            ))
        promise.current_status = assessment.status
        promise.current_explanation = assessment.explanation
        promise.last_checked_at = datetime.now(timezone.utc)
        checked += 1
    db.session.commit()
    return checked


def check_selected_promises(promises):
    checked = []
    for promise in promises:
        politician = promise.politician
        articles = retrieve_evidence(promise.promise, politician.name)
        result = assess_promise(articles, promise.promise, politician.name)
        if result.get("error"):
            continue
        assessment = Assessment(
            promise_id=promise.id,
            status=result.get("status", "nao verificada"),
            explanation=result.get("explicacao", ""),
        )
        db.session.add(assessment)
        for article in articles:
            db.session.add(AssessmentArticle(
                assessment=assessment,
                title=article["title"], url=article["url"], site=article.get("site"), summary=article.get("summary"),
            ))
        promise.current_status = assessment.status
        promise.current_explanation = assessment.explanation
        promise.last_checked_at = datetime.now(timezone.utc)
        checked.append(promise)
    db.session.commit()
    return checked
