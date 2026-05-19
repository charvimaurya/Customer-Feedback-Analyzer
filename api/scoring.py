import os
import json
from openai import OpenAI
from sqlalchemy.orm import Session
from datetime import datetime
from database import Feedback, InsightScore

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-api-key-here"))

def process_review_with_llm(review_text: str):
    """
    Uses OpenAI to extract category, intensity, and revenue risk from a review.
    """
    prompt = f"""
    Analyze the following customer review and provide a JSON response with three fields:
    - category: A concise 2-3 word string categorizing the main issue (e.g., "Late Delivery", "Defective Product"). If positive, categorize the positive aspect.
    - intensity: An integer from 1 to 10 indicating the severity or intensity of the sentiment. 10 is extremely intense.
    - revenue_risk: A boolean indicating if the review contains signals of lost revenue, such as mentions of returns, refunds, switching brands, or never buying again.

    Review: "{review_text}"
    
    Respond ONLY with valid JSON.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        
        category = data.get("category", "General Feedback")
        # Ensure intensity is int
        intensity = int(data.get("intensity", 5))
        # Ensure revenue_risk is bool
        revenue_risk = bool(data.get("revenue_risk", False))
        
        return {
            "category": category,
            "intensity": intensity,
            "revenue_risk": revenue_risk
        }
    except Exception as e:
        print(f"LLM Processing Error: {e}")
        return {
            "category": "Uncategorized",
            "intensity": 5,
            "revenue_risk": False
        }

def calculate_pis_for_insight(category: str, db: Session):
    """
    Calculates the Problem Impact Score (PIS) for a specific category.
    PIS = (frequency * recency_weight * avg_intensity) * (revenue_risk_multiplier)
    """
    # Total reviews for frequency
    total_reviews = db.query(Feedback).count()
    if total_reviews == 0:
        return 0.0

    # Reviews in this category
    category_reviews = db.query(Feedback).filter(Feedback.insight_category == category).all()
    if not category_reviews:
        return 0.0
    
    category_count = len(category_reviews)
    frequency = category_count / total_reviews
    
    # Calculate average intensity and risk flag
    total_intensity = 0
    has_revenue_risk = False
    
    total_recency_weight = 0.0
    
    now = datetime.utcnow()
    
    for review in category_reviews:
        total_intensity += (review.intensity_score or 5)
        if review.revenue_risk_flag:
            has_revenue_risk = True
            
        # Recency decay calculation
        if review.created_at:
            days_old = (now - review.created_at).days
        else:
            days_old = 0

        if days_old <= 30:
            weight = 3.0
        elif days_old >= 180:
            weight = 1.0
        else:
            # Linear decay from 30 to 180 days (3.0 down to 1.0)
            # m = (1.0 - 3.0) / (180 - 30) = -2 / 150 = -0.01333
            # y = m * (x - 30) + 3.0
            weight = -0.01333 * (days_old - 30) + 3.0
        
        total_recency_weight += weight
        
    avg_intensity = total_intensity / category_count
    avg_recency_weight = total_recency_weight / category_count
    
    # Risk multiplier
    revenue_risk_multiplier = 1.5 if has_revenue_risk else 1.0
    
    # PIS
    pis = (frequency * avg_recency_weight * avg_intensity) * revenue_risk_multiplier
    
    # Cache to InsightScore table
    score_record = db.query(InsightScore).filter(InsightScore.category == category).first()
    if not score_record:
        score_record = InsightScore(category=category)
        db.add(score_record)
        
    score_record.total_reviews = category_count
    score_record.pis_score = pis
    score_record.last_calculated_at = datetime.utcnow()
    
    db.commit()
    
    return pis

def recalculate_all_pis(db: Session):
    """Recalculates PIS for all distinct categories."""
    distinct_categories = db.query(Feedback.insight_category).distinct().all()
    for (cat,) in distinct_categories:
        if cat:
            calculate_pis_for_insight(cat, db)
