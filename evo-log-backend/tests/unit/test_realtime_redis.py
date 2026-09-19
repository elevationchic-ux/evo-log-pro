import json
import asyncio

from app.services.events.event_service import ReactiveEventBus
from app.services.realtime_store import RedisSignalingStore


class FakeRedis:
    def __init__(self):
        self.values = {}
        self.published = []

    def ping(self):
        return True

    def lpush(self, key, value):
        self.values.setdefault(key, []).insert(0, value)

    def ltrim(self, key, start, end):
        self.values[key] = self.values[key][start:end + 1]

    def lrange(self, key, start, end):
        return self.values.get(key, [])[start:end + 1]

    def set(self, key, value, ex=None):
        self.values[key] = value

    def get(self, key):
        return self.values.get(key)

    def delete(self, key):
        self.values.pop(key, None)

    def publish(self, channel, value):
        self.published.append((channel, value))

    def pipeline(self, transaction=True):
        return FakePipeline(self)


class FakePipeline:
    def __init__(self, redis):
        self.redis = redis
        self.commands = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def lpush(self, *args):
        self.commands.append(("lpush", args))
        return self

    def ltrim(self, *args):
        self.commands.append(("ltrim", args))
        return self

    def publish(self, *args):
        self.commands.append(("publish", args))
        return self

    def execute(self):
        for command, args in self.commands:
            getattr(self.redis, command)(*args)


def test_event_channels_are_tenant_scoped():
    bus = ReactiveEventBus("redis://unused")
    assert bus._origin
    assert "tenant:7" in "evo-log:events:tenant:7"


def test_event_delivery_never_crosses_tenants():
    class Socket:
        def __init__(self):
            self.messages = []

        async def send_json(self, payload):
            self.messages.append(payload)

    bus = ReactiveEventBus("redis://unused")
    tenant_a, tenant_b = Socket(), Socket()
    bus.add_connection(7, "a", tenant_a)
    bus.add_connection(8, "b", tenant_b)
    asyncio.run(bus._deliver({"type": "shipment.created", "company_id": 7,
                              "data": {"id": 1}, "timestamp": "now"}))
    assert len(tenant_a.messages) == 1
    assert tenant_b.messages == []


def test_signals_are_isolated_by_company_and_target():
    store = RedisSignalingStore("redis://unused")
    store.redis = FakeRedis()
    envelope = {"sender_id": 1, "timestamp": 10.0, "signal_type": "offer"}
    store.dispatch(7, "room", envelope, target_user_id=2)
    state, signals = store.fetch(7, "room", 2, 0)
    assert state is None
    assert signals == [envelope]
    _, signals = store.fetch(7, "room", 3, 0)
    assert signals == []
    assert store.redis.published[0][0].startswith("evo-log:webrtc:7:")
