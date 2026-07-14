from sqlalchemy import text

from app.database.session import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT current_database();"))
    print(result.scalar())