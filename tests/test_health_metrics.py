from deriv_sdk.client import DerivClient
from deriv_sdk.config import SDKConfig
from deriv_sdk.resilience.circuit_breaker import CircuitBreaker


def test_client_exposes_health_and_metrics_snapshots():
    client = DerivClient(app_id="1089")

    metrics = client.metrics()
    health = client.health()

    assert metrics.total_requests == 0
    assert not health.started
    assert not health.connected
    assert health.pending_requests == 0

    client.reset_metrics()


def test_client_health_reports_configured_circuit_breaker_state():
    breaker = CircuitBreaker(name="sdk")
    client = DerivClient(
        app_id="ignored",
        config=SDKConfig(app_id="1089", circuit_breaker=breaker),
    )

    health = client.health()

    assert health.circuit_breaker_states == {"sdk": "closed"}


def test_client_health_reports_active_subscriptions():
    client = DerivClient(app_id="1089")

    class FakeSubscription:
        id = "sub-1"

    client.market.subscriptions.register(FakeSubscription())  # type: ignore[arg-type]

    assert client.health().active_subscriptions == 1
