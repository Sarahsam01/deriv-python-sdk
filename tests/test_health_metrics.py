from deriv_sdk.client import DerivClient


def test_client_exposes_health_and_metrics_snapshots():
    client = DerivClient(app_id="1089")

    metrics = client.metrics()
    health = client.health()

    assert metrics.total_requests == 0
    assert not health.started
    assert not health.connected
    assert health.pending_requests == 0

    client.reset_metrics()
