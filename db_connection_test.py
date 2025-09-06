# db_connection_test.py
import os, sys, socket
from pathlib import Path
from dotenv import load_dotenv

print("=== DB connection smoke test ===")

# 1) Load env (same pattern as your app)
here = Path(__file__).resolve().parent
loaded = None
for name in (".env.development", ".env.dev", ".env"):
    p = here / name
    if p.exists():
        load_dotenv(p, override=False)
        loaded = p.name
        break
load_dotenv(here / ".env.local", override=True)

print(f"Env file loaded: {loaded or 'None'}")

# 2) Read the SUPABASE_* pieces (pooler)
USER = os.getenv("SUPABASE_USER", "")
PASSWORD = os.getenv("SUPABASE_PASSWORD", "")
HOST = os.getenv("SUPABASE_HOST", "")
PORT = int(os.getenv("SUPABASE_PORT", "6543"))
DBNAME = os.getenv("SUPABASE_DB") or os.getenv("SUPABASE_DBNAME") or "postgres"

print("Config preview (sanitized):")
print(f"  user = {USER}")
print(f"  host = {HOST}")
print(f"  port = {PORT}")
print(f"  db   = {DBNAME}")

# 3) Quick sanity checks
if not USER or not PASSWORD or not HOST:
    print("❌ Missing one or more of SUPABASE_USER / SUPABASE_PASSWORD / SUPABASE_HOST")
    sys.exit(1)

if "." not in USER:
    print("⚠️  SUPABASE_USER should look like 'postgres.<PROJECT_REF>' for the pooler.")

try:
    infos = socket.getaddrinfo(HOST, PORT, proto=socket.IPPROTO_TCP)
    ips = sorted({i[4][0] for i in infos})
    print(f"DNS resolves {HOST} -> {ips}")
except Exception as e:
    print(f"DNS resolution failed for {HOST}: {e}")

# 4) Try a direct psycopg2 connection (no SQLAlchemy), SSL required
try:
    import psycopg2
except Exception:
    print("Installing psycopg2-binary is required: pip install psycopg2-binary")
    sys.exit(1)

try:
    conn = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME,
        sslmode="require",
    )
    print("✅ Connection successful!")

    cur = conn.cursor()
    cur.execute("select version(), current_database(), current_user, now();")
    version, current_db, current_user, now = cur.fetchone()
    print(f"server version: {version}")
    print(f"current db:     {current_db}")
    print(f"current user:   {current_user}")
    print(f"now():          {now}")

    cur.close()
    conn.close()
    print("Closed cleanly.")
except Exception as e:
    print("❌ Connection failed.")
    print(repr(e))
    sys.exit(2)
