"""Diagnóstico das imagens (fotos dos políticos e imagens das propostas).

Uso (na pasta do projeto, com a internet ligada e o ambiente virtual ativo):
    python diagnostico_imagens.py                 -> testa a conexão e as fotos de TODOS os políticos
    python diagnostico_imagens.py fotos Lula Haddad   -> só alguns (trecho do nome)
    python diagnostico_imagens.py propostas Lula      -> escolhe imagens das propostas pendentes e mostra o resultado

Mostra, para cada caso, SE achou, POR QUAL etapa (título / busca / wikidata) e, quando falha, se foi
"sem foto" de verdade ou erro de conexão/limite de pedidos (HTTP 429) — que é o caso de tentar de novo.
"""
import sys
import time
import requests

import app as A


def testar_conexao():
    print("== Conexão com a Wikimedia ==")
    print("User-Agent:", A.WIKI_HEADERS["User-Agent"])
    for nome, url, params in (
        ("Wikipédia", A.WIKI_PT, {"action": "query", "format": "json", "titles": "Brasil"}),
        ("Commons", A.COMMONS, {"action": "query", "format": "json", "titles": "File:Example.jpg"}),
        ("Wikidata", A.WIKIDATA, {"action": "wbgetentities", "ids": "Q155", "props": "labels", "format": "json"}),
    ):
        try:
            t = time.time()
            r = requests.get(url, params=params, headers=A.WIKI_HEADERS, timeout=10)
            print(f"  {nome:10} HTTP {r.status_code}  ({time.time() - t:.1f}s)")
        except Exception as e:
            print(f"  {nome:10} FALHOU: {e}")
    print()


def todos_politicos(filtros):
    conn = A.get_db_connection()
    rows = [dict(r) for r in conn.execute("SELECT * FROM politicos ORDER BY categoria, nome")]
    conn.close()
    if filtros:
        f = [A.normalize_text(x) for x in filtros]
        rows = [r for r in rows if any(x in A.normalize_text(r["nome"]) for x in f)]
    return rows


def diag_fotos(filtros):
    pols = todos_politicos(filtros)
    ok = sem = erro = 0
    for i in range(0, len(pols), 12):
        lote = pols[i:i + 12]
        res = A.resolver_fotos(lote)
        for p in lote:
            r = res.get(p["id_politico"])
            if r and r.get("erro"):
                erro += 1
                print(f"  ERRO de conexão/limite  {p['nome']}")
            elif not r:
                sem += 1
                print(f"  SEM FOTO (não achei página/retrato)  {p['nome']}  [{p['cargo']} · {p['uf']}]")
            else:
                ok += 1
                print(f"  ok [{r['via']:<16}] {p['nome']}  {r['url'][:90]}")
    print(f"\nResumo: {ok} com foto · {sem} sem foto · {erro} com erro de conexão (de {len(pols)})")


def diag_propostas(filtros):
    for p in todos_politicos(filtros)[:1]:
        print(f"== Propostas de {p['nome']} ==")
        for _ in range(4):
            n = A.gerar_imagens_promessas(p)
            print(f"  rodada: {n} propostas decididas")
            if not n:
                break
        conn = A.get_db_connection()
        for r in conn.execute("SELECT titulo, img_status, img_titulo, img_tentativas FROM promessas WHERE id_politico=? ORDER BY id_promessa",
                              (p["id_politico"],)):
            print(f"  [{r['img_status'] or 'pendente':8}] {r['titulo'][:55]:55} -> {(r['img_titulo'] or '').replace('File:', '')[:50]}")
        conn.close()


if __name__ == "__main__":
    testar_conexao()
    modo = sys.argv[1] if len(sys.argv) > 1 else "fotos"
    filtros = sys.argv[2:] if modo in ("fotos", "propostas") else sys.argv[1:]
    if modo == "propostas":
        diag_propostas(filtros)
    else:
        diag_fotos(filtros)
