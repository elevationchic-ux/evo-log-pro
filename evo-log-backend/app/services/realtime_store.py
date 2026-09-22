"""Redis storage for WebRTC signaling and call state."""
import json
import uuid
from typing import Optional
import redis


class RedisSignalingStore:
    def __init__(self, redis_url: str):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)

    def _key(self, company_id, room_uuid, suffix):
        return f"evo-log:webrtc:{company_id}:{room_uuid}:{suffix}"

    def _ensure(self):
        try:
            self.redis.ping()
        except Exception as exc:
            raise RuntimeError(f"Redis WebRTC signaling unavailable: {exc}") from exc

    def dispatch(self, company_id: int, room_uuid: str, envelope: dict, target_user_id: Optional[int] = None):
        self._ensure()
        key = self._key(company_id, room_uuid, f"user:{target_user_id}" if target_user_id else "broadcast")
        with self.redis.pipeline(transaction=True) as pipe:
            pipe.lpush(key, json.dumps(envelope))
            pipe.ltrim(key, 0, 49)
            pipe.publish(self._key(company_id, room_uuid, "pubsub"), json.dumps(envelope))
            pipe.execute()

    def set_call(self, company_id: int, room_uuid: str, state: dict):
        self._ensure()
        self.redis.set(self._key(company_id, room_uuid, "state"), json.dumps(state), ex=86400)

    def end_call(self, company_id: int, room_uuid: str):
        self._ensure()
        self.redis.delete(
            self._key(company_id, room_uuid, "state"),
            self._key(company_id, room_uuid, "broadcast"),
        )

    def fetch(self, company_id: int, room_uuid: str, user_id: int, since: float):
        self._ensure()
        keys = [self._key(company_id, room_uuid, "broadcast"), self._key(company_id, room_uuid, f"user:{user_id}")]
        signals = []
        for key in keys:
            for raw in self.redis.lrange(key, 0, 49):
                item = json.loads(raw)
                if item["timestamp"] > since and item["sender_id"] != user_id:
                    signals.append(item)
        state_raw = self.redis.get(self._key(company_id, room_uuid, "state"))
        return json.loads(state_raw) if state_raw else None, signals

    def get_call(self, company_id: int, room_uuid: str):
        self._ensure()
        raw = self.redis.get(self._key(company_id, room_uuid, "state"))
        return json.loads(raw) if raw else None
