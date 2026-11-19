import sys, time
sys.path.insert(0, r"D:\TCC")
import app

pol = app.get_politico(politico_id=1)
print("politico:", pol["nome"])
with app._tokens_lock:
    app._tokens_run = 0
t = time.time()
coletados = app.scrape_all(pol)
print("coletados:", len(coletados), f"em {time.time()-t:.0f}s", flush=True)
known_urls, known_titles = app.get_known_articles(1)
novos = [a for a in coletados if a["url"] not in known_urls and app.norm_titulo(a["title"]) not in known_titles]
print("novos:", len(novos))
app.save_articles(1, novos)
app.AI_MAX_PER_RUN = 80
app.AI_BATCH_SIZE = 25
pend = app.preparar_pendentes(pol, app.get_pending_articles(1, 80))
print("pendentes preparados:", len(pend))
if pend:
    app.enrich_pending(pend)
    r = app.analisar_pendentes(pol, pend)
    print("análise:", r, flush=True)
    try:
        app.manutencao_promessas(pol)
    except Exception as e:
        print("manutenção erro:", e)
try:
    app.validar_promessas(pol)
except Exception as e:
    print("validação erro:", e)
with app._tokens_lock:
    print("tokens:", app._tokens_run)
con = app.get_db_connection()
print("total promessas Lula:", con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=1").fetchone()["c"])
print("sem imagem:", con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=1 AND img_status IS NULL").fetchone()["c"])
con.close()
# imagens específicas para as novas
app.NEWS_IMG_PER_RUN = 6
for rodada in range(1, 5):
    n = app.gerar_imagens_promessas(pol, limite=40)
    print("imagens rodada", rodada, ":", n, flush=True)
    if not n:
        break
con = app.get_db_connection()
print("sem imagem final:", con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=1 AND img_status IS NULL").fetchone()["c"])
con.close()
