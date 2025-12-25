"""
Consensus Tools
Tools for proposing and voting on collective actions
"""

def propose_consensus_tool(proposal: str, risk_level: str, affected_villages: list = None) -> dict:
    """
    Propose an action to neighboring village agents for consensus voting.
    
    Args:
        proposal: Description of the proposed action (e.g., 'escalate_to_quantum', 'alert_health_officials')
        risk_level: Current risk assessment level ('low', 'medium', 'high', 'critical')
        affected_villages: List of villages that should vote on this proposal
    
    Returns:
        dict: Proposal status and voting information
    """
    if affected_villages is None:
        affected_villages = ['Dharavi', 'Kalyan', 'Thane', 'Navi Mumbai']
    
    # Determine votes needed based on risk level
    votes_needed = 2 if risk_level in ['high', 'critical'] else 3
    
    return {
        "status": "proposal_created",
        "proposal": proposal,
        "risk_level": risk_level,
        "affected_villages": affected_villages,
        "votes_needed": votes_needed,
        "votes_received": 0,
        "consensus_reached": False,
        "message": f"Proposal '{proposal}' sent to {len(affected_villages)} villages"
    }


def vote_tool(proposal_id: str, vote: str, confidence: float = 0.5) -> dict:
    """
    Cast a vote on a consensus proposal.
    
    Args:
        proposal_id: ID of the proposal to vote on
        vote: Vote decision - 'approve', 'reject', or 'abstain'
        confidence: Confidence level in the vote (0.0 to 1.0)
    
    Returns:
        dict: Vote confirmation
    """
    valid_votes = ['approve', 'reject', 'abstain']
    if vote.lower() not in valid_votes:
        return {
            "status": "error",
            "message": f"Invalid vote. Must be one of: {valid_votes}"
        }
    
    return {
        "status": "vote_cast",
        "proposal_id": proposal_id,
        "vote": vote.lower(),
        "confidence": min(max(confidence, 0.0), 1.0),
        "message": f"Vote '{vote}' recorded for proposal {proposal_id}"
    }


# Legacy classes for backward compatibility
class ProposeConsensusTool:
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
    
    async def run(self, proposal: str, risk_level: str) -> dict:
        return propose_consensus_tool(proposal, risk_level)


class VoteTool:
    def __init__(self):
        pass
    
    async def run(self, proposal_id: str, vote: str, confidence: float = 0.5) -> dict:
        return vote_tool(proposal_id, vote, confidence)
