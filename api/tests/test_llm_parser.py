from unittest.mock import patch
from api.scoring import process_review_with_llm

def test_process_review_with_llm_success():
    mock_response_content = '{"category": "Product Quality", "intensity": 9, "revenue_risk": true}'
    
    with patch("api.scoring.client.chat.completions.create") as mock_create:
        mock_create.return_value.choices[0].message.content = mock_response_content
        
        result = process_review_with_llm("This product is broken and I want a refund now.")
        
        assert result["category"] == "Product Quality"
        assert result["intensity"] == 9
        assert result["revenue_risk"] is True

def test_process_review_with_llm_fallback_on_error():
    with patch("api.scoring.client.chat.completions.create") as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        result = process_review_with_llm("This product is okay.")
        
        assert result["category"] == "Uncategorized"
        assert result["intensity"] == 5
        assert result["revenue_risk"] is False

def test_process_review_with_llm_malformed_json():
    mock_response_content = '{"category": "Shipping", "intensity": "high", "revenue_risk": "yes"}'
    
    with patch("api.scoring.client.chat.completions.create") as mock_create:
        mock_create.return_value.choices[0].message.content = mock_response_content
        
        # It should try to parse 'high' to int and 'yes' to bool, which will fail or cast weirdly.
        # Int('high') raises ValueError, so it falls back to exception block
        result = process_review_with_llm("Where is my package?")
        
        assert result["category"] == "Uncategorized"
        assert result["intensity"] == 5
        assert result["revenue_risk"] is False
