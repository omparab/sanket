"""
Village Swarm Agent (Rule-Based Swarm Intelligence)

NO LLM calls for decision making!
Uses simple rules, thresholds, and inter-agent communication.

Gemini is ONLY used in edge/gemini_processor.py for:
- Voice transcription
- Image analysis  
- Language translation
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import asyncio

# ============================================================================
# Configuration Thresholds
# ============================================================================

THRESHOLDS = {
    'anomaly_score': 0.5,           # Score above this = anomaly detected
    'escalate_to_neighbors': 0.4,   # Belief above this = query neighbors
    'escalate_to_quantum': 0.7,     # Belief above this = trigger quantum
    'consensus_required': 0.6,      # Votes needed for consensus
    'high_risk_symptoms': ['fever', 'vomiting', 'diarrhea', 'rash', 'breathing difficulty'],
    'medium_risk_symptoms': ['headache', 'body pain', 'fatigue', 'nausea', 'cough'],
}


class VillageSwarmAgent:
    """
    Rule-based swarm agent for epidemiological monitoring.
    
    NO LLM/Gemini calls - uses simple if/else logic and math.
    Swarm intelligence emerges from:
    - Inter-agent communication (messages)
    - Collective voting
    - Simple rules producing complex behavior
    """
    
    def __init__(self, village_id: str, village_name: str, location: tuple,
                 orchestrator=None, quantum_service=None):
        self.village_id = village_id
        self.village_name = village_name
        self.location = location
        self.orchestrator = orchestrator
        self.quantum_service = quantum_service
        
        # Agent state
        self.symptom_history: List[Dict] = []
        self.outbreak_belief: float = 0.0
        self.risk_level: str = "normal"
        self.last_analysis: datetime = None
        
        # Communication state
        self.neighbor_beliefs: Dict[str, float] = {}
        self.pending_votes: Dict[str, str] = {}
        self.messages_received: List[Dict] = []

    # ========================================================================
    # CORE ANALYSIS (Simple Math - NO LLM)
    # ========================================================================
    
    def analyze_symptoms(self, symptoms: List[str]) -> Dict[str, Any]:
        """
        Analyze symptoms using simple scoring rules.
        NO LLM - just math and thresholds.
        """
        symptoms_lower = [s.lower().strip() for s in symptoms]
        
        # Count high-risk and medium-risk symptoms
        high_risk_count = sum(1 for s in symptoms_lower 
                             if s in THRESHOLDS['high_risk_symptoms'])
        medium_risk_count = sum(1 for s in symptoms_lower 
                               if s in THRESHOLDS['medium_risk_symptoms'])
        
        # Calculate anomaly score (simple weighted formula)
        total = len(symptoms_lower) or 1
        anomaly_score = (high_risk_count * 1.0 + medium_risk_count * 0.5) / total
        
        # Determine if anomaly
        is_anomaly = anomaly_score >= THRESHOLDS['anomaly_score']
        
        return {
            "anomaly_detected": is_anomaly,
            "anomaly_score": round(anomaly_score, 3),
            "high_risk_count": high_risk_count,
            "medium_risk_count": medium_risk_count,
            "total_symptoms": len(symptoms_lower)
        }
    
    def update_belief(self) -> float:
        """
        Update outbreak belief using Bayesian-like update.
        Simple math formula - NO LLM.
        """
        # Base belief from symptom history
        history_factor = min(len(self.symptom_history) / 10.0, 1.0)
        
        # Recent anomaly factor (last 5 reports)
        recent = self.symptom_history[-5:] if self.symptom_history else []
        anomaly_count = sum(1 for r in recent if r.get('anomaly_detected', False))
        anomaly_factor = anomaly_count / 5.0 if recent else 0
        
        # Neighbor influence (swarm behavior)
        neighbor_factor = 0
        if self.neighbor_beliefs:
            neighbor_factor = sum(self.neighbor_beliefs.values()) / len(self.neighbor_beliefs)
        
        # Combined belief (weighted average)
        self.outbreak_belief = (
            0.4 * history_factor +
            0.4 * anomaly_factor +
            0.2 * neighbor_factor
        )
        
        # Update risk level based on belief
        self._update_risk_level()
        
        return self.outbreak_belief

    def _update_risk_level(self):
        """Update risk level based on outbreak belief thresholds."""
        if self.outbreak_belief >= 0.8:
            self.risk_level = "critical"
        elif self.outbreak_belief >= 0.6:
            self.risk_level = "high"
        elif self.outbreak_belief >= 0.4:
            self.risk_level = "medium"
        elif self.outbreak_belief >= 0.2:
            self.risk_level = "low"
        else:
            self.risk_level = "normal"
    
    # ========================================================================
    # MAIN PROCESSING (Rule-Based Decision Tree)
    # ========================================================================
    
    async def process_symptom_report(self, symptoms: List[str], metadata: Dict) -> Dict:
        """
        Process symptom report using rule-based logic.
        
        Decision tree (NO LLM):
        1. Analyze symptoms → calculate anomaly score
        2. Update belief → simple math
        3. If belief > threshold → query neighbors
        4. If consensus → escalate to quantum
        """
        # Step 1: Analyze symptoms (simple math)
        analysis = self.analyze_symptoms(symptoms)
        
        # Store in history
        self.symptom_history.append({
            'symptoms': symptoms,
            'metadata': metadata,
            'timestamp': datetime.now().isoformat(),
            **analysis
        })
        
        # Step 2: Update belief (Bayesian-like formula)
        self.update_belief()
        
        # Step 3: Decide actions based on thresholds
        actions_taken = []
        
        # Rule: If belief > neighbor threshold, query neighbors
        if self.outbreak_belief >= THRESHOLDS['escalate_to_neighbors']:
            await self._query_neighbors()
            actions_taken.append("queried_neighbors")
        
        # Rule: If belief > quantum threshold, check consensus then escalate
        if self.outbreak_belief >= THRESHOLDS['escalate_to_quantum']:
            consensus = self._check_consensus()
            if consensus:
                await self._escalate_to_quantum()
                actions_taken.append("escalated_to_quantum")
            else:
                await self._propose_escalation()
                actions_taken.append("proposed_escalation")
        
        self.last_analysis = datetime.now()
        
        return {
            "village": self.village_name,
            "analysis": analysis,
            "outbreak_belief": round(self.outbreak_belief, 3),
            "risk_level": self.risk_level,
            "actions_taken": actions_taken,
            "symptom_count": len(self.symptom_history)
        }

    # ========================================================================
    # INTER-AGENT COMMUNICATION (Swarm Behavior)
    # ========================================================================
    
    async def _query_neighbors(self):
        """Query neighboring agents for their beliefs."""
        if not self.orchestrator:
            return
        
        neighbors = self.orchestrator.network_topology.get(self.village_id, [])
        
        for neighbor_id in neighbors:
            try:
                response = await self.orchestrator.query_agent(
                    neighbor_id, "status", {"from": self.village_id}
                )
                if response and 'outbreak_belief' in response:
                    self.neighbor_beliefs[neighbor_id] = response['outbreak_belief']
            except Exception:
                pass
    
    async def _propose_escalation(self):
        """Propose quantum escalation to neighbors for voting."""
        if not self.orchestrator:
            return
        
        neighbors = self.orchestrator.network_topology.get(self.village_id, [])
        
        proposal = {
            "type": "quantum_escalation",
            "proposer": self.village_id,
            "belief": self.outbreak_belief
        }
        
        # Collect votes from neighbors
        votes = await self.orchestrator.collect_votes(proposal, neighbors)
        self.pending_votes = votes
    
    def _check_consensus(self) -> bool:
        """Check if consensus reached based on neighbor beliefs."""
        if not self.neighbor_beliefs:
            # No neighbors queried yet, use own belief
            return self.outbreak_belief >= THRESHOLDS['escalate_to_quantum']
        
        # Count how many neighbors also have high belief
        high_belief_count = sum(
            1 for b in self.neighbor_beliefs.values() 
            if b >= THRESHOLDS['escalate_to_neighbors']
        )
        
        # Consensus if majority agrees
        total = len(self.neighbor_beliefs) + 1  # +1 for self
        consensus_ratio = (high_belief_count + 1) / total  # +1 for self
        
        return consensus_ratio >= THRESHOLDS['consensus_required']
    
    async def _escalate_to_quantum(self):
        """Trigger quantum analysis."""
        if self.quantum_service:
            try:
                # Gather swarm data for quantum analysis
                swarm_data = self.orchestrator.get_network_status() if self.orchestrator else {}
                await self.quantum_service.detect_outbreak_pattern(swarm_data)
            except Exception:
                pass

    # ========================================================================
    # MESSAGE HANDLING (Swarm Communication)
    # ========================================================================
    
    async def receive_query(self, query_type: str, context: Dict) -> Dict:
        """Handle query from another agent."""
        self.messages_received.append({
            "type": query_type,
            "context": context,
            "timestamp": datetime.now().isoformat()
        })
        
        # Return current status (no LLM needed)
        return {
            "village": self.village_name,
            "outbreak_belief": self.outbreak_belief,
            "risk_level": self.risk_level,
            "symptom_count": len(self.symptom_history),
            "anomaly_detected": self.risk_level in ['high', 'critical']
        }
    
    def vote_on_proposal(self, proposal: Dict) -> Dict:
        """
        Vote on a proposal using simple threshold logic.
        NO LLM - just compare beliefs.
        """
        proposal_type = proposal.get("type", "")
        proposer_belief = proposal.get("belief", 0)
        
        # Simple voting rule: approve if our belief is also high
        if proposal_type == "quantum_escalation":
            approve = self.outbreak_belief >= THRESHOLDS['escalate_to_neighbors']
        else:
            approve = self.outbreak_belief >= 0.5
        
        return {
            "vote": "approve" if approve else "reject",
            "voter": self.village_id,
            "confidence": self.outbreak_belief
        }
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "village_id": self.village_id,
            "village_name": self.village_name,
            "location": self.location,
            "outbreak_belief": self.outbreak_belief,
            "risk_level": self.risk_level,
            "symptom_count": len(self.symptom_history),
            "neighbor_beliefs": self.neighbor_beliefs,
            "last_analysis": self.last_analysis.isoformat() if self.last_analysis else None
        }


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_village_agents(orchestrator=None, quantum_service=None) -> Dict[str, VillageSwarmAgent]:
    """Create all village swarm agents."""
    villages = [
        ("v1", "Dharavi", (19.04, 72.86)),
        ("v2", "Kalyan", (19.24, 73.14)),
        ("v3", "Thane", (19.22, 72.97)),
        ("v4", "Navi Mumbai", (19.03, 73.01))
    ]
    
    agents = {}
    for vid, vname, location in villages:
        agents[vid] = VillageSwarmAgent(vid, vname, location, orchestrator, quantum_service)
    
    return agents


# Alias for backward compatibility
VillageADKAgent = VillageSwarmAgent
