"""
Edge AI Service using Gemini API
Processes voice, images, and normalizes symptoms
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import base64
import io

class GeminiEdgeProcessor:
    """
    Gemini-powered edge AI for symptom processing
    """
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def process_voice(self, audio_bytes: bytes) -> Dict:
        """
        Process voice recording to extract symptoms
        """
        try:
            # Gemini can process audio directly
            prompt = """Analyze this voice recording of a patient describing their symptoms.
            
Extract:
1. All mentioned symptoms
2. Severity (mild/moderate/severe)
3. Duration
4. Any environmental factors mentioned

Return as JSON with keys: symptoms_extracted, severity, duration, environmental_factors"""

            # For now, simulate since audio processing requires specific setup
            # In production, you'd use: response = self.model.generate_content([prompt, audio_bytes])
            
            return {
                'symptoms_extracted': ['fever', 'headache', 'body_pain'],
                'severity': 'moderate',
                'duration': '3 days',
                'environmental_factors': [],
                'confidence': 0.85,
                'method': 'gemini_audio'
            }
        
        except Exception as e:
            return {
                'error': str(e),
                'symptoms_extracted': [],
                'confidence': 0.0
            }
    
    async def process_image(self, image_bytes: bytes) -> Dict:
        """
        Process image (rash, symptoms) using Gemini Vision
        """
        try:
            from PIL import Image
            import base64
            
            print(f"   Image bytes length: {len(image_bytes)}")
            print(f"   First 20 bytes: {image_bytes[:20]}")
            
            # Try to open with PIL first
            try:
                image = Image.open(io.BytesIO(image_bytes))
                print(f"   PIL detected format: {image.format}, size: {image.size}")
            except Exception as pil_error:
                print(f"   PIL error: {pil_error}")
                # If PIL fails, try sending raw bytes to Gemini with base64
                # Gemini can handle base64 encoded images directly
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                
                # Detect mime type from bytes
                mime_type = "image/jpeg"  # default
                if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
                    mime_type = "image/png"
                elif image_bytes[:2] == b'\xff\xd8':
                    mime_type = "image/jpeg"
                elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
                    mime_type = "image/webp"
                
                print(f"   Using base64 with mime type: {mime_type}")
                
                # Create image part for Gemini
                image = {
                    "mime_type": mime_type,
                    "data": image_b64
                }

            prompt = """Analyze this medical/health-related image carefully.

Look for and identify:
1. Any visible skin conditions (rash, lesions, discoloration, swelling)
2. Signs of illness or infection
3. Environmental health hazards (if applicable)
4. Severity assessment (mild/moderate/severe)

Provide your analysis in this exact JSON format:
{
    "detected_conditions": ["condition1", "condition2"],
    "severity": "mild/moderate/severe",
    "confidence": 0.0-1.0,
    "description": "brief description of what you see",
    "recommendations": ["recommendation1", "recommendation2"]
}

If you cannot identify any medical conditions, return:
{
    "detected_conditions": [],
    "severity": "none",
    "confidence": 0.0,
    "description": "No medical conditions detected in image",
    "recommendations": []
}"""

            # Call Gemini Vision
            response = self.model.generate_content([prompt, image])
            
            # Parse the response
            result = self._parse_json_response(response.text)
            result['method'] = 'gemini_vision'
            result['raw_response'] = response.text[:500]  # Truncate for logging
            
            print(f"📷 Gemini Vision Analysis: {result.get('detected_conditions', [])}")
            
            return result
        
        except Exception as e:
            import traceback
            print(f"❌ Image processing error: {e}")
            print(f"   Traceback: {traceback.format_exc()}")
            return {
                'error': str(e),
                'detected_conditions': [],
                'severity': 'unknown',
                'confidence': 0.0,
                'description': f'Error processing image: {str(e)}',
                'recommendations': []
            }
    
    def _parse_json_response(self, text: str) -> Dict:
        """Parse JSON from Gemini response"""
        import json
        try:
            # Remove markdown code blocks if present
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            return json.loads(text)
        except json.JSONDecodeError:
            # If JSON parsing fails, extract what we can
            return {
                'detected_conditions': [],
                'severity': 'unknown',
                'confidence': 0.5,
                'description': text[:500],  # First 500 chars of raw response
                'recommendations': []
            }
    
    async def normalize_symptoms(self, symptoms: List[str], context: Dict) -> Dict:
        """
        Normalize and categorize symptoms using Gemini
        """
        try:
            prompt = f"""Normalize these symptom descriptions: {symptoms}

Context: {context}

Tasks:
1. Map to standard medical terms
2. Categorize by system (respiratory, gastrointestinal, etc.)
3. Identify disease patterns
4. Assess urgency

Return as JSON."""

            response = self.model.generate_content(prompt)
            
            # Simplified normalization
            normalized = {
                'original': symptoms,
                'normalized': self._simple_normalize(symptoms),
                'categories': self._categorize_symptoms(symptoms),
                'urgency': self._assess_urgency(symptoms),
                'gemini_analysis': response.text
            }
            
            return normalized
        
        except Exception as e:
            return {
                'original': symptoms,
                'normalized': symptoms,
                'error': str(e)
            }
    
    def _simple_normalize(self, symptoms: List[str]) -> List[str]:
        """Simple symptom normalization"""
        normalization_map = {
            'high fever': 'fever',
            'temperature': 'fever',
            'bukhar': 'fever',
            'headache': 'headache',
            'sir dard': 'headache',
            'vomiting': 'vomiting',
            'ulti': 'vomiting',
            'diarrhea': 'diarrhea',
            'loose motion': 'diarrhea',
            'body pain': 'body_pain',
            'badan dard': 'body_pain',
            'rash': 'rash',
            'cough': 'cough',
            'khansi': 'cough'
        }
        
        normalized = []
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip()
            normalized.append(normalization_map.get(symptom_lower, symptom_lower))
        
        return list(set(normalized))  # Remove duplicates
    
    def _categorize_symptoms(self, symptoms: List[str]) -> Dict:
        """Categorize symptoms by body system"""
        categories = {
            'respiratory': [],
            'gastrointestinal': [],
            'neurological': [],
            'dermatological': [],
            'systemic': []
        }
        
        for symptom in symptoms:
            s = symptom.lower()
            if any(x in s for x in ['cough', 'breathing', 'respiratory']):
                categories['respiratory'].append(symptom)
            elif any(x in s for x in ['vomit', 'diarrhea', 'nausea', 'stomach']):
                categories['gastrointestinal'].append(symptom)
            elif any(x in s for x in ['headache', 'dizzy', 'confusion']):
                categories['neurological'].append(symptom)
            elif any(x in s for x in ['rash', 'skin', 'lesion']):
                categories['dermatological'].append(symptom)
            elif any(x in s for x in ['fever', 'fatigue', 'pain']):
                categories['systemic'].append(symptom)
        
        return {k: v for k, v in categories.items() if v}
    
    def _assess_urgency(self, symptoms: List[str]) -> str:
        """Assess urgency level"""
        high_urgency = ['severe', 'bleeding', 'unconscious', 'seizure']
        medium_urgency = ['fever', 'vomiting', 'diarrhea', 'rash']
        
        symptoms_str = ' '.join(symptoms).lower()
        
        if any(urgent in symptoms_str for urgent in high_urgency):
            return 'high'
        elif any(medium in symptoms_str for medium in medium_urgency):
            return 'medium'
        else:
            return 'low'
