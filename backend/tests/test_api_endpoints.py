import io
from PIL import Image

def test_api_analyze_text_only(client):
    payload = {
        "headline": "WHO announces new global health guidelines for 2026",
        "article_text": "According to official spokespersons at the Geneva headquarters, updated recommendations have been published for member states."
    }
    response = client.post("/api/analyze", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["headline"] == payload["headline"]
    assert "final_assessment" in data
    assert "claims" in data
    assert "text_analysis" in data
    assert "latency_breakdown_ms" in data
    assert data["total_latency_ms"] > 0

    analysis_id = data["id"]

    # Retrieve analysis report by ID
    get_resp = client.get(f"/api/analyses/{analysis_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == analysis_id

    # Check history listing
    hist_resp = client.get("/api/history?page=1&page_size=10")
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert hist_data["total"] >= 1
    assert any(item["id"] == analysis_id for item in hist_data["items"])

    # Delete history record
    del_resp = client.delete(f"/api/history/{analysis_id}")
    assert del_resp.status_code == 200

    # Verify deleted
    get_after_del = client.get(f"/api/analyses/{analysis_id}")
    assert get_after_del.status_code == 404

def test_api_analyze_missing_inputs(client):
    response = client.post("/api/analyze", data={})
    assert response.status_code == 400
    assert "At least one input parameter" in response.json()["detail"]

def test_api_analyze_multimodal_with_image(client):
    img = Image.new("RGB", (120, 120), color="green")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    data = {
        "headline": "Park expansion completed in downtown district",
        "article_text": "City officials announced the completion of the urban green park."
    }
    files = {
        "image": ("park.jpg", buf, "image/jpeg")
    }

    response = client.post("/api/analyze", data=data, files=files)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["image_analysis"]["has_image"] is True
    assert res_json["image_analysis"]["image_format"] == "JPEG"
    assert res_json["image_analysis"]["image_dimensions"] == "120x120"
