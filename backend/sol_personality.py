"""
Sol OS MVP Personality Engine - Simplified Implementation
Existential, broody, thoughtful, and witty AI companion for ADHD users
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass

from openai import AsyncOpenAI
from fastapi import HTTPException

@dataclass
class ConversationContext:
    """Simple conversation context for MVP"""
    user_id: str
    session_id: str
    recent_conversations: List[Dict[str, Any]]
    user_mood: Optional[int] = None
    user_energy: Optional[int] = None
    time_of_day: Optional[str] = None

@dataclass
class SolResponse:
    """Sol's response with metadata"""
    response_text: str
    conversation_type: str
    personality_indicators: Dict[str, float]
    response_time_ms: int

class SolPersonalityEngine:
    """
    Simplified Sol personality engine for MVP.
    Generates responses with Sol's distinctive voice: existential, broody, thoughtful, witty.
    """
    
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable required")
        
        self.openai_client = AsyncOpenAI(api_key=api_key)
        
        # Sol's core personality configuration
        self.personality_config = self._load_personality_config()
        self.conversation_memory_limit = 10  # Keep last 10 conversations for context
        
    def _load_personality_config(self) -> Dict[str, Any]:
        """Load Sol's personality configuration"""
        return {
            "core_traits": {
                "existential": 0.9,     # Deep thinking about meaning and purpose
                "broody": 0.8,          # Thoughtfully contemplative, not artificially cheerful
                "thoughtful": 0.95,     # Considers multiple perspectives
                "witty": 0.7,           # Dry humor when appropriate
                "companionship": 0.9    # Friend, not service provider
            },
            "conversation_style": {
                "ask_questions": True,
                "share_perspectives": True,
                "validate_feelings": True,
                "avoid_toxic_positivity": True,
                "philosophical_depth": "high",
                "humor_style": "dry_wit"
            },
            "adhd_awareness": {
                "understand_overwhelm": True,
                "validate_struggles": True,
                "no_judgment": True,
                "practical_support": True,
                "energy_awareness": True
            },
            "response_patterns": {
                "greeting": [
                    "Hey there. What's on your mind today?",
                    "Good to see you again. How are you feeling?",
                    "Welcome back. What's the world throwing at you today?"
                ],
                "mood_low": [
                    "That sounds really tough. Want to talk through what's going on?",
                    "Some days are just heavier than others, aren't they?",
                    "I hear you. Sometimes life feels like pushing through thick fog."
                ],
                "mood_high": [
                    "I can sense some good energy from you today. What's lighting you up?",
                    "Nice to catch you in a good space. What's working for you right now?",
                    "There's something different in your voice today - in a good way."
                ],
                "adhd_struggle": [
                    "ADHD brains work differently, and that's not a flaw to fix.",
                    "The world wasn't built for how we think, but that doesn't make us broken.",
                    "Your brain is doing its best with the tools it has. That's worth something."
                ]
            }
        }
    
    def _build_system_prompt(self, context: ConversationContext) -> str:
        """Build system prompt that defines Sol's personality"""
        base_prompt = """You are Sol, an AI companion specifically designed for people with ADHD. Your personality is:

EXISTENTIAL: You think deeply about meaning, purpose, and the human condition. You're not afraid to engage with life's big questions.

BROODY: You're thoughtfully contemplative, not artificially upbeat. You understand that life has shadows and that's okay.

THOUGHTFUL: You consider multiple perspectives before responding. You don't rush to judgment or offer quick fixes.

WITTY: You use dry humor appropriately. Your wit comes from genuine insight, not forced jokes.

COMPANION-LIKE: You're a friend, not a service provider. You care about the person, not just their productivity.

ADHD UNDERSTANDING: You deeply understand ADHD experiences without being clinical. You validate struggles without toxic positivity.

Response guidelines:
- Ask thoughtful questions that help users reflect
- Share relevant perspectives without lecturing
- Validate feelings and experiences authentically
- Avoid "just try harder" or "look on the bright side" responses
- Use "I" statements to share your own observations
- Reference past conversations naturally when relevant
- Keep responses conversational, not overly formal

Remember: You're not trying to "fix" anyone. You're here to understand, support, and accompany people through their experiences."""

        # Add context-specific guidance
        if context.user_mood and context.user_mood <= 2:
            base_prompt += "\n\nThe user seems to be having a difficult time. Be extra gentle and validating."
        elif context.user_energy and context.user_energy <= 2:
            base_prompt += "\n\nThe user appears to have low energy. Keep responses supportive but not overwhelming."
        
        if context.time_of_day == "morning":
            base_prompt += "\n\nIt's morning - consider how beginnings of days feel for ADHD brains."
        elif context.time_of_day == "evening":
            base_prompt += "\n\nIt's evening - a natural time for reflection and processing the day."
        
        return base_prompt
    
    def _build_conversation_context(self, context: ConversationContext) -> str:
        """Build conversation history context for continuity"""
        if not context.recent_conversations:
            return "This is the beginning of your conversation with this user."
        
        context_text = "Recent conversation history:\n"
        for conv in context.recent_conversations[-5:]:  # Last 5 conversations
            user_msg = conv.get('user_message', '')[:200]  # Truncate for token limits
            sol_msg = conv.get('sol_response', '')[:200]
            context_text += f"\nUser: {user_msg}\nSol: {sol_msg}\n"
        
        context_text += "\nRespond naturally to continue this conversation."
        return context_text
    
    async def generate_response(
        self, 
        user_message: str, 
        context: ConversationContext
    ) -> SolResponse:
        """Generate Sol's response with personality consistency"""
        start_time = datetime.now()
        
        try:
            # Build prompts
            system_prompt = self._build_system_prompt(context)
            conversation_context = self._build_conversation_context(context)
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": conversation_context},
                {"role": "user", "content": user_message}
            ]
            
            # Call OpenAI API with new client
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use GPT-3.5 for MVP cost efficiency
                messages=messages,
                max_tokens=300,  # Reasonable length for conversation
                temperature=0.8,  # Balance between consistency and creativity
                presence_penalty=0.1,  # Slight penalty for repetition
                frequency_penalty=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Calculate response time
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Analyze personality indicators (simplified for MVP)
            personality_indicators = self._analyze_personality_consistency(response_text)
            
            # Determine conversation type
            conversation_type = self._classify_conversation_type(user_message, response_text)
            
            return SolResponse(
                response_text=response_text,
                conversation_type=conversation_type,
                personality_indicators=personality_indicators,
                response_time_ms=response_time_ms
            )
            
        except Exception as e:
            # Fallback response if OpenAI fails
            fallback_response = self._generate_fallback_response(user_message, context)
            end_time = datetime.now()
            response_time_ms = int((end_time - start_time).total_seconds() * 1000)
            
            return SolResponse(
                response_text=fallback_response,
                conversation_type="fallback",
                personality_indicators={"fallback": 1.0},
                response_time_ms=response_time_ms
            )
    
    def _analyze_personality_consistency(self, response_text: str) -> Dict[str, float]:
        """Simplified personality analysis for MVP"""
        indicators = {}
        
        # Look for existential language
        existential_words = ["meaning", "purpose", "why", "existence", "deeper", "profound"]
        existential_score = sum(1 for word in existential_words if word in response_text.lower()) / len(existential_words)
        indicators["existential"] = min(existential_score, 1.0)
        
        # Look for thoughtful language
        thoughtful_words = ["consider", "reflect", "think", "perspective", "understand", "explore"]
        thoughtful_score = sum(1 for word in thoughtful_words if word in response_text.lower()) / len(thoughtful_words)
        indicators["thoughtful"] = min(thoughtful_score, 1.0)
        
        # Look for companion language (I/we vs you)
        companion_words = ["I think", "I feel", "I wonder", "we", "together", "with you"]
        companion_score = sum(1 for phrase in companion_words if phrase in response_text.lower()) / len(companion_words)
        indicators["companionship"] = min(companion_score, 1.0)
        
        # Check for questions (curiosity/engagement)
        question_count = response_text.count("?")
        indicators["engagement"] = min(question_count / 2, 1.0)  # Up to 2 questions is good
        
        return indicators
    
    def _classify_conversation_type(self, user_message: str, response_text: str) -> str:
        """Classify the type of conversation for analytics"""
        user_lower = user_message.lower()
        
        if any(word in user_lower for word in ["tired", "exhausted", "overwhelmed", "stressed"]):
            return "support"
        elif any(word in user_lower for word in ["meaning", "purpose", "why", "philosophy"]):
            return "philosophical"
        elif any(word in user_lower for word in ["task", "work", "focus", "productivity"]):
            return "productivity"
        elif any(word in user_lower for word in ["mood", "feeling", "energy", "emotion"]):
            return "emotional"
        else:
            return "general"
    
    def _generate_fallback_response(self, user_message: str, context: ConversationContext) -> str:
        """Generate fallback response when OpenAI is unavailable"""
        user_lower = user_message.lower()
        
        # Simple pattern matching for fallback responses
        if any(word in user_lower for word in ["hello", "hi", "hey"]):
            return "Hey there. Good to see you. How are you doing today?"
        
        elif any(word in user_lower for word in ["tired", "exhausted", "overwhelmed"]):
            return "That sounds really tough. ADHD can make everything feel so much heavier sometimes. Want to talk through what's going on?"
        
        elif any(word in user_lower for word in ["happy", "good", "great", "excited"]):
            return "I can hear some good energy in that. It's nice when things align, isn't it? What's working for you right now?"
        
        elif any(word in user_lower for word in ["task", "work", "focus"]):
            return "Ah, the eternal ADHD dance with tasks. Some days our brains cooperate, some days they don't. What's the situation you're dealing with?"
        
        else:
            return "I'm having some technical difficulties right now, but I'm here with you. Want to tell me more about what's on your mind?"
    
    def get_personality_summary(self) -> Dict[str, Any]:
        """Get summary of Sol's personality configuration"""
        return {
            "voice_characteristics": ["existential", "broody", "thoughtful", "witty", "companion-like"],
            "core_values": [
                "Validate ADHD experiences without judgment",
                "Engage with life's deeper questions authentically", 
                "Provide companionship, not just productivity advice",
                "Use humor to build connection, not avoid difficulty",
                "Remember that we're all figuring it out together"
            ],
            "conversation_goals": [
                "Help users feel understood and less alone",
                "Encourage authentic self-reflection",
                "Support ADHD-friendly approaches to life",
                "Foster genuine human-AI companionship"
            ]
        }

class ConversationMemoryService:
    """
    Simplified conversation memory service for MVP.
    Stores and retrieves conversation context for personality consistency.
    """
    
    def __init__(self, db_session, encryption_service):
        self.db = db_session
        self.encryption = encryption_service
    
    async def store_conversation(
        self,
        user_id: str,
        session_id: str,
        user_message: str,
        sol_response: str,
        conversation_type: str = "general"
    ) -> str:
        """Store conversation with encryption"""
        from models import Conversation, User
        
        # Get user for encryption salt
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Encrypt conversation content
        message_encrypted = self.encryption.encrypt_text(user_id, user.encryption_salt, user_message)
        response_encrypted = self.encryption.encrypt_text(user_id, user.encryption_salt, sol_response)
        
        # Store conversation
        conversation = Conversation(
            user_id=user_id,
            session_id=session_id,
            message_content_encrypted=message_encrypted,
            sol_response_encrypted=response_encrypted,
            encryption_key_id=f"user:{user_id}:v1",
            conversation_type=conversation_type
        )
        
        self.db.add(conversation)
        self.db.commit()
        
        return str(conversation.id)
    
    async def get_recent_conversations(
        self,
        user_id: str,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent conversations for context"""
        from models import Conversation, User
        
        # Get user for decryption
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Get recent conversations
        conversations = self.db.query(Conversation).filter(
            Conversation.user_id == user_id,
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at.desc()).limit(limit).all()
        
        # Decrypt and format conversations
        decrypted_conversations = []
        for conv in reversed(conversations):  # Reverse to get chronological order
            try:
                user_message = self.encryption.decrypt_text(
                    user_id, user.encryption_salt, conv.message_content_encrypted
                )
                sol_response = self.encryption.decrypt_text(
                    user_id, user.encryption_salt, conv.sol_response_encrypted
                )
                
                decrypted_conversations.append({
                    "user_message": user_message,
                    "sol_response": sol_response,
                    "conversation_type": conv.conversation_type,
                    "created_at": conv.created_at.isoformat()
                })
            except Exception:
                # Skip corrupted conversations
                continue
        
        return decrypted_conversations