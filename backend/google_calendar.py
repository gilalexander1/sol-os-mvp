"""
Google Calendar Integration Service
OAuth 2.0 authentication and two-way sync functionality
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from sqlalchemy.orm import Session
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .database import get_db
from .models import User, TimeBlock
from .encryption import encrypt_data, decrypt_data
from .config import settings

logger = logging.getLogger(__name__)

class GoogleCalendarService:
    """Service for Google Calendar OAuth and sync operations"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly',
        'https://www.googleapis.com/auth/calendar.events'
    ]
    
    def __init__(self):
        self.client_config = {
            "web": {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [f"{settings.FRONTEND_URL}/auth/google/callback"]
            }
        }
    
    def get_authorization_url(self, user_id: str) -> str:
        """Generate OAuth 2.0 authorization URL"""
        try:
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=f"{settings.FRONTEND_URL}/auth/google/callback"
            )
            flow.state = user_id  # Pass user_id in state for callback
            
            authorization_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'  # Force consent to get refresh token
            )
            
            return authorization_url
        except Exception as e:
            logger.error(f"Error generating authorization URL: {str(e)}")
            raise
    
    def handle_oauth_callback(self, code: str, state: str, db: Session) -> bool:
        """Handle OAuth callback and store encrypted tokens"""
        try:
            user_id = state
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User not found for OAuth callback: {user_id}")
                return False
            
            flow = Flow.from_client_config(
                self.client_config,
                scopes=self.SCOPES,
                redirect_uri=f"{settings.FRONTEND_URL}/auth/google/callback"
            )
            
            # Exchange authorization code for tokens
            flow.fetch_token(code=code)
            credentials = flow.credentials
            
            # Encrypt and store tokens
            access_token_encrypted = encrypt_data(
                credentials.token,
                user.encryption_salt
            )
            refresh_token_encrypted = encrypt_data(
                credentials.refresh_token,
                user.encryption_salt
            ) if credentials.refresh_token else None
            
            # Update user record
            user.google_calendar_access_token = access_token_encrypted
            user.google_calendar_refresh_token = refresh_token_encrypted
            user.google_calendar_token_expires_at = credentials.expiry
            user.google_calendar_connected = True
            user.updated_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Google Calendar connected for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {str(e)}")
            db.rollback()
            return False
    
    def get_credentials(self, user: User) -> Optional[Credentials]:
        """Get valid Google credentials for user"""
        try:
            if not user.google_calendar_connected:
                return None
            
            # Decrypt tokens
            access_token = decrypt_data(
                user.google_calendar_access_token,
                user.encryption_salt
            )
            
            refresh_token = decrypt_data(
                user.google_calendar_refresh_token,
                user.encryption_salt
            ) if user.google_calendar_refresh_token else None
            
            # Create credentials object
            credentials = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                expiry=user.google_calendar_token_expires_at
            )
            
            # Refresh if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Update stored tokens
                db = next(get_db())
                user.google_calendar_access_token = encrypt_data(
                    credentials.token,
                    user.encryption_salt
                )
                user.google_calendar_token_expires_at = credentials.expiry
                db.commit()
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error getting credentials: {str(e)}")
            return None
    
    def disconnect_calendar(self, user_id: str, db: Session) -> bool:
        """Disconnect Google Calendar for user"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            # Clear OAuth data
            user.google_calendar_access_token = None
            user.google_calendar_refresh_token = None
            user.google_calendar_token_expires_at = None
            user.google_calendar_connected = False
            user.google_calendar_sync_enabled = False
            user.updated_at = datetime.utcnow()
            
            # Clear sync data from time blocks
            time_blocks = db.query(TimeBlock).filter(TimeBlock.user_id == user_id).all()
            for block in time_blocks:
                block.google_calendar_event_id = None
                block.google_calendar_sync_enabled = False
                block.sync_status = 'disconnected'
            
            db.commit()
            logger.info(f"Google Calendar disconnected for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting calendar: {str(e)}")
            db.rollback()
            return False
    
    def create_google_event(self, user: User, time_block: TimeBlock) -> Optional[str]:
        """Create event in Google Calendar"""
        try:
            credentials = self.get_credentials(user)
            if not credentials:
                return None
            
            service = build('calendar', 'v3', credentials=credentials)
            
            # Prepare event data
            event = {
                'summary': time_block.title,
                'description': time_block.description or '',
                'location': time_block.location or '',
                'start': {
                    'dateTime': time_block.start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': time_block.end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if time_block.all_day:
                event['start'] = {
                    'date': time_block.start_time.date().isoformat(),
                }
                event['end'] = {
                    'date': time_block.end_time.date().isoformat(),
                }
            
            # Create event
            created_event = service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return created_event['id']
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating Google event: {str(e)}")
            return None
    
    def update_google_event(self, user: User, time_block: TimeBlock) -> bool:
        """Update event in Google Calendar"""
        try:
            if not time_block.google_calendar_event_id:
                return False
            
            credentials = self.get_credentials(user)
            if not credentials:
                return False
            
            service = build('calendar', 'v3', credentials=credentials)
            
            # Prepare event data
            event = {
                'summary': time_block.title,
                'description': time_block.description or '',
                'location': time_block.location or '',
                'start': {
                    'dateTime': time_block.start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': time_block.end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            if time_block.all_day:
                event['start'] = {
                    'date': time_block.start_time.date().isoformat(),
                }
                event['end'] = {
                    'date': time_block.end_time.date().isoformat(),
                }
            
            # Update event
            service.events().update(
                calendarId='primary',
                eventId=time_block.google_calendar_event_id,
                body=event
            ).execute()
            
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error updating Google event: {str(e)}")
            return False
    
    def delete_google_event(self, user: User, event_id: str) -> bool:
        """Delete event from Google Calendar"""
        try:
            credentials = self.get_credentials(user)
            if not credentials:
                return False
            
            service = build('calendar', 'v3', credentials=credentials)
            
            service.events().delete(
                calendarId='primary',
                eventId=event_id
            ).execute()
            
            return True
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting Google event: {str(e)}")
            return False
    
    def sync_from_google(self, user: User, db: Session, days_ahead: int = 30) -> bool:
        """Sync events from Google Calendar to Sol OS"""
        try:
            credentials = self.get_credentials(user)
            if not credentials:
                return False
            
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get events from next 30 days
            now = datetime.utcnow()
            time_max = (now + timedelta(days=days_ahead)).isoformat() + 'Z'
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=now.isoformat() + 'Z',
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            google_events = events_result.get('items', [])
            
            # Process each Google event
            for g_event in google_events:
                # Skip if event was created by Sol OS
                if g_event.get('description', '').startswith('[Sol OS]'):
                    continue
                
                # Check if we already have this event
                existing_block = db.query(TimeBlock).filter(
                    TimeBlock.user_id == user.id,
                    TimeBlock.google_calendar_event_id == g_event['id']
                ).first()
                
                if existing_block:
                    # Update existing block
                    self._update_time_block_from_google_event(existing_block, g_event)
                else:
                    # Create new block
                    new_block = self._create_time_block_from_google_event(user.id, g_event)
                    db.add(new_block)
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error syncing from Google: {str(e)}")
            db.rollback()
            return False
    
    def _create_time_block_from_google_event(self, user_id: str, g_event: Dict[str, Any]) -> TimeBlock:
        """Create TimeBlock from Google Calendar event"""
        start_time = self._parse_google_datetime(g_event['start'])
        end_time = self._parse_google_datetime(g_event['end'])
        
        return TimeBlock(
            user_id=user_id,
            title=g_event.get('summary', 'Untitled Event'),
            description=g_event.get('description', ''),
            location=g_event.get('location', ''),
            start_time=start_time,
            end_time=end_time,
            all_day='date' in g_event['start'],
            google_calendar_event_id=g_event['id'],
            google_calendar_sync_enabled=True,
            sync_status='synced',
            last_synced_at=datetime.utcnow(),
            block_type='external',
            color='#34D399'  # Green for external events
        )
    
    def _update_time_block_from_google_event(self, time_block: TimeBlock, g_event: Dict[str, Any]):
        """Update TimeBlock with data from Google Calendar event"""
        time_block.title = g_event.get('summary', 'Untitled Event')
        time_block.description = g_event.get('description', '')
        time_block.location = g_event.get('location', '')
        time_block.start_time = self._parse_google_datetime(g_event['start'])
        time_block.end_time = self._parse_google_datetime(g_event['end'])
        time_block.all_day = 'date' in g_event['start']
        time_block.sync_status = 'synced'
        time_block.last_synced_at = datetime.utcnow()
    
    def _parse_google_datetime(self, dt_info: Dict[str, str]) -> datetime:
        """Parse Google Calendar datetime format"""
        if 'dateTime' in dt_info:
            # Regular event with time
            dt_str = dt_info['dateTime']
            # Remove timezone info and parse
            if 'T' in dt_str:
                dt_str = dt_str.split('T')[0] + 'T' + dt_str.split('T')[1].split('+')[0].split('-')[0].split('Z')[0]
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00')).replace(tzinfo=None)
        else:
            # All-day event
            return datetime.fromisoformat(dt_info['date']).replace(hour=9)  # Default to 9 AM

# Global service instance
google_calendar_service = GoogleCalendarService()