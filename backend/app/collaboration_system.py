"""
Advanced Real-time Collaboration System for DealFlow Analytics
Implements team workspaces, deal sharing, and investment committee features
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Set, Any
from datetime import datetime, timedelta
from enum import Enum
import redis
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel, Field, EmailStr
import hashlib
import jwt
from collections import defaultdict

class UserRole(Enum):
    """User roles in the system"""
    ADMIN = "admin"
    PARTNER = "partner"
    PRINCIPAL = "principal"
    ASSOCIATE = "associate"
    ANALYST = "analyst"
    VIEWER = "viewer"

class DealStatus(Enum):
    """Deal pipeline status"""
    SOURCED = "sourced"
    SCREENING = "screening"
    DUE_DILIGENCE = "due_diligence"
    PARTNER_REVIEW = "partner_review"
    IC_REVIEW = "ic_review"  # Investment Committee
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    MONITORING = "monitoring"

class VoteType(Enum):
    """Investment committee vote types"""
    STRONG_YES = "strong_yes"
    YES = "yes"
    NEUTRAL = "neutral"
    NO = "no"
    STRONG_NO = "strong_no"
    ABSTAIN = "abstain"

class User(BaseModel):
    """User model"""
    user_id: str
    email: EmailStr
    name: str
    firm_id: str
    role: UserRole
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

class Workspace(BaseModel):
    """Team workspace model"""
    workspace_id: str
    firm_id: str
    name: str
    description: Optional[str] = None
    members: List[str] = Field(default_factory=list)  # user_ids
    settings: Dict[str, Any] = Field(default_factory=dict)
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class Deal(BaseModel):
    """Deal model with collaboration features"""
    deal_id: str
    workspace_id: str
    company_name: str
    company_data: Dict[str, Any]
    status: DealStatus
    stage: str  # Seed, Series A, B, C, etc.
    investment_amount: Optional[float] = None
    valuation: Optional[float] = None
    ownership_target: Optional[float] = None
    lead_partner: str  # user_id
    team_members: List[str] = Field(default_factory=list)
    annotations: List[Dict[str, Any]] = Field(default_factory=list)
    documents: List[Dict[str, Any]] = Field(default_factory=list)
    due_diligence_items: List[Dict[str, Any]] = Field(default_factory=list)
    ic_votes: Dict[str, VoteType] = Field(default_factory=dict)
    ic_comments: List[Dict[str, Any]] = Field(default_factory=list)
    activity_log: List[Dict[str, Any]] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Annotation(BaseModel):
    """Deal annotation model"""
    annotation_id: str
    deal_id: str
    user_id: str
    content: str
    type: str  # "note", "risk", "opportunity", "question"
    section: Optional[str] = None  # Which section of analysis
    created_at: datetime = Field(default_factory=datetime.utcnow)
    replies: List[Dict[str, Any]] = Field(default_factory=list)

class DueDiligenceItem(BaseModel):
    """Due diligence checklist item"""
    item_id: str
    deal_id: str
    category: str  # "legal", "financial", "technical", "market", "team"
    title: str
    description: Optional[str] = None
    assigned_to: Optional[str] = None  # user_id
    status: str  # "pending", "in_progress", "completed", "flagged"
    priority: str  # "low", "medium", "high", "critical"
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    notes: List[Dict[str, Any]] = Field(default_factory=list)
    attachments: List[Dict[str, Any]] = Field(default_factory=list)

class CollaborationHub:
    """
    Central hub for all collaboration features
    """
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.active_connections: Dict[str, Set[WebSocket]] = defaultdict(set)
        self.user_connections: Dict[str, WebSocket] = {}
        self.workspace_cache: Dict[str, Workspace] = {}
        self.deal_cache: Dict[str, Deal] = {}
        self.jwt_secret = os.getenv("JWT_SECRET", "your-secret-key-here")
        
    async def connect_websocket(
        self,
        websocket: WebSocket,
        user_id: str,
        workspace_id: str
    ):
        """
        Connect user to collaboration workspace via WebSocket
        """
        await websocket.accept()
        
        # Add to active connections
        self.active_connections[workspace_id].add(websocket)
        self.user_connections[user_id] = websocket
        
        # Notify other users in workspace
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
        
        # Send initial state
        await self.send_workspace_state(websocket, workspace_id)
    
    async def disconnect_websocket(
        self,
        websocket: WebSocket,
        user_id: str,
        workspace_id: str
    ):
        """
        Disconnect user from workspace
        """
        self.active_connections[workspace_id].discard(websocket)
        self.user_connections.pop(user_id, None)
        
        # Notify other users
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    async def handle_websocket_message(
        self,
        websocket: WebSocket,
        message: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ):
        """
        Handle incoming WebSocket messages
        """
        message_type = message.get("type")
        
        handlers = {
            "cursor_move": self.handle_cursor_move,
            "selection_change": self.handle_selection_change,
            "annotation_create": self.handle_annotation_create,
            "annotation_reply": self.handle_annotation_reply,
            "deal_update": self.handle_deal_update,
            "vote_cast": self.handle_vote_cast,
            "comment_add": self.handle_comment_add,
            "dd_item_update": self.handle_dd_item_update,
            "typing_indicator": self.handle_typing_indicator
        }
        
        handler = handlers.get(message_type)
        if handler:
            await handler(message, user_id, workspace_id)
        else:
            await websocket.send_json({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            })
    
    async def handle_cursor_move(
        self,
        message: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ):
        """
        Handle cursor movement for collaborative editing
        """
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "cursor_update",
                "user_id": user_id,
                "position": message.get("position"),
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
    
    async def handle_selection_change(
        self,
        message: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ):
        """
        Handle text selection changes
        """
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "selection_update",
                "user_id": user_id,
                "selection": message.get("selection"),
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
    
    async def handle_annotation_create(
        self,
        message: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ):
        """
        Create new annotation on a deal
        """
        annotation = Annotation(
            annotation_id=str(uuid.uuid4()),
            deal_id=message.get("deal_id"),
            user_id=user_id,
            content=message.get("content"),
            type=message.get("annotation_type", "note"),
            section=message.get("section")
        )
        
        # Save annotation
        await self.save_annotation(annotation)
        
        # Broadcast to workspace
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "annotation_created",
                "annotation": annotation.dict(),
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Send notification to mentioned users
        mentioned_users = self.extract_mentions(annotation.content)
        for mentioned_user in mentioned_users:
            await self.send_notification(
                mentioned_user,
                {
                    "type": "mention",
                    "from_user": user_id,
                    "deal_id": annotation.deal_id,
                    "content": annotation.content
                }
            )
    
    async def handle_vote_cast(
        self,
        message: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ):
        """
        Handle investment committee vote
        """
        deal_id = message.get("deal_id")
        vote = VoteType(message.get("vote"))
        comment = message.get("comment", "")
        
        # Update deal with vote
        deal = await self.get_deal(deal_id)
        if deal:
            deal.ic_votes[user_id] = vote
            if comment:
                deal.ic_comments.append({
                    "user_id": user_id,
                    "comment": comment,
                    "vote": vote.value,
                    "timestamp": datetime.utcnow().isoformat()
                })
            
            await self.save_deal(deal)
            
            # Calculate vote summary
            vote_summary = self.calculate_vote_summary(deal.ic_votes)
            
            # Broadcast update
            await self.broadcast_to_workspace(
                workspace_id,
                {
                    "type": "vote_update",
                    "deal_id": deal_id,
                    "user_id": user_id,
                    "vote": vote.value,
                    "vote_summary": vote_summary,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
            
            # Check if voting is complete
            if self.is_voting_complete(deal, workspace_id):
                await self.finalize_ic_decision(deal, workspace_id)
    
    async def handle_dd_item_update(
        self,
        message: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ):
        """
        Handle due diligence item update
        """
        item_id = message.get("item_id")
        updates = message.get("updates", {})
        
        # Update DD item
        dd_item = await self.get_dd_item(item_id)
        if dd_item:
            for key, value in updates.items():
                if hasattr(dd_item, key):
                    setattr(dd_item, key, value)
            
            # Track completion
            if updates.get("status") == "completed":
                dd_item.completed_at = datetime.utcnow()
                
                # Send completion notification
                await self.send_notification(
                    dd_item.assigned_to,
                    {
                        "type": "dd_completed",
                        "item": dd_item.title,
                        "completed_by": user_id
                    }
                )
            
            await self.save_dd_item(dd_item)
            
            # Broadcast update
            await self.broadcast_to_workspace(
                workspace_id,
                {
                    "type": "dd_item_updated",
                    "item_id": item_id,
                    "updates": updates,
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
    
    async def handle_typing_indicator(
        self,
        message: Dict[str, Any],
        user_id: str,
        workspace_id: str
    ):
        """
        Handle typing indicators for real-time awareness
        """
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "typing_indicator",
                "user_id": user_id,
                "is_typing": message.get("is_typing", False),
                "context": message.get("context"),  # Where they're typing
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude_user=user_id
        )
    
    async def create_workspace(
        self,
        name: str,
        firm_id: str,
        created_by: str,
        description: Optional[str] = None
    ) -> Workspace:
        """
        Create new team workspace
        """
        workspace = Workspace(
            workspace_id=str(uuid.uuid4()),
            firm_id=firm_id,
            name=name,
            description=description,
            created_by=created_by,
            members=[created_by]
        )
        
        # Save to cache and persistent storage
        self.workspace_cache[workspace.workspace_id] = workspace
        if self.redis_client:
            self.redis_client.hset(
                "workspaces",
                workspace.workspace_id,
                json.dumps(workspace.dict())
            )
        
        return workspace
    
    async def create_deal(
        self,
        workspace_id: str,
        company_name: str,
        company_data: Dict[str, Any],
        lead_partner: str,
        stage: str
    ) -> Deal:
        """
        Create new deal in workspace
        """
        deal = Deal(
            deal_id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            company_name=company_name,
            company_data=company_data,
            status=DealStatus.SOURCED,
            stage=stage,
            lead_partner=lead_partner,
            team_members=[lead_partner]
        )
        
        # Add to cache
        self.deal_cache[deal.deal_id] = deal
        
        # Save to persistent storage
        await self.save_deal(deal)
        
        # Create default DD checklist
        await self.create_dd_checklist(deal.deal_id)
        
        # Log activity
        await self.log_activity(
            deal.deal_id,
            lead_partner,
            "created",
            f"Deal created for {company_name}"
        )
        
        # Broadcast to workspace
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "deal_created",
                "deal": deal.dict(),
                "created_by": lead_partner,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        return deal
    
    async def share_deal(
        self,
        deal_id: str,
        shared_by: str,
        share_with: List[str],  # user_ids or emails
        permissions: Dict[str, bool] = None
    ) -> Dict[str, Any]:
        """
        Share deal with team members or external users
        """
        deal = await self.get_deal(deal_id)
        if not deal:
            raise HTTPException(status_code=404, detail="Deal not found")
        
        # Default permissions
        if permissions is None:
            permissions = {
                "can_view": True,
                "can_comment": True,
                "can_edit": False,
                "can_vote": False
            }
        
        # Generate share token for external users
        share_token = self.generate_share_token(deal_id, permissions)
        
        # Add users to deal team
        for user_id in share_with:
            if user_id not in deal.team_members:
                deal.team_members.append(user_id)
        
        await self.save_deal(deal)
        
        # Send notifications
        for user_id in share_with:
            await self.send_notification(
                user_id,
                {
                    "type": "deal_shared",
                    "deal_id": deal_id,
                    "company_name": deal.company_name,
                    "shared_by": shared_by,
                    "permissions": permissions
                }
            )
        
        return {
            "share_token": share_token,
            "share_url": f"https://dealflow.ai/deals/{deal_id}?token={share_token}",
            "shared_with": share_with,
            "permissions": permissions
        }
    
    async def create_dd_checklist(self, deal_id: str) -> List[DueDiligenceItem]:
        """
        Create default due diligence checklist for a deal
        """
        categories = {
            "legal": [
                "Corporate structure and cap table review",
                "IP ownership and patents verification",
                "Employment agreements and key person insurance",
                "Litigation history and ongoing disputes",
                "Regulatory compliance review"
            ],
            "financial": [
                "Historical financials audit (3 years)",
                "Revenue recognition and quality of earnings",
                "Unit economics analysis",
                "Burn rate and runway calculation",
                "Customer concentration analysis",
                "Working capital requirements"
            ],
            "technical": [
                "Technology architecture review",
                "Scalability assessment",
                "Security audit",
                "Code quality and technical debt",
                "Data privacy and protection",
                "Third-party dependencies"
            ],
            "market": [
                "TAM/SAM/SOM validation",
                "Competitive landscape analysis",
                "Customer interviews (10+)",
                "Market growth projections",
                "Go-to-market strategy review",
                "Pricing strategy validation"
            ],
            "team": [
                "Founder background checks",
                "Key employee interviews",
                "Organization structure review",
                "Compensation and equity analysis",
                "Culture assessment",
                "Hiring plan evaluation"
            ]
        }
        
        checklist = []
        
        for category, items in categories.items():
            for item_title in items:
                dd_item = DueDiligenceItem(
                    item_id=str(uuid.uuid4()),
                    deal_id=deal_id,
                    category=category,
                    title=item_title,
                    status="pending",
                    priority="medium" if category != "financial" else "high"
                )
                checklist.append(dd_item)
                await self.save_dd_item(dd_item)
        
        return checklist
    
    def calculate_vote_summary(
        self,
        votes: Dict[str, VoteType]
    ) -> Dict[str, Any]:
        """
        Calculate investment committee vote summary
        """
        vote_counts = defaultdict(int)
        for vote in votes.values():
            vote_counts[vote.value] += 1
        
        total_votes = len(votes)
        if total_votes == 0:
            return {"status": "no_votes", "recommendation": "pending"}
        
        # Calculate weighted score
        weights = {
            VoteType.STRONG_YES: 2,
            VoteType.YES: 1,
            VoteType.NEUTRAL: 0,
            VoteType.NO: -1,
            VoteType.STRONG_NO: -2,
            VoteType.ABSTAIN: 0
        }
        
        weighted_score = sum(
            weights.get(vote, 0) for vote in votes.values()
        )
        
        # Determine recommendation
        avg_score = weighted_score / total_votes
        if avg_score >= 1.5:
            recommendation = "strong_proceed"
        elif avg_score >= 0.5:
            recommendation = "proceed"
        elif avg_score >= -0.5:
            recommendation = "further_review"
        else:
            recommendation = "do_not_proceed"
        
        return {
            "total_votes": total_votes,
            "vote_counts": dict(vote_counts),
            "weighted_score": weighted_score,
            "average_score": avg_score,
            "recommendation": recommendation,
            "consensus_level": self.calculate_consensus(vote_counts, total_votes)
        }
    
    def calculate_consensus(
        self,
        vote_counts: Dict[str, int],
        total_votes: int
    ) -> str:
        """
        Calculate consensus level from votes
        """
        if total_votes == 0:
            return "no_consensus"
        
        max_votes = max(vote_counts.values())
        consensus_ratio = max_votes / total_votes
        
        if consensus_ratio >= 0.8:
            return "strong_consensus"
        elif consensus_ratio >= 0.6:
            return "moderate_consensus"
        elif consensus_ratio >= 0.4:
            return "weak_consensus"
        else:
            return "no_consensus"
    
    def generate_share_token(
        self,
        deal_id: str,
        permissions: Dict[str, bool]
    ) -> str:
        """
        Generate JWT token for deal sharing
        """
        payload = {
            "deal_id": deal_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow()
        }
        
        token = jwt.encode(
            payload,
            self.jwt_secret,
            algorithm="HS256"
        )
        
        return token
    
    def verify_share_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode share token
        """
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Share link expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid share token")
    
    def extract_mentions(self, content: str) -> List[str]:
        """
        Extract @mentions from content
        """
        import re
        pattern = r'@(\w+)'
        mentions = re.findall(pattern, content)
        return mentions
    
    async def broadcast_to_workspace(
        self,
        workspace_id: str,
        message: Dict[str, Any],
        exclude_user: Optional[str] = None
    ):
        """
        Broadcast message to all users in workspace
        """
        connections = self.active_connections.get(workspace_id, set())
        
        for connection in connections:
            # Skip excluded user
            if exclude_user:
                user_id = self.get_user_id_from_connection(connection)
                if user_id == exclude_user:
                    continue
            
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to connection: {e}")
                connections.discard(connection)
    
    async def send_notification(
        self,
        user_id: str,
        notification: Dict[str, Any]
    ):
        """
        Send notification to specific user
        """
        # Check if user has active WebSocket connection
        if user_id in self.user_connections:
            connection = self.user_connections[user_id]
            try:
                await connection.send_json({
                    "type": "notification",
                    "notification": notification,
                    "timestamp": datetime.utcnow().isoformat()
                })
            except Exception as e:
                print(f"Error sending notification: {e}")
        
        # Also save to notification queue for offline users
        if self.redis_client:
            self.redis_client.lpush(
                f"notifications:{user_id}",
                json.dumps(notification)
            )
    
    async def send_workspace_state(
        self,
        websocket: WebSocket,
        workspace_id: str
    ):
        """
        Send current workspace state to newly connected user
        """
        # Get workspace details
        workspace = self.workspace_cache.get(workspace_id)
        
        # Get active deals
        deals = await self.get_workspace_deals(workspace_id)
        
        # Get online users
        online_users = list(self.active_connections[workspace_id])
        
        state = {
            "type": "workspace_state",
            "workspace": workspace.dict() if workspace else None,
            "deals": [deal.dict() for deal in deals],
            "online_users": len(online_users),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await websocket.send_json(state)
    
    # Storage methods
    async def save_deal(self, deal: Deal):
        """Save deal to persistent storage"""
        if self.redis_client:
            self.redis_client.hset(
                "deals",
                deal.deal_id,
                json.dumps(deal.dict(), default=str)
            )
    
    async def get_deal(self, deal_id: str) -> Optional[Deal]:
        """Get deal from storage"""
        if deal_id in self.deal_cache:
            return self.deal_cache[deal_id]
        
        if self.redis_client:
            data = self.redis_client.hget("deals", deal_id)
            if data:
                deal = Deal(**json.loads(data))
                self.deal_cache[deal_id] = deal
                return deal
        
        return None
    
    async def get_workspace_deals(self, workspace_id: str) -> List[Deal]:
        """Get all deals in a workspace"""
        deals = []
        
        # Check cache first
        for deal in self.deal_cache.values():
            if deal.workspace_id == workspace_id:
                deals.append(deal)
        
        # Check persistent storage
        if self.redis_client and not deals:
            all_deals = self.redis_client.hgetall("deals")
            for deal_data in all_deals.values():
                deal = Deal(**json.loads(deal_data))
                if deal.workspace_id == workspace_id:
                    deals.append(deal)
                    self.deal_cache[deal.deal_id] = deal
        
        return deals
    
    async def save_annotation(self, annotation: Annotation):
        """Save annotation to storage"""
        if self.redis_client:
            self.redis_client.hset(
                "annotations",
                annotation.annotation_id,
                json.dumps(annotation.dict(), default=str)
            )
    
    async def save_dd_item(self, dd_item: DueDiligenceItem):
        """Save DD item to storage"""
        if self.redis_client:
            self.redis_client.hset(
                "dd_items",
                dd_item.item_id,
                json.dumps(dd_item.dict(), default=str)
            )
    
    async def get_dd_item(self, item_id: str) -> Optional[DueDiligenceItem]:
        """Get DD item from storage"""
        if self.redis_client:
            data = self.redis_client.hget("dd_items", item_id)
            if data:
                return DueDiligenceItem(**json.loads(data))
        return None
    
    async def log_activity(
        self,
        deal_id: str,
        user_id: str,
        action: str,
        details: str
    ):
        """Log activity for audit trail"""
        activity = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        deal = await self.get_deal(deal_id)
        if deal:
            deal.activity_log.append(activity)
            await self.save_deal(deal)
    
    def get_user_id_from_connection(self, connection: WebSocket) -> Optional[str]:
        """Get user ID from WebSocket connection"""
        for user_id, conn in self.user_connections.items():
            if conn == connection:
                return user_id
        return None
    
    def is_voting_complete(self, deal: Deal, workspace_id: str) -> bool:
        """Check if all required votes are cast"""
        workspace = self.workspace_cache.get(workspace_id)
        if not workspace:
            return False
        
        # Get required voters (e.g., all partners)
        required_voters = self.get_required_voters(workspace)
        
        # Check if all required voters have voted
        for voter_id in required_voters:
            if voter_id not in deal.ic_votes:
                return False
        
        return True
    
    def get_required_voters(self, workspace: Workspace) -> List[str]:
        """Get list of required voters for IC decisions"""
        # This would typically query user roles
        # For now, return all workspace members as example
        return workspace.members
    
    async def finalize_ic_decision(self, deal: Deal, workspace_id: str):
        """Finalize investment committee decision"""
        vote_summary = self.calculate_vote_summary(deal.ic_votes)
        
        # Update deal status based on decision
        if vote_summary["recommendation"] in ["strong_proceed", "proceed"]:
            deal.status = DealStatus.NEGOTIATION
            decision = "approved"
        else:
            deal.status = DealStatus.CLOSED_LOST
            decision = "rejected"
        
        await self.save_deal(deal)
        
        # Notify all stakeholders
        await self.broadcast_to_workspace(
            workspace_id,
            {
                "type": "ic_decision_final",
                "deal_id": deal.deal_id,
                "decision": decision,
                "vote_summary": vote_summary,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Log the decision
        await self.log_activity(
            deal.deal_id,
            "system",
            "ic_decision",
            f"IC Decision: {decision} with {vote_summary['consensus_level']} consensus"
        )

import os