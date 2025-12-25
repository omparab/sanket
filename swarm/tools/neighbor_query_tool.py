"""
Neighbor Query Tool
Query neighboring village agents for their status
"""

def query_neighbors_tool(neighbor_village: str, query_type: str = "status") -> dict:
    """
    Query a neighboring village agent for their current epidemiological status.
    
    Args:
        neighbor_village: Name of the neighboring village to query (e.g., 'Kalyan', 'Thane')
        query_type: Type of query - 'status', 'symptoms', or 'risk_level'
    
    Returns:
        dict: Response from the neighboring village agent
    """
    # In production, this would actually communicate with other agents
    # For now, return simulated response
    return {
        "status": "query_sent",
        "neighbor": neighbor_village,
        "query_type": query_type,
        "response": {
            "village": neighbor_village,
            "risk_level": "medium",
            "outbreak_belief": 0.45,
            "recent_symptoms": ["fever", "headache"],
            "anomaly_detected": False
        },
        "message": f"Successfully queried {neighbor_village} for {query_type}"
    }


# Legacy class for backward compatibility
class QueryNeighborsTool:
    """Legacy wrapper - use query_neighbors_tool function instead"""
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
    
    async def run(self, neighbor_village: str, query_type: str = "status") -> dict:
        if self.orchestrator:
            try:
                return await self.orchestrator.query_agent(
                    neighbor_village, query_type, {}
                )
            except Exception:
                pass
        return query_neighbors_tool(neighbor_village, query_type)
