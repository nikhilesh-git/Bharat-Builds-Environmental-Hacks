"""
Storage abstraction supporting SQLite locally and DynamoDB when deployed.
Includes 6 pre-seeded sample requests (is_sample=true) for instant demo.
"""

import os
import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime

class BaseStorage:
    def get(self, request_id: str) -> Optional[dict]:
        raise NotImplementedError

    def list_all(self) -> List[dict]:
        raise NotImplementedError

    def save(self, request_data: dict) -> dict:
        raise NotImplementedError

    def update_status(self, request_id: str, status: str, collector_name: Optional[str] = None) -> Optional[dict]:
        raise NotImplementedError


class SQLiteStorage(BaseStorage):
    def __init__(self, db_path: str = "kabadi.db"):
        self.db_path = db_path
        self._init_db()
        self._seed_sample_data()

    def _get_conn(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS requests (
                    id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    name TEXT NOT NULL,
                    locality TEXT NOT NULL,
                    slot TEXT NOT NULL,
                    items_json TEXT NOT NULL,
                    total_min INTEGER NOT NULL,
                    total_max INTEGER NOT NULL,
                    collector_name TEXT,
                    is_sample INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def _seed_sample_data(self):
        with self._get_conn() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM requests")
            count = cur.fetchone()[0]
            if count == 0:
                samples = [
                    {
                        "id": "req_sample_101",
                        "status": "pending",
                        "name": "राजेश कुमार",
                        "locality": "लाजपत नगर IV, ब्लॉक सी",
                        "slot": "कल सुबह (10:00 AM - 12:00 PM)",
                        "items_json": json.dumps([
                            {"material": "अखबार (Newspaper)", "quantity": "12 kg", "assumed": False, "rate_per_kg": "₹12 - ₹15/kg", "min_price": 144, "max_price": 180},
                            {"material": "गत्ता (Cardboard)", "quantity": "6 kg", "assumed": False, "rate_per_kg": "₹8 - ₹10/kg", "min_price": 48, "max_price": 60}
                        ]),
                        "total_min": 192,
                        "total_max": 240,
                        "collector_name": None,
                        "is_sample": 1,
                        "created_at": "2026-10-11T16:00:00Z"
                    },
                    {
                        "id": "req_sample_102",
                        "status": "pending",
                        "name": "Pooja Malhotra",
                        "locality": "Malviya Nagar, Main Market",
                        "slot": "Today Afternoon (2:00 PM - 4:00 PM)",
                        "items_json": json.dumps([
                            {"material": "लोहा (Iron / Steel)", "quantity": "8 kg", "assumed": True, "rate_per_kg": "₹26 - ₹30/kg", "min_price": 208, "max_price": 240},
                            {"material": "PET प्लास्टिक बोतलें", "quantity": "3 kg", "assumed": False, "rate_per_kg": "₹15 - ₹20/kg", "min_price": 45, "max_price": 60}
                        ]),
                        "total_min": 253,
                        "total_max": 300,
                        "collector_name": None,
                        "is_sample": 1,
                        "created_at": "2026-10-11T16:15:00Z"
                    },
                    {
                        "id": "req_sample_103",
                        "status": "pending",
                        "name": "अमित सक्सेना",
                        "locality": "रोहिणी सेक्टर 7, पॉकेट 3",
                        "slot": "कल दोपहर (2:00 PM - 4:00 PM)",
                        "items_json": json.dumps([
                            {"material": "ई-कचरा / पुराना कूलर", "quantity": "15 kg", "assumed": True, "rate_per_kg": "₹26 - ₹30/kg", "min_price": 390, "max_price": 450},
                            {"material": "तांबा (Copper Wire)", "quantity": "1 kg", "assumed": False, "rate_per_kg": "₹450 - ₹520/kg", "min_price": 450, "max_price": 520}
                        ]),
                        "total_min": 840,
                        "total_max": 970,
                        "collector_name": None,
                        "is_sample": 1,
                        "created_at": "2026-10-11T16:30:00Z"
                    },
                    {
                        "id": "req_sample_104",
                        "status": "pending",
                        "name": "Sunita Verma",
                        "locality": "Saket, Block J",
                        "slot": "Tomorrow Morning (10:00 AM - 12:00 PM)",
                        "items_json": json.dumps([
                            {"material": "किताबें / मिश्रित कागज", "quantity": "20 kg", "assumed": False, "rate_per_kg": "₹8 - ₹12/kg", "min_price": 160, "max_price": 240}
                        ]),
                        "total_min": 160,
                        "total_max": 240,
                        "collector_name": None,
                        "is_sample": 1,
                        "created_at": "2026-10-11T16:45:00Z"
                    },
                    {
                        "id": "req_sample_105",
                        "status": "accepted",
                        "name": "दिनेश अग्रवाल",
                        "locality": "ग्रेटर कैलाश I, एन ब्लॉक",
                        "slot": "आज शाम (4:00 PM - 6:00 PM)",
                        "items_json": json.dumps([
                            {"material": "एल्युमिनियम के बर्तन", "quantity": "4 kg", "assumed": False, "rate_per_kg": "₹100 - ₹125/kg", "min_price": 400, "max_price": 500}
                        ]),
                        "total_min": 400,
                        "total_max": 500,
                        "collector_name": "सुरेश कबाड़ीवाला",
                        "is_sample": 1,
                        "created_at": "2026-10-11T15:00:00Z"
                    },
                    {
                        "id": "req_sample_106",
                        "status": "accepted",
                        "name": "विकास मेहरा",
                        "locality": "मयूर विहार फेज 1",
                        "slot": "कल सुबह (10:00 AM - 12:00 PM)",
                        "items_json": json.dumps([
                            {"material": "अखबार (Newspaper)", "quantity": "18 kg", "assumed": False, "rate_per_kg": "₹12 - ₹15/kg", "min_price": 216, "max_price": 270},
                            {"material": "कठोर प्लास्टिक की बाल्टी", "quantity": "2 kg", "assumed": True, "rate_per_kg": "₹12 - ₹18/kg", "min_price": 24, "max_price": 36}
                        ]),
                        "total_min": 240,
                        "total_max": 306,
                        "collector_name": "रमेश कुमार",
                        "is_sample": 1,
                        "created_at": "2026-10-11T15:30:00Z"
                    }
                ]
                for s in samples:
                    conn.execute("""
                        INSERT INTO requests (id, status, name, locality, slot, items_json, total_min, total_max, collector_name, is_sample, created_at)
                        VALUES (:id, :status, :name, :locality, :slot, :items_json, :total_min, :total_max, :collector_name, :is_sample, :created_at)
                    """, s)
                conn.commit()

    def get(self, request_id: str) -> Optional[dict]:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT * FROM requests WHERE id = ?", (request_id,))
            row = cur.fetchone()
            if not row:
                return None
            return self._row_to_dict(row)

    def list_all(self) -> List[dict]:
        with self._get_conn() as conn:
            cur = conn.execute("SELECT * FROM requests ORDER BY created_at DESC")
            return [self._row_to_dict(row) for row in cur.fetchall()]

    def save(self, data: dict) -> dict:
        req_id = data["id"]
        status = data.get("status", "pending")
        name = data.get("name", "")
        locality = data.get("locality", "")
        slot = data.get("slot", "")
        items_json = json.dumps(data.get("items", []))
        total_min = int(data.get("total_min", 0))
        total_max = int(data.get("total_max", 0))
        collector_name = data.get("collector_name")
        is_sample = 1 if data.get("is_sample") else 0
        created_at = data.get("created_at") or datetime.utcnow().isoformat() + "Z"

        with self._get_conn() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO requests 
                (id, status, name, locality, slot, items_json, total_min, total_max, collector_name, is_sample, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (req_id, status, name, locality, slot, items_json, total_min, total_max, collector_name, is_sample, created_at))
            conn.commit()

        return self.get(req_id)

    def update_status(self, request_id: str, status: str, collector_name: Optional[str] = None) -> Optional[dict]:
        with self._get_conn() as conn:
            if collector_name is not None:
                conn.execute("UPDATE requests SET status = ?, collector_name = ? WHERE id = ?", (status, collector_name, request_id))
            else:
                conn.execute("UPDATE requests SET status = ? WHERE id = ?", (status, request_id))
            conn.commit()
        return self.get(request_id)

    def _row_to_dict(self, row) -> dict:
        d = dict(row)
        try:
            d["items"] = json.loads(d["items_json"])
        except Exception:
            d["items"] = []
        del d["items_json"]
        d["is_sample"] = bool(d["is_sample"])
        return d


def get_storage() -> BaseStorage:
    storage_type = os.environ.get("STORAGE", "sqlite").lower()
    if storage_type == "dynamodb":
        try:
            from backend.storage_dynamo import DynamoStorage
            return DynamoStorage()
        except Exception as e:
            print(f"DynamoDB load failed, falling back to SQLite: {e}")
            return SQLiteStorage()
    return SQLiteStorage()
