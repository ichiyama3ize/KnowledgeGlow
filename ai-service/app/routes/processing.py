#!/usr/bin/env python3
"""
AI Processing routes for KnowledgeGlow
"""

import time
import re
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
from urllib.parse import urlparse

router = APIRouter()

class ProcessingRequest(BaseModel):
    text: str = ""
    url: str = ""
    source_type: str = "text"  # text, url, file

class ProcessingResponse(BaseModel):
    summary: str
    tags: List[str]
    analysis: str
    status: str
    error: str = ""

def extract_text_from_url(url: str) -> str:
    """Extract text content from URL (simplified implementation)"""
    try:
        # Validate URL
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("Invalid URL format")
        
        # Simple HTTP request to get content
        headers = {
            'User-Agent': 'KnowledgeGlow/1.0 (Knowledge Management Bot)'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Simple text extraction (in production, use proper HTML parsing)
        content = response.text
        
        # Remove HTML tags (basic implementation)
        clean_text = re.sub(r'<[^>]+>', ' ', content)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Limit content length
        if len(clean_text) > 5000:
            clean_text = clean_text[:5000] + "..."
        
        return clean_text
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract content from URL: {str(e)}")

def mock_ai_processing(text: str) -> Dict[str, Any]:
    """Mock AI processing (replace with actual OpenAI integration)"""
    
    # Simulate processing time
    time.sleep(0.5)
    
    # Generate mock summary
    words = text.split()
    summary_length = min(50, len(words) // 3)
    summary = " ".join(words[:summary_length])
    if len(words) > summary_length:
        summary += "..."
    
    # Generate mock tags based on content
    tags = []
    text_lower = text.lower()
    
    # Technology tags
    if any(word in text_lower for word in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
        tags.append('AI')
    if any(word in text_lower for word in ['python', 'javascript', 'programming', 'code', 'development']):
        tags.append('Development')
    if any(word in text_lower for word in ['database', 'sql', 'data']):
        tags.append('Database')
    if any(word in text_lower for word in ['web', 'http', 'api', 'rest']):
        tags.append('Web')
    if any(word in text_lower for word in ['research', 'study', 'analysis']):
        tags.append('Research')
    
    # Default tags if none found
    if not tags:
        tags = ['General', 'Knowledge']
    
    # Generate mock analysis
    analysis = f"This content appears to be about {', '.join(tags).lower()}. "
    analysis += f"The text contains approximately {len(words)} words and covers "
    
    if 'ai' in text_lower or 'artificial intelligence' in text_lower:
        analysis += "artificial intelligence concepts and applications."
    elif 'development' in text_lower or 'programming' in text_lower:
        analysis += "software development practices and methodologies."
    elif 'database' in text_lower:
        analysis += "database design and management principles."
    else:
        analysis += "general knowledge and information."
    
    return {
        'summary': summary,
        'tags': tags,
        'analysis': analysis
    }

@router.post("/process", response_model=ProcessingResponse)
async def process_content(request: ProcessingRequest):
    """Process content with AI analysis"""
    
    try:
        start_time = time.time()
        
        # Get text content based on source type
        if request.source_type == "url" and request.url:
            text_content = extract_text_from_url(request.url)
        elif request.source_type == "text" and request.text:
            text_content = request.text
        else:
            raise HTTPException(status_code=400, detail="No valid content provided")
        
        # Validate content length
        if len(text_content.strip()) < 10:
            raise HTTPException(status_code=400, detail="Content too short for processing")
        
        # Process with AI (mock implementation)
        ai_result = mock_ai_processing(text_content)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return ProcessingResponse(
            summary=ai_result['summary'],
            tags=ai_result['tags'],
            analysis=ai_result['analysis'],
            status="success"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ProcessingResponse(
            summary="",
            tags=[],
            analysis="",
            status="error",
            error=str(e)
        )

@router.get("/process/health")
async def processing_health():
    """Health check for processing service"""
    return {
        "status": "healthy",
        "service": "ai-processing",
        "capabilities": ["text", "url"]
    }