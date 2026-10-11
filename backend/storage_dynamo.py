"""
backend/storage_dynamo.py
DynamoDB storage implementation — lazily imported when STORAGE=dynamodb.
Table key: id (S). Table name from env DYNAMO_TABLE (default: KabadiRequests).
"""

import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from backend.storage import Storage

_TABLE_NAME = os.environ.get("DYNAMO_TABLE", "KabadiRequests")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DynamoDBStorage(Storage):
    def __init__(self, table_name: str = _TABLE_NAME) -> None:
        import boto3  # noqa: PLC0415
        region = os.environ.get("AWS_REGION", "ap-south-1")
        self._table = boto3.resource("dynamodb", region_name=region).Table(table_name)

    @staticmethod
    def _enc(record: dict[str, Any]) -> dict[str, Any]:
        out = dict(record)
        if isinstance(out.get("items"), list):
            out["items"] = json.dumps(out["items"])
        out["is_sample"] = str(out.get("is_sample", False))
        out["total_min"] = str(out.get("total_min", 0))
        out["total_max"] = str(out.get("total_max", 0))
        return out

    @staticmethod
    def _dec(item: dict[str, Any]) -> dict[str, Any]:
        out = dict(item)
        if isinstance(out.get("items"), str):
            out["items"] = json.loads(out["items"])
        out["is_sample"] = out.get("is_sample", "False") == "True"
        out["total_min"] = float(out.get("total_min", 0))
        out["total_max"] = float(out.get("total_max", 0))
        return out

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        record: dict[str, Any] = {
            "id":             data.get("id", str(uuid.uuid4())),
            "name":           data["name"],
            "locality":       data["locality"],
            "slot":           data["slot"],
            "items":          data.get("items", []),
            "total_min":      float(data.get("total_min", 0)),
            "total_max":      float(data.get("total_max", 0)),
            "original_text":  data.get("original_text", ""),
            "lang":           data.get("lang", "hi"),
            "status":         data.get("status", "pending"),
            "collector_name": data.get("collector_name"),
            "is_sample":      data.get("is_sample", False),
            "created_at":     data.get("created_at", _now_iso()),
        }
        self._table.put_item(Item=self._enc(record))
        return record

    def get(self, request_id: str) -> Optional[dict[str, Any]]:
        resp = self._table.get_item(Key={"id": request_id})
        item = resp.get("Item")
        return self._dec(item) if item else None

    def list(self, *, status=None, collector_name=None, limit=100, offset=0):
        from boto3.dynamodb.conditions import Attr  # noqa: PLC0415
        fe = None
        if status:
            fe = Attr("status").eq(status)
        if collector_name:
            cond = Attr("collector_name").eq(collector_name)
            fe = cond if fe is None else fe & cond
        kwargs = {"FilterExpression": fe} if fe else {}
        items: list[dict] = []
        resp = self._table.scan(**kwargs)
        items.extend(resp.get("Items", []))
        while "LastEvaluatedKey" in resp:
            resp = self._table.scan(ExclusiveStartKey=resp["LastEvaluatedKey"], **kwargs)
            items.extend(resp.get("Items", []))
        items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return [self._dec(i) for i in items[offset: offset + limit]]

    def accept(self, request_id: str, collector_name: str) -> Optional[dict[str, Any]]:
        self._table.update_item(
            Key={"id": request_id},
            UpdateExpression="SET #s = :s, collector_name = :c",
            ConditionExpression="#s = :pending",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": "accepted", ":c": collector_name, ":pending": "pending"},
        )
        return self.get(request_id)

    def count(self) -> int:
        return self._table.item_count
