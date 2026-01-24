# Log: Level 01 - Supabase Integration (Complete)

**Date (KST)**: 2026-01-24 19:37
**Commit Hash**: `661f7f5` (Previous Commit) -> *Will be updated after this log is committed*

## 1. Summary
We successfully migrated the data storage from local files to Supabase Cloud DB.

## 2. Modified Files (Direct Links)
- **Supabase Storage Logic**: [crawler/storage_supabase.py](../crawler/storage_supabase.py)
- **Main Crawler**: [crawler/main.py](../crawler/main.py)
- **Environment Config**: [crawler/.env](../crawler/.env)
- **SQL Schema**: [crawler/schema.sql](../crawler/schema.sql)
- **Learning Guide**: [SUPABASE_LEARNING.md](../SUPABASE_LEARNING.md)

## 3. New Concepts Learned

### A. Environment Variables (`.env`)
Instead of hardcoding secrets in Python, we use a separate file.
```python
from dotenv import load_dotenv
import os

load_dotenv() # Load variables from .env
secret_key = os.getenv("SUPABASE_KEY")
```

### B. Supabase `Upsert`
Inserting data but handling duplicates automatically.
```python
# If a record with the same date/station/line exists, update it. If not, insert.
client.table("subway_traffic").upsert(data, on_conflict="date,station_name,line_number").execute()
```

### C. Type Hinting with Supabase
Using explicit types helps prevent errors.
```python
from supabase import Client
client: Client = create_client(url, key)
```

## 4. Work History
- **Verified APIs**: Seoul Data and KMA APIs are confirmed working.
- **Supabase**: Connection successful, table creation tutorial provided.
- **Git**: Initialized repository and established version control workflow.
