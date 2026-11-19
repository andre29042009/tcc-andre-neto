import sys, time, traceback
sys.path.insert(0, r"D:\TCC")
import app

LOG = r"D:\TCC\popular_todos_v2.log"

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {msg}\n")
    print(msg, flush=True)

def preencher_genericas(pid):
    con = app.get_db_connection()
    pend = [dict(r) for r in con.execute("""SELECT p.id_promessa, t.nome AS tema
                                            FROM promessas p JOIN temas t ON t.id_tema=p.id_tema
                                            WHERE p.id_politico=? AND p.img_status IS NULL""", (pid,))]
    if not pend:
        con.close()
        return 0
    uso = app._imagens_usadas_global()
    usadas = {r[0] for r in con.execute("SELECT img_titulo FROM promessas WHERE id_politico=? AND img_status='ok' AND img_titulo IS NOT NULL", (pid,))}
    n = 0
    for p in pend:
        gen = app._imagem_generica(p["tema"], uso, usadas)
        if not gen:
            continue
        titulo = "generica:" + (gen.get("img_titulo") or "")
        con.execute("""UPDATE promessas SET img_status='ok', img_url=?, img_credito=?, img_link=?,
                       img_titulo=?, img_tentativas=0 WHERE id_promessa=?""",
                    (gen["img_url"], gen["img_credito"], gen["img_link"], titulo, p["id_promessa"]))
        usadas.add(titulo)
        uso[titulo] = uso.get(titulo, 0) + 1
        n += 1
    con.commit()
    con.close()
    return n

def processar(pol):
    pid = pol["id_politico"]
    con = app.get_db_connection()
    antes = con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=?", (pid,)).fetchone()["c"]
    con.close()
    if antes >= 5:
        log(f"PULANDO {pol['nome']} ({antes})")
        return

    log(f"INICIO {pol['nome']} ({pol['categoria']})")
    app.QUERIES_GERAIS = [
        "promessas de campanha", "promessas cumpridas e não cumpridas",
        "balanço do governo entregas", "promete anuncia projeto",
        "promessa não cumprida descumpriu",
    ]
    app.QUERIES_TEMAS = ["saúde", "educação", "segurança pública", "economia emprego", "infraestrutura obras"]
    try:
        coletados = app.scrape_all(pol)
    except Exception as e:
        log(f"ERRO coleta {pol['nome']}: {str(e)[:150]}")
        coletados = []
    if coletados:
        known_urls, known_titles = app.get_known_articles(pid)
        novos = [a for a in coletados if a["url"] not in known_urls and app.norm_titulo(a["title"]) not in known_titles]
        app.save_articles(pid, novos)
        app.AI_MAX_PER_RUN = 12
        app.AI_BATCH_SIZE = 12
        pend = app.preparar_pendentes(pol, app.get_pending_articles(pid, 12))
        if pend:
            app.enrich_pending(pend)
            try:
                app.analisar_pendentes(pol, pend)
            except Exception as e:
                log(f"IA falhou {pol['nome']}: {str(e)[:160]}")
    con = app.get_db_connection()
    total = con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=?", (pid,)).fetchone()["c"]
    con.close()
    if total < 5:
        n_local = app.extrair_promessas_locais(pol, limite=12)
        log(f"LOCAL {pol['nome']}: +{n_local}")
    try:
        app.validar_promessas(pol)
    except Exception as e:
        log(f"ERRO validação {pol['nome']}: {str(e)[:150]}")
    n_img = preencher_genericas(pid)
    con = app.get_db_connection()
    total = con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=?", (pid,)).fetchone()["c"]
    semimg = con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=? AND img_status IS NULL", (pid,)).fetchone()["c"]
    con.close()
    log(f"FIM {pol['nome']}: {total} promessas, {n_img} imagens, {semimg} sem imagem")

def main():
    con = app.get_db_connection()
    pols = [dict(r) for r in con.execute("""SELECT * FROM politicos
                                            ORDER BY CASE categoria WHEN 'federal' THEN 1
                                                     WHEN 'governadores' THEN 2 ELSE 3 END, nome""")]
    con.close()
    for pol in pols:
        try:
            processar(pol)
        except Exception:
            log(f"FALHA {pol['nome']}: {traceback.format_exc()[:300]}")
        time.sleep(1)
    log("BATCH FINALIZADO")

if __name__ == "__main__":
    log("BATCH V2 INICIADO")
    main()
