"""
Swarm Orchestrator (Rule-Based Multi-Agent Coordination)

Manages village agents and enables swarm intelligence through:
- Inter-agent communication (messages)
- Collective voting
- Network topology

NO LLM calls - pure rule-based coordination.
"""

from typing import Dict, List
from datetime import datetime
import asyncio


class SwarmOrchestrator:
    """
    Orchestrator for coordinating village swarm agents.
    Uses simple message passing and voting - NO LLM.
    """
    
    def __init__(self, quantum_service=None):
        self.quantum_service = quantum_service
        self.agents: Dict[str, any] = {}
        
        # Communication log for frontend visibility
        self.communication_log: List[Dict] = []
        
        # Network topology (which villages are neighbors)
        self.network_topology: Dict[str, List[str]] = {
            'v1': ['v2', 'v3'],        # Dharavi ↔ Kalyan, Thane
            'v2': ['v1', 'v3'],        # Kalyan ↔ Dharavi, Thane
            'v3': ['v1', 'v2', 'v4'],  # Thane ↔ all
            'v4': ['v3']               # Navi Mumbai ↔ Thane
        }
        
        self._initialize_swarm()
    
    def _initialize_swarm(self):
        """Create village agents."""
        from swarm.agents.village_adk_agent import create_village_agents
        
        self.agents = create_village_agents(
            orchestrator=self,
            quantum_service=self.quantum_service
        )
        
        print(f"✓ Swarm initialized: {len(self.agents)} rule-based agents")
    
    def _log_communication(self, from_agent: str, to_agent: str, msg_type: str, content: Dict):
        """Log inter-agent communication for frontend visibility."""
        self.communication_log.append({
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "type": msg_type,
            "content": content
        })
        # Keep only last 100 messages
        if len(self.communication_log) > 100:
            self.communication_log = self.communication_log[-100:]

    def _resolve_village_id(self, village_id: str) -> str:
        """Resolve village name to ID (accepts both 'Dharavi' and 'v1')."""
        if village_id in self.agents:
            return village_id
        
        # Match by name (case-insensitive)
        village_lower = village_id.lower().replace(' ', '_')
        for aid, agent in self.agents.items():
            if agent.village_name.lower().replace(' ', '_') == village_lower:
                return aid
            if agent.village_name.lower() == village_id.lower():
                return aid
        
        return None
    
    async def process_symptom_report(self, village_id: str, symptoms: List[str], metadata: Dict) -> Dict:
        """Process symptom report through the appropriate agent."""
        resolved_id = self._resolve_village_id(village_id)
        
        if not resolved_id:
            # Default to first agent
            resolved_id = list(self.agents.keys())[0] if self.agents else None
            if not resolved_id:
                raise ValueError("No agents available")
            print(f"⚠️ Village '{village_id}' not found, using: {resolved_id}")
        
        agent = self.agents[resolved_id]
        
        # Log the incoming report
        self._log_communication(
            "ASHA_Worker", agent.village_name,
            "symptom_report",
            {"symptoms": symptoms, "count": len(symptoms)}
        )
        
        # Process through rule-based agent (NO LLM)
        result = await agent.process_symptom_report(symptoms, metadata)
        
        # Log any neighbor queries that happened
        actions = result.get('actions_taken', [])
        if 'queried_neighbors' in actions:
            neighbors = self.network_topology.get(resolved_id, [])
            for n_id in neighbors:
                n_agent = self.agents.get(n_id)
                if n_agent:
                    self._log_communication(
                        agent.village_name, n_agent.village_name,
                        "status_query",
                        {"query": "outbreak_status", "belief": agent.outbreak_belief}
                    )
                    self._log_communication(
                        n_agent.village_name, agent.village_name,
                        "status_response",
                        {"belief": n_agent.outbreak_belief, "risk": n_agent.risk_level}
                    )
        
        if 'proposed_escalation' in actions:
            self._log_communication(
                agent.village_name, "ALL_NEIGHBORS",
                "consensus_proposal",
                {"proposal": "quantum_escalation", "belief": agent.outbreak_belief}
            )
        
        if 'escalated_to_quantum' in actions:
            self._log_communication(
                agent.village_name, "QUANTUM_SERVICE",
                "quantum_escalation",
                {"reason": "consensus_reached", "belief": agent.outbreak_belief}
            )
        
        return {
            'village': agent.village_name,
            'village_id': resolved_id,
            'agent_response': result,
            'autonomous_actions_taken': actions
        }

    async def query_agent(self, agent_id: str, query_type: str, context: Dict) -> Dict:
        """Query a specific agent."""
        resolved_id = self._resolve_village_id(agent_id)
        if not resolved_id:
            return {"error": f"Agent {agent_id} not found"}
        
        agent = self.agents[resolved_id]
        return await agent.receive_query(query_type, context)
    
    async def collect_votes(self, proposal: Dict, voters: List[str]) -> Dict:
        """Collect votes from agents using simple threshold logic."""
        votes = {}
        
        for voter_id in voters:
            resolved_id = self._resolve_village_id(voter_id)
            if resolved_id and resolved_id in self.agents:
                agent = self.agents[resolved_id]
                vote_result = agent.vote_on_proposal(proposal)
                votes[voter_id] = vote_result
                
                # Log the vote
                self._log_communication(
                    agent.village_name, proposal.get('proposer', 'unknown'),
                    "vote",
                    vote_result
                )
        
        return votes
    
    def get_communication_log(self, limit: int = 50) -> List[Dict]:
        """Get recent communication log for frontend."""
        return self.communication_log[-limit:]
    
    def get_network_status(self) -> Dict:
        """Get status of entire swarm network."""
        return {
            'total_agents': len(self.agents),
            'network_topology': self.network_topology,
            'agents': {
                aid: {
                    'name': agent.village_name,
                    'location': agent.location,
                    'outbreak_belief': round(agent.outbreak_belief, 3),
                    'risk_level': agent.risk_level,
                    'symptom_count': len(agent.symptom_history),
                    'neighbors': self.network_topology.get(aid, [])
                }
                for aid, agent in self.agents.items()
            },
            'recent_communications': len(self.communication_log)
        }
    
    def get_agent(self, village_id: str):
        """Get specific agent."""
        resolved_id = self._resolve_village_id(village_id)
        return self.agents.get(resolved_id) if resolved_id else None

    async def trigger_outbreak_detection_workflow(self, initiator_id: str) -> Dict:
        """
        Trigger outbreak detection across all agents.
        Uses collective voting - NO LLM.
        """
        resolved_id = self._resolve_village_id(initiator_id)
        if not resolved_id:
            return {"error": "Initiator not found"}
        
        initiator = self.agents[resolved_id]
        
        # Log workflow start
        self._log_communication(
            initiator.village_name, "ALL_AGENTS",
            "workflow_trigger",
            {"workflow": "outbreak_detection"}
        )
        
        # Gather beliefs from all agents
        beliefs = {}
        for aid, agent in self.agents.items():
            beliefs[aid] = {
                "village": agent.village_name,
                "belief": agent.outbreak_belief,
                "risk_level": agent.risk_level,
                "symptom_count": len(agent.symptom_history)
            }
            
            # Log belief sharing
            self._log_communication(
                agent.village_name, "ORCHESTRATOR",
                "belief_share",
                {"belief": round(agent.outbreak_belief, 3), "risk": agent.risk_level}
            )
        
        # Calculate collective belief (simple average)
        avg_belief = sum(b["belief"] for b in beliefs.values()) / len(beliefs)
        
        # Determine if quantum escalation needed
        high_risk_count = sum(1 for b in beliefs.values() if b["belief"] >= 0.6)
        escalate = high_risk_count >= 2 or avg_belief >= 0.7
        
        result = {
            "initiator": initiator.village_name,
            "collective_belief": round(avg_belief, 3),
            "high_risk_villages": high_risk_count,
            "escalate_to_quantum": escalate,
            "village_beliefs": beliefs
        }
        
        # Log decision
        self._log_communication(
            "ORCHESTRATOR", "ALL_AGENTS",
            "collective_decision",
            {"escalate": escalate, "avg_belief": round(avg_belief, 3)}
        )
        
        # Trigger quantum if needed
        if escalate and self.quantum_service:
            self._log_communication(
                "ORCHESTRATOR", "QUANTUM_SERVICE",
                "quantum_trigger",
                {"reason": "collective_decision", "belief": round(avg_belief, 3)}
            )
            
            quantum_result = await self.quantum_service.detect_outbreak_pattern(
                self.get_network_status()
            )
            result["quantum_analysis"] = quantum_result
            
            self._log_communication(
                "QUANTUM_SERVICE", "ALL_AGENTS",
                "quantum_result",
                {"outbreak_prob": quantum_result.get('outbreak_probability', 0)}
            )
        
        return result
