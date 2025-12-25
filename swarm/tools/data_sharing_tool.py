"""
Data Sharing Tool
Share anonymized symptom data with neighboring villages
"""

def share_data_tool(agent_id: str, data_type: str, anonymized_data: dict = None) -> dict:
    """
    Share anonymized epidemiological data with neighboring village agents.
    
    Args:
        agent_id: ID of the agent sharing data
        data_type: Type of data being shared ('symptoms', 'risk_assessment', 'outbreak_belief')
        anonymized_data: The anonymized data to share
    
    Returns:
        dict: Data sharing confirmation
    """
    if anonymized_data is None:
        anonymized_data = {}
    
    valid_data_types = ['symptoms', 'risk_assessment', 'outbreak_belief', 'trend_analysis']
    if data_type not in valid_data_types:
        return {
            "status": "error",
            "message": f"Invalid data type. Must be one of: {valid_data_types}"
        }
    
    return {
        "status": "data_shared",
        "agent_id": agent_id,
        "data_type": data_type,
        "data_size": len(str(anonymized_data)),
        "recipients": ["neighboring_agents"],
        "privacy_preserved": True,
        "message": f"Anonymized {data_type} data shared successfully"
    }


# Legacy class for backward compatibility
class ShareDataTool:
    def __init__(self, agent_id: str = "unknown"):
        self.agent_id = agent_id
    
    async def run(self, data_type: str, anonymized_data: dict = None) -> dict:
        return share_data_tool(self.agent_id, data_type, anonymized_data)
