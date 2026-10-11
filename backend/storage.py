"""
backend/storage.py
Storage interface + SQLite implementation + get_storage() factory.

Real contract data model (from CONTRACT.md):
  id, name, locality, slot, items (JSON), total_min, total_max,
  original_text, lang, status, collector_name, is_sample, created_at

Environment variable:
    STORAGE  "sqlite" (default) | "dynamodb"
"""

import json
import os
import sqlite3
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Abstract interface
# ---------------------------------------------------------------------------

class Storage(ABC):
    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]: ...
    @abstractmethod
    def get(self, request_id: str) -> Optional[dict[str, Any]]: ...
    @abstractmethod
    def list(self, *, status: Optional[str] = None, collector_name: Optional[str] = None,
             limit: int = 100, offset: int = 0) -> list[dict[str, Any]]: ...
    @abstractmethod
    def accept(self, request_id: str, collector_name: str) -> Optional[dict[str, Any]]: ...
    @abstractmethod
    def count(self) -> int: ...


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    d = dict(row)
    if d.get("items") and isinstance(d["items"], str):
        d["items"] = json.loads(d["items"])
    d["is_sample"] = bool(d.get("is_sample", 0))
    return d


# ---------------------------------------------------------------------------
# SQLite implementation
# ---------------------------------------------------------------------------

_DB_PATH = os.environ.get("SQLITE_PATH", "kabadi.db")

_DDL = """
CREATE TABLE IF NOT EXISTS pickup_requests (
    id             TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    locality       TEXT NOT NULL,
    slot           TEXT NOT NULL,
    items          TEXT NOT NULL,   -- JSON array
    total_min      REAL NOT NULL DEFAULT 0,
    total_max      REAL NOT NULL DEFAULT 0,
    original_text  TEXT,
    lang           TEXT NOT NULL DEFAULT 'hi',
    status         TEXT NOT NULL DEFAULT 'pending',
    collector_name TEXT,
    is_sample      INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL
);
"""


class SQLiteStorage(Storage):
    def __init__(self, db_path: str = _DB_PATH) -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL;")
        self._conn.executescript(_DDL)
        self._conn.commit()

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        now = _now_iso()
        record = {
            "id":             data.get("id", str(uuid.uuid4())),
            "name":           data["name"],
            "locality":       data["locality"],
            "slot":           data["slot"],
            "items":          json.dumps(data.get("items", [])),
            "total_min":      float(data.get("total_min", 0)),
            "total_max":      float(data.get("total_max", 0)),
            "original_text":  data.get("original_text", ""),
            "lang":           data.get("lang", "hi"),
            "status":         data.get("status", "pending"),
            "collector_name": data.get("collector_name"),
            "is_sample":      int(data.get("is_sample", False)),
            "created_at":     data.get("created_at", now),
        }
        self._conn.execute(
            """INSERT INTO pickup_requests
               (id, name, locality, slot, items, total_min, total_max,
                original_text, lang, status, collector_name, is_sample, created_at)
               VALUES
               (:id, :name, :locality, :slot, :items, :total_min, :total_max,
                :original_text, :lang, :status, :collector_name, :is_sample, :created_at)""",
            record,
        )
        self._conn.commit()
        record["items"] = json.loads(record["items"])
        record["is_sample"] = bool(record["is_sample"])
        return record

    def get(self, request_id: str) -> Optional[dict[str, Any]]:
        cur = self._conn.execute(
            "SELECT * FROM pickup_requests WHERE id = ?", (request_id,)
        )
        row = cur.fetchone()
        return _row_to_dict(row) if row else None

    def list(
        self,
        *,
        status: Optional[str] = None,
        collector_name: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        clauses: list[str] = []
        params: list[Any] = []
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        if collector_name is not None:
            clauses.append("collector_name = ?")
            params.append(collector_name)
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        params += [limit, offset]
        cur = self._conn.execute(
            f"SELECT * FROM pickup_requests {where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params,
        )
        return [_row_to_dict(r) for r in cur.fetchall()]

    def accept(self, request_id: str, collector_name: str) -> Optional[dict[str, Any]]:
        self._conn.execute(
            "UPDATE pickup_requests SET status='accepted', collector_name=? WHERE id=? AND status='pending'",
            (collector_name, request_id),
        )
        self._conn.commit()
        return self.get(request_id)

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM pickup_requests").fetchone()[0]


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_storage_instance: Optional[Storage] = None


def get_storage() -> Storage:
    global _storage_instance
    if _storage_instance is None:
        backend = os.environ.get("STORAGE", "sqlite").lower()
        if backend == "dynamodb":
            from backend import storage_dynamo  # noqa: PLC0415
            _storage_instance = storage_dynamo.DynamoDBStorage()
        else:
            _storage_instance = SQLiteStorage()
    return _storage_instance
