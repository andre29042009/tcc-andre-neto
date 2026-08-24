import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SQLITE_PATH = os.path.join(BASE_DIR, "instance", "mapc.sqlite3")
os.makedirs(os.path.dirname(DEFAULT_SQLITE_PATH), exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
G1_PROMISES_URL = "https://g1.globo.com/politica/promessas-dos-politicos/home/"
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///" + DEFAULT_SQLITE_PATH.replace("\\", "/")
if DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith("sqlite:////"):
    database_path = DATABASE_URL.removeprefix("sqlite:///")
    if not os.path.isabs(database_path):
        database_path = os.path.join(BASE_DIR, "..", database_path)
        DATABASE_URL = "sqlite:///" + os.path.abspath(database_path).replace("\\", "/")
SYNC_INTERVAL_HOURS = int(os.getenv("SYNC_INTERVAL_HOURS", "24"))
MAPC_NAME = "MAPC - Monitoramento e Analise de Promessas de Campanha"

TEMAS_PROMESSAS = [
    "saude", "educacao", "seguranca", "empregos", "infraestrutura",
    "meio ambiente", "economia", "habitacao", "corrupcao",
    "mobilidade", "assistencia social",
]

# Mandatos em curso em 2026. O catalogo e intencionalmente pequeno e pode ser
# ampliado conforme a fonte oficial do G1 publicar novos perfis.
POLITICIANS = {
    "federal": [
        {"id": "lula", "nome": "Luiz Inacio Lula da Silva", "cargo": "Presidente da Republica", "partido": "PT", "uf": "BR", "desde": "2023"},
        {"id": "alkmin", "nome": "Geraldo Alckmin", "cargo": "Vice-Presidente", "partido": "PSB", "uf": "BR", "desde": "2023"},
    ],
    "governadores": [
        {"id": "tarcisio", "nome": "Tarcisio de Freitas", "cargo": "Governador", "partido": "Republicanos", "uf": "SP", "desde": "2023"},
        {"id": "caiado", "nome": "Ronaldo Caiado", "cargo": "Governador", "partido": "Uniao Brasil", "uf": "GO", "desde": "2019"},
        {"id": "zema", "nome": "Romeu Zema", "cargo": "Governador", "partido": "Novo", "uf": "MG", "desde": "2019"},
        {"id": "leite", "nome": "Eduardo Leite", "cargo": "Governador", "partido": "PSDB", "uf": "RS", "desde": "2019"},
        {"id": "barbalho", "nome": "Helder Barbalho", "cargo": "Governador", "partido": "MDB", "uf": "PA", "desde": "2019"},
        {"id": "fonteles", "nome": "Rafael Fonteles", "cargo": "Governador", "partido": "PT", "uf": "PI", "desde": "2023"},
    ],
    "prefeitos": [
        {"id": "paes", "nome": "Eduardo Paes", "cargo": "Prefeito", "partido": "PSD", "uf": "RJ", "desde": "2021"},
        {"id": "nunes", "nome": "Ricardo Nunes", "cargo": "Prefeito", "partido": "MDB", "uf": "SP", "desde": "2021"},
        {"id": "campos", "nome": "Joao Campos", "cargo": "Prefeito", "partido": "PSB", "uf": "PE", "desde": "2021"},
        {"id": "reis", "nome": "Bruno Reis", "cargo": "Prefeito", "partido": "Uniao Brasil", "uf": "BA", "desde": "2021"},
        {"id": "mabel", "nome": "Sandro Mabel", "cargo": "Prefeito", "partido": "Uniao Brasil", "uf": "GO", "desde": "2025"},
    ],
}

ALL_POLITICIANS = [politician for group in POLITICIANS.values() for politician in group]
