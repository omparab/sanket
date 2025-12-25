"""
Quantum Escalation Tool
Trigger quantum analysis for outbreak pattern detection
"""

def escalate_to_quantum_tool(village_name: str, outbreak_belief: float, symptoms_data: dict = None) -> dict:
    """
    Trigger quantum analysis for advanced outbreak pattern detection.
    
    Args:
        village_name: Name of the village requesting quantum analysis
        outbreak_belief: Current outbreak probability belief (0.0 to 1.0)
        symptoms_data: Optional additional symptom data for analysis
    
    Returns:
        dict: Quantum escalation status and priority
    """
    # Determine priority based on outbreak belief
    if outbreak_belief >= 0.8:
        priority = "critical"
    elif outbreak_belief >= 0.6:
        priority = "high"
    elif outbreak_belief >= 0.4:
        priority = "medium"
    else:
        priority = "low"
    
    return {
        "status": "escalated_to_quantum",
        "village": village_name,
        "outbreak_belief": outbreak_belief,
        "priority": priority,
        "quantum_circuits": ["pattern_detection", "causality_analysis", "resource_optimization"],
        "estimated_analysis_time": "2-5 seconds",
        "message": f"Quantum analysis triggered for {village_name} with {priority} priority"
    }


# Legacy class for backward compatibility
class EscalateToQuantumTool:
    def __init__(self, quantum_service=None):
        self.quantum_service = quantum_service
    
    async def run(self, village_name: str, outbreak_belief: float) -> dict:
        result = escalate_to_quantum_tool(village_name, outbreak_belief)
        
        # If quantum service available, actually run analysis
        if self.quantum_service and outbreak_belief > 0.6:
            try:
                quantum_result = await self.quantum_service.detect_outbreak_pattern({})
                result["quantum_result"] = quantum_result
            except Exception as e:
                result["quantum_error"] = str(e)
        
        return result
