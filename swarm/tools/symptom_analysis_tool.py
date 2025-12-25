"""
Symptom Analysis Tool
Simple Python function for ADK to use as a FunctionTool
"""

def analyze_symptoms_tool(symptoms: list, history_count: int = 0) -> dict:
    """
    Analyze symptom patterns for disease outbreak anomalies.
    
    Args:
        symptoms: List of reported symptoms (e.g., ['fever', 'headache', 'vomiting'])
        history_count: Number of previous symptom reports in this village
    
    Returns:
        dict: Analysis result containing anomaly detection and recommendations
    """
    # High-risk symptoms that indicate potential outbreak
    high_risk_symptoms = [
        'fever', 'vomiting', 'diarrhea', 'rash', 'breathing difficulty',
        'body pain', 'fatigue', 'nausea', 'cough'
    ]
    
    # Normalize and check symptoms
    symptoms_lower = [s.lower().strip() for s in symptoms]
    detected_high_risk = [s for s in symptoms_lower if s in high_risk_symptoms]
    
    # Calculate anomaly score
    anomaly_score = len(detected_high_risk) / max(len(symptoms), 1)
    
    # Determine if this is an anomaly
    is_anomaly = (
        anomaly_score > 0.5 or 
        history_count > 5 or 
        len(detected_high_risk) >= 3
    )
    
    # Determine risk level
    if anomaly_score > 0.7 or history_count > 10:
        risk_level = "critical"
    elif anomaly_score > 0.5 or history_count > 7:
        risk_level = "high"
    elif anomaly_score > 0.3 or history_count > 4:
        risk_level = "medium"
    else:
        risk_level = "low"
    
    return {
        "status": "analyzed",
        "anomaly_detected": is_anomaly,
        "anomaly_score": round(anomaly_score, 2),
        "risk_level": risk_level,
        "high_risk_symptoms_found": detected_high_risk,
        "total_symptoms": len(symptoms),
        "history_count": history_count,
        "recommendation": "escalate_to_neighbors" if is_anomaly else "continue_monitoring"
    }


# Legacy class for backward compatibility
class AnalyzeSymptomsToolTool:
    """Legacy wrapper - use analyze_symptoms_tool function instead"""
    def __init__(self):
        pass
    
    async def run(self, symptoms: list, history_count: int = 0) -> dict:
        return analyze_symptoms_tool(symptoms, history_count)
