import sys, time
sys.path.insert(0, r"D:\TCC")
import app

LOG = r"D:\TCC\mais_promessas.log"

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

con = app.get_db_connection()
pols = [dict(r) for r in con.execute("SELECT * FROM politicos ORDER BY nome")]
con.close()
for pol in pols:
    pid = pol["id_politico"]
    if pid == 1:
        continue
    antes = 0
    con = app.get_db_connection()
    antes = con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=?", (pid,)).fetchone()["c"]
    con.close()
    n = app.extrair_promessas_locais(pol, limite=25)
    try:
        app.validar_promessas(pol)
    except Exception as e:
        log(f"validacao {pol['nome']}: {str(e)[:100]}")
    ni = preencher_genericas(pid)
    con = app.get_db_connection()
    depois = con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=?", (pid,)).fetchone()["c"]
    sem = con.execute("SELECT COUNT(*) c FROM promessas WHERE id_politico=? AND img_status IS NULL", (pid,)).fetchone()["c"]
    con.close()
    log(f"{pol['nome']}: {antes} -> {depois} (+{n} locais, {ni} imagens, {sem} sem imagem)")
log("MAIS PROMESSAS FINALIZADO")
