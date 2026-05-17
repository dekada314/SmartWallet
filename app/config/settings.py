from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent.parent
INFRASTRUCTURE_PATH = root_dir / "infrastructure"

KNOWLEDGE_BASE_PATH = INFRASTRUCTURE_PATH / "knowledge_base" / "yaml"
DB = INFRASTRUCTURE_PATH / "database" / "db" / "app.sqlite3"
