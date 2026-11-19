"""Pré-preenche as imagens de todas as promessas pendentes, político por político.

Uso:  python preencher_imagens.py            (todos os políticos)
      python preencher_imagens.py 12 15      (só os ids informados)

Rode uma vez (pode deixar em segundo plano): depois disso a página abre com as imagens
já prontas, sem esperar a busca. As buscas ficam salvas na tabela commons_cache.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app


def pendentes(pid: int) -> int:
    con = app.get_db_connection()
    n = con.execute("SELECT COUNT(*) FROM promessas WHERE id_politico=? AND img_status IS NULL", (pid,)).fetchone()[0]
    con.close()
    return n


def main(ids=None):
    con = app.get_db_connection()
    pols = [dict(r) for r in con.execute("SELECT * FROM politicos ORDER BY nome")]
    con.close()
    if ids:
        pols = [p for p in pols if p["id_politico"] in ids]
    t0 = time.time()
    for pol in pols:
        pid = pol["id_politico"]
        if not pendentes(pid):
            continue
        total = 0
        for _ in range(12):                     
            n = app.gerar_imagens_promessas(pol, limite=40)
            total += n
            if n == 0 or not pendentes(pid):
                break
        print(f"{pol['nome']}: +{total} imagens, {pendentes(pid)} ainda sem imagem", flush=True)
    print(f"Concluído em {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main({int(x) for x in sys.argv[1:]} or None)