def test_health_check_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data

def test_metrics_endpoint(client):
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_verification_requests" in data
    assert "completed_requests" in data
    assert "average_pipeline_latency_ms" in data

def test_providers_status_endpoint(client):
    response = client.get("/api/providers/status")
    assert response.status_code == 200
    data = response.json()
    assert "providers" in data
    names = [p["name"] for p in data["providers"]]
    assert "Google Gemini API" in names
    assert "Google Fact Check Tools API" in names
    assert "GDELT Project 2.0 DOC API" in names
