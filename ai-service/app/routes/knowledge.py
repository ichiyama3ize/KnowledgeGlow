#!/usr/bin/env python3
"""
Knowledge management routes for KnowledgeGlow
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from database import KnowledgeDB

router = APIRouter()

class KnowledgeItemCreate(BaseModel):
    title: str
    content: str
    source_type: str = "text"
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    ai_analysis: Optional[str] = None

class KnowledgeItemUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    ai_analysis: Optional[str] = None

class KnowledgeItemResponse(BaseModel):
    id: int
    title: str
    content: str
    source_type: str
    source_url: Optional[str] = None
    tags: Optional[List[str]] = None
    summary: Optional[str] = None
    ai_analysis: Optional[str] = None
    created_at: str
    updated_at: str

@router.post("/knowledge", response_model=dict)
async def create_knowledge_item(item: KnowledgeItemCreate):
    """Create a new knowledge item"""
    try:
        item_id = KnowledgeDB.create_knowledge_item(
            title=item.title,
            content=item.content,
            source_type=item.source_type,
            source_url=item.source_url,
            tags=item.tags,
            summary=item.summary,
            ai_analysis=item.ai_analysis
        )
        
        return {
            "id": item_id,
            "message": "Knowledge item created successfully",
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create knowledge item: {str(e)}")

@router.get("/knowledge", response_model=List[dict])
async def get_knowledge_items(
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0, ge=0),
    search: Optional[str] = Query(default=None)
):
    """Get knowledge items with optional search"""
    try:
        if search:
            items = KnowledgeDB.search_knowledge_items(search, limit)
        else:
            items = KnowledgeDB.get_all_knowledge_items(limit, offset)
        
        return items
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge items: {str(e)}")

@router.get("/knowledge/{item_id}", response_model=dict)
async def get_knowledge_item(item_id: int):
    """Get a specific knowledge item"""
    try:
        item = KnowledgeDB.get_knowledge_item(item_id)
        
        if not item:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return item
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve knowledge item: {str(e)}")

@router.put("/knowledge/{item_id}", response_model=dict)
async def update_knowledge_item(item_id: int, item: KnowledgeItemUpdate):
    """Update a knowledge item"""
    try:
        # Convert to dict and remove None values
        update_data = {k: v for k, v in item.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        success = KnowledgeDB.update_knowledge_item(item_id, **update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return {
            "id": item_id,
            "message": "Knowledge item updated successfully",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update knowledge item: {str(e)}")

@router.delete("/knowledge/{item_id}", response_model=dict)
async def delete_knowledge_item(item_id: int):
    """Delete a knowledge item"""
    try:
        success = KnowledgeDB.delete_knowledge_item(item_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Knowledge item not found")
        
        return {
            "id": item_id,
            "message": "Knowledge item deleted successfully",
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete knowledge item: {str(e)}")

@router.get("/knowledge/search/{query}", response_model=List[dict])
async def search_knowledge_items(
    query: str,
    limit: int = Query(default=50, le=500)
):
    """Search knowledge items"""
    try:
        items = KnowledgeDB.search_knowledge_items(query, limit)
        return items
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/knowledge/stats/summary", response_model=dict)
async def get_knowledge_stats():
    """Get knowledge database statistics"""
    try:
        # Get total count
        items = KnowledgeDB.get_all_knowledge_items(limit=10000)  # Get all for counting
        total_items = len(items)
        
        # Count by source type
        source_types = {}
        tags_count = {}
        
        for item in items:
            # Count source types
            source_type = item.get('source_type', 'unknown')
            source_types[source_type] = source_types.get(source_type, 0) + 1
            
            # Count tags
            if item.get('tags'):
                for tag in item['tags']:
                    tags_count[tag] = tags_count.get(tag, 0) + 1
        
        return {
            "total_items": total_items,
            "source_types": source_types,
            "popular_tags": dict(sorted(tags_count.items(), key=lambda x: x[1], reverse=True)[:10]),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")