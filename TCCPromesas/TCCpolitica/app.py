from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify, render_template, request
from sqlalchemy import or_

from config import ALL_POLITICIANS, DATABASE_URL, G1_PROMISES_URL, GROQ_API_KEY, MAPC_NAME, POLITICIANS, SYNC_INTERVAL_HOURS, TEMAS_PROMESSAS
from db import Assessment, Politician, Promise, db
from services.sync import check_active_promises, check_selected_promises, sync_g1_promises

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


def serialize_promise(promise):
    return {
        "id": promise.id,
        "promessa": promise.promise,
        "resumo": promise.summary,
        "area": promise.theme,
        "status": promise.current_status,
        "explicacao": promise.current_explanation,
        "fonte": {"url": promise.source_url, "title": "Fonte oficial da promessa", "site": "Fonte pública"},
        "ultima_verificacao": promise.last_checked_at.isoformat() if promise.last_checked_at else None,
    }


with app.app_context():
    db.create_all()


def scheduled_update():
    with app.app_context():
        try:
            sync_g1_promises()
            check_active_promises()
        except Exception as error:
            app.logger.error("Falha na atualização automática: %s", error)


scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(scheduled_update, "interval", hours=SYNC_INTERVAL_HOURS, id="mapc-update", replace_existing=True)
scheduler.start()


@app.get("/")
def landing():
    return render_template("index.html", source_url=G1_PROMISES_URL, project_name=MAPC_NAME)


@app.get("/promessas")
def promises_app():
    catalog = {category: list(items) for category, items in POLITICIANS.items()}
    stored = Politician.query.order_by(Politician.name).all()
    if stored:
        catalog["prefeitos"] = [
            {"id": item.id.removeprefix("g1-"), "historico": True, "nome": item.name, "cargo": item.office, "partido": item.party, "uf": item.state, "desde": item.started_at}
            for item in stored
        ]
    catalog_count = sum(len(items) for items in catalog.values())
    return render_template(
        "app.html",
        politicians=catalog,
        politicians_count=catalog_count,
        themes=TEMAS_PROMESSAS,
        has_api_key=bool(GROQ_API_KEY),
        source_url=G1_PROMISES_URL,
        project_name=MAPC_NAME,
    )


@app.post("/api/search")
def search():
    body = request.get_json(silent=True) or {}
    theme = str(body.get("query", "")).strip()
    politician_name = str(body.get("politician", "")).strip()
    if not theme or not politician_name:
        return jsonify({"error": "Informe o politico e o tema da busca."}), 400
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY nao configurada no ambiente."}), 503

    politician_record = Politician.query.filter(Politician.name.ilike(f"%{politician_name}%")).first()
    if not politician_record:
        return jsonify({"error": "Este político ainda não possui promessas oficiais importadas."}), 404

    promises = Promise.query.filter_by(politician_id=politician_record.id).filter(
        or_(Promise.theme.ilike(f"%{theme}%"), Promise.promise.ilike(f"%{theme}%"))
    ).all()
    if not promises:
        return jsonify({"error": "Nenhuma promessa oficial encontrada nesta categoria."}), 404

    checked = check_selected_promises(promises)
    return jsonify({
        "promessas": [serialize_promise(item) for item in checked or promises],
        "resumo_geral": f"Promessas oficiais avaliadas por evidências recentes na categoria {theme}.",
        "total_artigos_analisados": sum(len(item.assessments[-1].articles) for item in checked if item.assessments),
        "sites_consultados": sorted({article.site for item in checked for assessment in item.assessments[-1:] for article in assessment.articles if article.site}),
    })


@app.get("/historico/<politician_id>")
def history_page(politician_id):
    politician = db.session.get(Politician, politician_id) or db.session.get(Politician, f"g1-{politician_id}")
    if not politician:
        return "Politico nao encontrado", 404
    return render_template("history.html", politician=politician, project_name=MAPC_NAME)


@app.get("/api/politicians/<politician_id>/promises")
def politician_promises(politician_id):
    politician = db.session.get(Politician, politician_id) or db.session.get(Politician, f"g1-{politician_id}")
    if not politician:
        return jsonify({"error": "Politico nao encontrado"}), 404
    return jsonify({"politico": politician.name, "promessas": [serialize_promise(item) for item in politician.promises]})


@app.get("/api/politicians/<politician_id>/history")
def politician_history(politician_id):
    politician = db.session.get(Politician, politician_id) or db.session.get(Politician, f"g1-{politician_id}")
    if not politician:
        return jsonify({"error": "Politico nao encontrado"}), 404
    history = []
    for promise in politician.promises:
        history.append({
            **serialize_promise(promise),
            "historico": [
                {"status": item.status, "explicacao": item.explanation, "data": item.created_at.isoformat()}
                for item in sorted(promise.assessments, key=lambda item: item.created_at)
            ],
        })
    return jsonify({"politico": politician.name, "promessas": history})


@app.post("/api/sync")
def sync_now():
    try:
        profiles = sync_g1_promises()
        checked = check_active_promises()
        return jsonify({"ok": True, "perfis_importados": profiles, "promessas_verificadas": checked})
    except Exception as error:
        app.logger.exception("Falha na sincronização")
        return jsonify({"error": str(error)}), 502


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "ia_configurada": bool(GROQ_API_KEY), "banco": DATABASE_URL.split(":", 1)[0], "intervalo_horas": SYNC_INTERVAL_HOURS})


if __name__ == "__main__":
    print("MAPC: http://localhost:5000")
    app.run(debug=True, use_reloader=False, port=5000)
