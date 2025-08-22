"""
Google Calendar API Routes
OAuth flow and sync endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from ..database import get_db
from ..models import User, TimeBlock
from ..security import get_current_user
from ..google_calendar import google_calendar_service
from ..schemas import TimeBlockResponse, CalendarSyncStatus

router = APIRouter(prefix="/api/v1/calendar", tags=["calendar"])

@router.get("/connect")
async def connect_google_calendar(current_user: User = Depends(get_current_user)):
    """Initiate Google Calendar OAuth flow"""
    try:
        auth_url = google_calendar_service.get_authorization_url(current_user.id)
        return {"auth_url": auth_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate auth URL: {str(e)}")

@router.post("/oauth/callback")
async def oauth_callback(
    code: str,
    state: str,
    error: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    success = google_calendar_service.handle_oauth_callback(code, state, db)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to process OAuth callback")
    
    return {"message": "Google Calendar connected successfully"}

@router.delete("/disconnect")
async def disconnect_google_calendar(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect Google Calendar"""
    success = google_calendar_service.disconnect_calendar(current_user.id, db)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to disconnect calendar")
    
    return {"message": "Google Calendar disconnected successfully"}

@router.get("/status")
async def get_calendar_status(current_user: User = Depends(get_current_user)):
    """Get Google Calendar connection status"""
    return CalendarSyncStatus(
        connected=current_user.google_calendar_connected,
        sync_enabled=current_user.google_calendar_sync_enabled,
        last_sync=None  # Will be implemented with sync scheduling
    )

@router.post("/sync/from-google")
async def sync_from_google(
    days_ahead: int = Query(30, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger sync from Google Calendar"""
    if not current_user.google_calendar_connected:
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    
    success = google_calendar_service.sync_from_google(current_user, db, days_ahead)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to sync from Google Calendar")
    
    return {"message": f"Synced events from Google Calendar for next {days_ahead} days"}

@router.post("/sync/to-google/{time_block_id}")
async def sync_to_google(
    time_block_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually sync specific time block to Google Calendar"""
    if not current_user.google_calendar_connected:
        raise HTTPException(status_code=400, detail="Google Calendar not connected")
    
    # Get time block
    time_block = db.query(TimeBlock).filter(
        TimeBlock.id == time_block_id,
        TimeBlock.user_id == current_user.id
    ).first()
    
    if not time_block:
        raise HTTPException(status_code=404, detail="Time block not found")
    
    try:
        if time_block.google_calendar_event_id:
            # Update existing event
            success = google_calendar_service.update_google_event(current_user, time_block)
        else:
            # Create new event
            event_id = google_calendar_service.create_google_event(current_user, time_block)
            if event_id:
                time_block.google_calendar_event_id = event_id
                success = True
            else:
                success = False
        
        if success:
            time_block.sync_status = 'synced'
            time_block.last_synced_at = datetime.utcnow()
            time_block.sync_error = None
        else:
            time_block.sync_status = 'error'
            time_block.sync_error = 'Failed to sync to Google Calendar'
        
        db.commit()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to sync to Google Calendar")
        
        return {"message": "Time block synced to Google Calendar successfully"}
        
    except Exception as e:
        time_block.sync_status = 'error'
        time_block.sync_error = str(e)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/time-blocks", response_model=List[TimeBlockResponse])
async def get_time_blocks(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get time blocks with optional date filtering"""
    query = db.query(TimeBlock).filter(TimeBlock.user_id == current_user.id)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(TimeBlock.start_time >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(TimeBlock.end_time <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    time_blocks = query.order_by(TimeBlock.start_time).all()
    return time_blocks

@router.post("/time-blocks", response_model=TimeBlockResponse)
async def create_time_block(
    time_block_data: dict,
    sync_to_google: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new time block with optional Google Calendar sync"""
    try:
        # Create time block
        new_block = TimeBlock(
            user_id=current_user.id,
            title=time_block_data['title'],
            description=time_block_data.get('description'),
            location=time_block_data.get('location'),
            start_time=datetime.fromisoformat(time_block_data['start_time']),
            end_time=datetime.fromisoformat(time_block_data['end_time']),
            all_day=time_block_data.get('all_day', False),
            block_type=time_block_data.get('block_type', 'work'),
            color=time_block_data.get('color', '#4A90E2'),
            is_flexible=time_block_data.get('is_flexible', False),
            buffer_time_minutes=time_block_data.get('buffer_time_minutes', 10),
            google_calendar_sync_enabled=sync_to_google and current_user.google_calendar_connected
        )
        
        db.add(new_block)
        db.commit()
        db.refresh(new_block)
        
        # Sync to Google Calendar if enabled
        if (sync_to_google and current_user.google_calendar_connected 
            and current_user.google_calendar_sync_enabled):
            
            event_id = google_calendar_service.create_google_event(current_user, new_block)
            if event_id:
                new_block.google_calendar_event_id = event_id
                new_block.sync_status = 'synced'
                new_block.last_synced_at = datetime.utcnow()
            else:
                new_block.sync_status = 'error'
                new_block.sync_error = 'Failed to sync to Google Calendar'
            
            db.commit()
        
        return new_block
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create time block: {str(e)}")

@router.put("/time-blocks/{time_block_id}", response_model=TimeBlockResponse)
async def update_time_block(
    time_block_id: str,
    time_block_data: dict,
    sync_to_google: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update time block with optional Google Calendar sync"""
    # Get time block
    time_block = db.query(TimeBlock).filter(
        TimeBlock.id == time_block_id,
        TimeBlock.user_id == current_user.id
    ).first()
    
    if not time_block:
        raise HTTPException(status_code=404, detail="Time block not found")
    
    try:
        # Update fields
        for field, value in time_block_data.items():
            if field in ['start_time', 'end_time']:
                setattr(time_block, field, datetime.fromisoformat(value))
            elif hasattr(time_block, field):
                setattr(time_block, field, value)
        
        time_block.updated_at = datetime.utcnow()
        
        # Sync to Google Calendar if enabled
        if (sync_to_google and current_user.google_calendar_connected 
            and current_user.google_calendar_sync_enabled
            and time_block.google_calendar_sync_enabled):
            
            success = google_calendar_service.update_google_event(current_user, time_block)
            if success:
                time_block.sync_status = 'synced'
                time_block.last_synced_at = datetime.utcnow()
                time_block.sync_error = None
            else:
                time_block.sync_status = 'error'
                time_block.sync_error = 'Failed to update in Google Calendar'
        
        db.commit()
        return time_block
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update time block: {str(e)}")

@router.delete("/time-blocks/{time_block_id}")
async def delete_time_block(
    time_block_id: str,
    delete_from_google: bool = Query(True),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete time block with optional Google Calendar sync"""
    # Get time block
    time_block = db.query(TimeBlock).filter(
        TimeBlock.id == time_block_id,
        TimeBlock.user_id == current_user.id
    ).first()
    
    if not time_block:
        raise HTTPException(status_code=404, detail="Time block not found")
    
    try:
        # Delete from Google Calendar if needed
        if (delete_from_google and current_user.google_calendar_connected 
            and time_block.google_calendar_event_id):
            
            google_calendar_service.delete_google_event(
                current_user, 
                time_block.google_calendar_event_id
            )
        
        # Delete from database
        db.delete(time_block)
        db.commit()
        
        return {"message": "Time block deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete time block: {str(e)}")