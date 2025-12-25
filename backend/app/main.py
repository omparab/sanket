"""
Updated FastAPI Backend with ADK Integration
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
import os

# Import services
from backend.app.services.edge_ai_service import GeminiEdgeProcessor
from backend.app.services.quantum_service import QuantumService

# ============================================================================
# Initialize FastAPI
# ============================================================================

app = FastAPI(
    title="Sanket API with ADK",
    description="Quantum-Enhanced Epidemiology Network with AI Development Kit",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Initialize Services with ADK
# ============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "your-api-key")

# Initialize in correct order (quantum first, then swarm with quantum)
quantum_service = QuantumService()
gemini_processor = GeminiEdgeProcessor(api_key=GEMINI_API_KEY)

# Import and initialize ADK swarm service with quantum service
from backend.app.services.adk_swarm_service import ADKSwarmService
adk_swarm_service = ADKSwarmService(quantum_service=quantum_service)

# ============================================================================
# Data Models
# ============================================================================

class SymptomReportRequest(BaseModel):
    village_id: str
    symptoms: List[str]
    environmental_factors: Optional[List[str]] = []
    vital_signs: Optional[Dict] = {}

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/")
async def root():
    return {
        "service": "Sanket API with ADK Integration",
        "version": "2.0.0",
        "components": {
            "edge_ai": "Gemini API",
            "swarm": "ADK Multi-Agent System",
            "quantum": "TensorFlow Quantum"
        },
        "adk_features": [
            "Autonomous agent tools",
            "Multi-agent orchestration",
            "Workflow coordination",
            "Built-in consensus protocols"
        ]
    }

@app.get("/health")
async def health_check():
    adk_status = adk_swarm_service.get_network_status()
    
    return {
        "status": "healthy",
        "services": {
            "edge_ai": "operational",
            "adk_swarm": "operational",
            "quantum": "operational"
        },
        "adk_agents": {
            "total": adk_status['total_agents'],
            "active": adk_status['total_agents']
        }
    }

# ============================================================================
# Edge AI Endpoints (Gemini)
# ============================================================================

@app.post("/api/v1/edge/submit-report")
async def submit_symptom_report(
    village_id: str,
    symptoms: List[str],
    voice: Optional[UploadFile] = File(None),
    image: Optional[UploadFile] = File(None)
):
    """
    Process symptom report with optional voice/image analysis.
    
    Flow:
    1. Gemini processes voice/image (Edge AI) - ONLY for multimodal input
    2. Swarm agent analyzes symptoms (rule-based - NO LLM)
    3. If consensus, trigger quantum analysis
    """
    
    print(f"\n{'='*70}")
    print(f"📥 NEW SYMPTOM REPORT: Village {village_id}")
    print(f"   Symptoms: {symptoms}")
    print(f"   Has Voice: {voice is not None}")
    print(f"   Has Image: {image is not None}")
    print(f"{'='*70}")
    
    # STEP 1: Process with Gemini (Edge AI) - ONLY for voice/image
    edge_analysis = {}
    
    if voice:
        try:
            voice_bytes = await voice.read()
            print(f"🎤 Processing voice ({len(voice_bytes)} bytes)...")
            voice_result = await gemini_processor.process_voice(voice_bytes)
            edge_analysis['voice'] = voice_result
            # Add extracted symptoms
            extracted = voice_result.get('symptoms_extracted', [])
            if extracted:
                symptoms.extend(extracted)
                print(f"   Extracted symptoms: {extracted}")
        except Exception as e:
            print(f"❌ Voice processing error: {e}")
            edge_analysis['voice'] = {'error': str(e)}
    
    if image:
        try:
            image_bytes = await image.read()
            print(f"📷 Processing image ({len(image_bytes)} bytes)...")
            image_result = await gemini_processor.process_image(image_bytes)
            edge_analysis['image'] = image_result
            print(f"   Detected conditions: {image_result.get('detected_conditions', [])}")
            print(f"   Severity: {image_result.get('severity', 'unknown')}")
            print(f"   Description: {image_result.get('description', 'N/A')[:100]}...")
        except Exception as e:
            print(f"❌ Image processing error: {e}")
            edge_analysis['image'] = {'error': str(e)}
    
    # Normalize symptoms (uses Gemini for translation/normalization)
    try:
        normalized = await gemini_processor.normalize_symptoms(symptoms, {})
        edge_analysis['normalized'] = normalized
    except Exception as e:
        edge_analysis['normalized'] = {'error': str(e), 'original': symptoms}
    
    # STEP 2: Send to Swarm Agent (Rule-based - NO LLM)
    print(f"\n🤖 Sending to Swarm Agent (rule-based)...")
    
    adk_result = await adk_swarm_service.process_symptom_report(
        village_id=village_id,
        symptoms=symptoms,
        metadata={'edge_analysis': edge_analysis}
    )
    
    print(f"✓ Swarm Agent processed report")
    print(f"   Risk Level: {adk_result.get('agent_response', {}).get('risk_level', 'unknown')}")
    print(f"   Outbreak Belief: {adk_result.get('agent_response', {}).get('outbreak_belief', 0)}")
    print(f"   Actions: {adk_result.get('autonomous_actions_taken', [])}")
    
    # STEP 3: Check if quantum escalation triggered
    quantum_result = None
    if 'escalated_to_quantum' in adk_result.get('autonomous_actions_taken', []):
        print(f"\n⚛️ Quantum analysis triggered...")
        swarm_data = adk_swarm_service.get_network_status()
        quantum_result = await quantum_service.detect_outbreak_pattern(swarm_data)
        print(f"   Outbreak probability: {quantum_result.get('outbreak_probability', 0):.2f}")
    
    print(f"{'='*70}\n")
    
    return {
        'status': 'processed',
        'edge_analysis': edge_analysis,
        'swarm_response': adk_result,
        'quantum_analysis': quantum_result,
        'workflow': 'rule_based_swarm'
    }

# ============================================================================
# ADK Swarm Endpoints
# ============================================================================

@app.get("/api/v1/swarm/agents")
async def get_adk_agents():
    """Get all ADK agents status"""
    return adk_swarm_service.get_network_status()

@app.get("/api/v1/swarm/agent/{village_id}")
async def get_adk_agent_status(village_id: str):
    """Get specific ADK agent status"""
    agent_status = adk_swarm_service.get_agent_status(village_id)
    
    if not agent_status:
        raise HTTPException(404, "ADK agent not found")
    
    return agent_status

@app.post("/api/v1/swarm/trigger-workflow/{village_id}")
async def trigger_outbreak_workflow(village_id: str):
    """
    Manually trigger the outbreak detection workflow
    All ADK agents will coordinate through the workflow
    """
    result = await adk_swarm_service.trigger_outbreak_detection_workflow(village_id)
    
    return {
        'workflow': 'outbreak_detection',
        'triggered_by': village_id,
        'result': result
    }

@app.get("/api/v1/swarm/network-topology")
async def get_network_topology():
    """Get agent network connections"""
    status = adk_swarm_service.get_network_status()
    return {
        'topology': status['network_topology'],
        'total_agents': status['total_agents']
    }

@app.get("/api/v1/swarm/communications")
async def get_swarm_communications(limit: int = 50):
    """Get recent inter-agent communications for visualization"""
    return {
        'communications': adk_swarm_service.orchestrator.get_communication_log(limit),
        'total_agents': len(adk_swarm_service.orchestrator.agents),
        'topology': adk_swarm_service.orchestrator.network_topology
    }

# ============================================================================
# Quantum Endpoints (unchanged)
# ============================================================================

@app.post("/api/v1/quantum/analyze")
async def run_quantum_analysis():
    """Run quantum analysis on swarm data"""
    swarm_data = adk_swarm_service.get_network_status()
    
    pattern_result = await quantum_service.detect_outbreak_pattern(swarm_data)
    
    villages = [
        {'name': a['name'], 'outbreak_belief': a['outbreak_belief']}
        for a in swarm_data['agents'].values()
    ]
    allocation = await quantum_service.optimize_resource_allocation(
        villages=villages,
        resources={'ors': 1000, 'staff': 50, 'kits': 500}
    )
    
    return {
        'pattern_detection': pattern_result,
        'resource_allocation': allocation,
        'timestamp': datetime.now().isoformat()
    }

@app.get("/api/v1/quantum/insights")
async def get_quantum_insights():
    """Get latest quantum insights"""
    swarm_data = adk_swarm_service.get_network_status()
    return await quantum_service.detect_outbreak_pattern(swarm_data)

# ============================================================================
# Analytics Endpoints
# ============================================================================

@app.get("/api/v1/analytics/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics with ADK metrics"""
    swarm_status = adk_swarm_service.get_network_status()
    
    total_reports = sum(
        a['symptom_count'] for a in swarm_status['agents'].values()
    )
    
    high_risk_villages = sum(
        1 for a in swarm_status['agents'].values()
        if a['risk_level'] in ['high', 'critical']
    )
    
    avg_belief = sum(
        a['outbreak_belief'] for a in swarm_status['agents'].values()
    ) / len(swarm_status['agents']) if swarm_status['agents'] else 0
    
    return {
        'active_villages': swarm_status['total_agents'],
        'total_reports': total_reports,
        'high_risk_villages': high_risk_villages,
        'average_outbreak_belief': avg_belief,
        'system_status': 'operational',
        'framework': 'ADK Multi-Agent System'
    }

# ============================================================================
# Startup Event
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize system with ADK"""
    print("\n" + "="*70)
    print("🚀 SANKET SYSTEM STARTING (ADK INTEGRATION)")
    print("="*70)
    print("✓ Edge AI Service (Gemini) - Ready")
    print("✓ ADK Swarm Intelligence Network - Ready")
    
    status = adk_swarm_service.get_network_status()
    print(f"  - {status['total_agents']} ADK agents initialized")
    print(f"  - Network topology: {len(status['network_topology'])} connections")
    
    print("✓ Quantum Service (TensorFlow Quantum) - Ready")
    print("="*70)
    print("🆕 NEW: AI Development Kit (ADK) Features:")
    print("  - Autonomous agent tools")
    print("  - Multi-agent orchestration")
    print("  - Workflow coordination")
    print("  - Built-in consensus protocols")
    print("="*70)
    print("System operational at http://localhost:8000")
    print("API docs at http://localhost:8000/docs")
    print("="*70 + "\n")

# ============================================================================
# Run Server
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)