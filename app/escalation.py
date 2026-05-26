# escalation.py

ESCALATION_KEYWORDS = {
    "failed": [
        "didn't work",
        "doesn't work",
        "still broken",
        "didn't solve",
        "didn't help",
        "not working",
        "failed",
        "failure",
        "error",
        "crashed",
        "stuck",
        "frozen",
        "urgent",
        "critical",
        "emergency",
        "asap",
    ],
    "multiple_attempts": [
        "tried again",
        "tried multiple times",
        "tried twice",
        "tried 2",
        "tried 3",
        "multiple times",
        "again",
        "still not",
        "even after",
        "even with",
    ],
    "business_impact": [
        "everyone",
        "whole team",
        "all users",
        "can't work",
        "can't do my job",
        "outage",
        "down",
        "data loss",
        "all departments",
        "blocking",
        "halted",
        "stopped",
    ],
}


def detect_escalation_keywords(text: str) -> dict:
    """
    Detects escalation keywords in text (English).
    
    Args:
        text: User message
        
    Returns:
        {
            "escalation_triggered": bool,
            "reasons": list of categories matched,
            "confidence": float 0.0-1.0,
            "matched_keywords": list of matched keywords
        }
    """
    text_lower = text.lower()
    reasons = []
    matched = []
    
    for category, keywords in ESCALATION_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                if category not in reasons:
                    reasons.append(category)
                matched.append(keyword)
                break  # One match per category
    
    escalation_triggered = len(reasons) > 0
    # Confidence: 1 reason=0.33, 2 reasons=0.66, 3+=1.0
    confidence = min(len(reasons) / 3, 1.0)
    
    return {
        "escalation_triggered": escalation_triggered,
        "reasons": reasons,
        "confidence": confidence,
        "matched_keywords": matched,
    }