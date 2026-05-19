import io
from unittest.mock import patch
from database import InsightScore

def test_upload_csv(client):
    csv_content = "review_id,review_text,review_date,rating\n1,Great app,2023-10-01,5\n2,Broken,2023-10-02,1"
    
    # We should mock process_csv_background so we don't actually call the LLM in this endpoint test
    with patch("api.main.process_csv_background") as mock_bg:
        response = client.post(
            "/upload-csv", 
            files={"file": ("test.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        )
        
        assert response.status_code == 200
        assert response.json() == {"message": "CSV upload started processing in the background."}
        
        # Verify background task was queued
        assert mock_bg.called

def test_get_ranked_insights(client, db_session):
    # Add dummy insight scores
    db_session.add(InsightScore(category="Bug", pis_score=15.5, total_reviews=3))
    db_session.add(InsightScore(category="UI", pis_score=5.0, total_reviews=2))
    db_session.commit()
    
    response = client.get("/insights/ranked")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) >= 2
    
    # Assert they are sorted descending by pis_score
    scores = [item["pis_score"] for item in data]
    assert scores == sorted(scores, reverse=True)
    
    # Assert top is Bug
    assert data[0]["category"] == "Bug"
