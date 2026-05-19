import pytest
from datetime import datetime, timedelta
from database import Feedback, InsightScore
from api.scoring import calculate_pis_for_insight

def test_calculate_pis_for_insight(db_session):
    # Setup mock data
    now = datetime.utcnow()
    
    # Total reviews = 10
    # Category reviews = 4
    # Frequency = 0.4
    
    # Review 1: 10 days old (weight 3.0), intensity 8, risk False
    db_session.add(Feedback(
        raw_content="review 1", insight_category="Late Delivery", 
        intensity_score=8, revenue_risk_flag=False, created_at=now - timedelta(days=10)
    ))
    
    # Review 2: 60 days old (weight: -0.01333*(30) + 3.0 = 2.6), intensity 6, risk True
    db_session.add(Feedback(
        raw_content="review 2", insight_category="Late Delivery", 
        intensity_score=6, revenue_risk_flag=True, created_at=now - timedelta(days=60)
    ))
    
    # Review 3: 200 days old (weight 1.0), intensity 4, risk False
    db_session.add(Feedback(
        raw_content="review 3", insight_category="Late Delivery", 
        intensity_score=4, revenue_risk_flag=False, created_at=now - timedelta(days=200)
    ))
    
    # Review 4: 30 days old (weight 3.0), intensity 10, risk False
    db_session.add(Feedback(
        raw_content="review 4", insight_category="Late Delivery", 
        intensity_score=10, revenue_risk_flag=False, created_at=now - timedelta(days=30)
    ))
    
    # 6 other reviews in another category
    for i in range(6):
        db_session.add(Feedback(
            raw_content=f"other {i}", insight_category="Other Category",
            intensity_score=5, revenue_risk_flag=False, created_at=now
        ))
        
    db_session.commit()
    
    # Calculate PIS
    pis = calculate_pis_for_insight("Late Delivery", db_session)
    
    # Expected calculations:
    # Frequency = 4 / 10 = 0.4
    # Weights = 3.0, 2.6, 1.0, 3.0. Total = 9.6. Avg = 9.6 / 4 = 2.4
    # Intensity = 8 + 6 + 4 + 10 = 28. Avg = 28 / 4 = 7.0
    # Risk Multiplier = 1.5 (because Review 2 has risk)
    # Expected PIS = (0.4 * 2.4 * 7.0) * 1.5 = 6.72 * 1.5 = 10.08
    
    # Check if calculation is close
    assert abs(pis - 10.08) < 0.1
    
    # Verify DB update
    score = db_session.query(InsightScore).filter_by(category="Late Delivery").first()
    assert score is not None
    assert score.total_reviews == 4
    assert abs(score.pis_score - 10.08) < 0.1
