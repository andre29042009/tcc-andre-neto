# MAPC

**MAPC - Monitoramento e Analise de Promessas de Campanha** acompanha promessas oficiais publicadas pelo projeto [Promessas dos Politicos do G1](https://g1.globo.com/politica/promessas-dos-politicos/home/).

## Execucao

```powershell
python -m pip install -r requirements.txt
$env:GROQ_API_KEY = "sua-chave"
python TCCpolitica/app.py
```

Abra `http://127.0.0.1:5000`.

## Banco

O desenvolvimento usa SQLite automaticamente. Para MySQL, configure antes de iniciar:

```powershell
$env:DATABASE_URL = "mysql+pymysql://usuario:senha@localhost:3306/mapc"
```

O banco precisa existir previamente. As tabelas sao criadas pelo Flask na inicializacao.

## Atualizacao

A rota `POST /api/sync` importa os perfis e promessas atuais do G1 e reavalia as promessas com noticias. O agendador executa a mesma rotina a cada 24 horas por padrao; altere `SYNC_INTERVAL_HOURS` para outro intervalo.

Cada avaliacao fica registrada com status, explicacao, data e artigos consultados. O historico de cada politico fica disponivel em `/historico/<id>` depois da sincronizacao.
