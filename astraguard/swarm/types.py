"""
SwarmMessage types and schema for inter-satellite communication.

Issue #398: Message bus abstraction for distributed satellite operations
- Topic-based pub/sub messaging
- QoS levels (0: fire-forget, 1: ACK, 2: reliable)
- ISL bandwidth and latency constraints
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional
from datetime import datetime
from uuid import UUID, uuid4

from astraguard.swarm.models import AgentID


class SwarmTopic(str, Enum):
    """Topic categories for satellite messaging.
    
    health/     → Periodic health summaries and status (30s intervals)
    intent/     → Action plans and mission intent (variable)
    coord/      → Coordination and synchronization messages
    control/    → Control commands and mode changes
    """
    HEALTH = "health"
    INTENT = "intent"
    COORD = "coord"
    CONTROL = "control"

    @classmethod
    def is_valid_topic(cls, topic: str) -> bool:
        """Check if topic string is valid."""
        for member in cls:
            if topic.startswith(f"{member.value}/"):
                return True
        return False


class QoSLevel(int, Enum):
    """Quality of Service levels for message delivery.
    
    FIRE_FORGET (0): Best effort, no guarantees
    ACK (1): Sender waits for acknowledgment
    RELIABLE (2): Retry + deduplication guarantee
    """
    FIRE_FORGET = 0
    ACK = 1
    RELIABLE = 2


@dataclass(frozen=True)
class SwarmMessage:
    """Immutable inter-satellite message.
    
    Attributes:
        topic: Message topic (e.g., "health/summary", "control/safe_mode")
        payload: Serialized message content (bytes, typically LZ4 compressed)
        sender: Agent ID of message sender
        qos: Quality of Service level (0, 1, 2)
        timestamp: UTC timestamp of message creation
        sequence: Sequence number for ordering (Issue #403 prep)
        message_id: Unique message identifier (UUID4)
        receiver: Optional specific receiver (None = broadcast)
    """
    topic: str
    payload: bytes
    sender: AgentID
    qos: int = 1
    timestamp: datetime = field(default_factory=datetime.utcnow)
    sequence: int = 0
    message_id: UUID = field(default_factory=uuid4)
    receiver: Optional[AgentID] = None

    def __post_init__(self):
        """Validate message constraints."""
        # Validate topic
        if not SwarmTopic.is_valid_topic(self.topic):
            raise ValueError(
                f"Invalid topic: {self.topic}. Must start with "
                f"'health/', 'intent/', 'coord/', or 'control/'"
            )
        
        # Validate QoS
        if self.qos not in (0, 1, 2):
            raise ValueError(f"QoS must be 0, 1, or 2, got {self.qos}")
        
        # Validate payload
        if not isinstance(self.payload, bytes):
            raise ValueError(f"Payload must be bytes, got {type(self.payload)}")
        
        if len(self.payload) == 0:
            raise ValueError("Payload cannot be empty")
        
        if len(self.payload) > 10240:  # 10KB ISL limit
            raise ValueError(
                f"Payload size {len(self.payload)} exceeds 10KB ISL limit"
            )
        
        # Validate sequence
        if self.sequence < 0:
            raise ValueError(f"Sequence must be non-negative, got {self.sequence}")

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "topic": self.topic,
            "payload": self.payload.hex(),  # Hex encode bytes
            "sender": self.sender.to_dict(),
            "qos": self.qos,
            "timestamp": self.timestamp.isoformat(),
            "sequence": self.sequence,
            "message_id": str(self.message_id),
            "receiver": self.receiver.to_dict() if self.receiver else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SwarmMessage":
        """Deserialize from dictionary."""
        from uuid import UUID
        
        sender_data = data["sender"]
        sender = AgentID(
            constellation=sender_data["constellation"],
            satellite_serial=sender_data["satellite_serial"],
            uuid=UUID(sender_data["uuid"]),
        )
        
        receiver = None
        if data.get("receiver"):
            receiver_data = data["receiver"]
            receiver = AgentID(
                constellation=receiver_data["constellation"],
                satellite_serial=receiver_data["satellite_serial"],
                uuid=UUID(receiver_data["uuid"]),
            )
        
        return cls(
            topic=data["topic"],
            payload=bytes.fromhex(data["payload"]),
            sender=sender,
            qos=data.get("qos", 1),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            sequence=data.get("sequence", 0),
            message_id=UUID(data.get("message_id", str(uuid4()))),
            receiver=receiver,
        )


@dataclass
class MessageAck:
    """Acknowledgment for QoS 1 messages.
    
    Attributes:
        message_id: ID of acknowledged message
        sender: Agent sending the ACK
        timestamp: ACK timestamp
        success: Whether delivery was successful
    """
    message_id: UUID
    sender: AgentID
    timestamp: datetime = field(default_factory=datetime.utcnow)
    success: bool = True

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "message_id": str(self.message_id),
            "sender": self.sender.to_dict(),
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
        }


@dataclass
class TopicFilter:
    """Filter for topic subscriptions.
    
    Supports wildcard subscriptions:
    - "health/*" → all health topics
    - "health/summary" → specific topic
    - "*" → all topics (use with caution)
    """
    pattern: str

    def __post_init__(self):
        """Validate filter pattern."""
        if not self.pattern:
            raise ValueError("Filter pattern cannot be empty")

    def matches(self, topic: str) -> bool:
        """Check if topic matches this filter."""
        if self.pattern == "*":
            return True
        
        if self.pattern.endswith("/*"):
            prefix = self.pattern[:-2]
            return topic.startswith(f"{prefix}/")
        
        return self.pattern == topic


@dataclass
class SubscriptionID:
    """Subscription identifier for message bus operations.
    
    Attributes:
        id: Unique subscription identifier
        topic_filter: Topic filter for this subscription
        subscriber: Subscribing agent
    """
    id: UUID = field(default_factory=uuid4)
    topic_filter: str = ""
    subscriber: Optional[AgentID] = None

    def __hash__(self):
        """Make subscription hashable."""
        return hash(self.id)

    def __eq__(self, other):
        """Compare subscriptions by ID."""
        if not isinstance(other, SubscriptionID):
            return False
        return self.id == other.id

class PriorityEnum(int, Enum):
    """Priority levels for intent messages.
    
    AVAILABILITY (1): Lowest - role changes, load balancing
    PERFORMANCE (2): Medium - thrust optimization, attitude control
    SAFETY (3): Highest - emergency stop, safe mode transitions
    """
    AVAILABILITY = 1
    PERFORMANCE = 2
    SAFETY = 3


@dataclass
class IntentMessage:
    """Intent message for coordinating planned actions across constellation.
    
    Issue #402: Intent signal exchange protocol
    - Communicates planned actions (attitude adjust, load shed, role change)
    - Includes conflict scoring for collision detection
    - Prioritized delivery with QoS=2 (reliable)
    
    Attributes:
        action_type: Type of action (e.g., "attitude_adjust", "load_shed", "role_change")
        parameters: Action parameters as dict (e.g., {"target_angle": 45.2, "duration": 30})
        priority: Priority level (SAFETY > PERFORMANCE > AVAILABILITY)
        sender: AgentID of intent originator
        conflict_score: 0.0-1.0 estimated conflict vs known intents
        sequence: Sequence number for ordering (Issue #403 prep)
        timestamp: When intent was created
    """
    action_type: str
    parameters: dict[str, Any]
    priority: PriorityEnum
    sender: AgentID
    conflict_score: float = 0.0
    sequence: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate intent message fields."""
        if not self.action_type:
            raise ValueError("action_type must not be empty")
        if not isinstance(self.priority, PriorityEnum):
            raise ValueError("priority must be PriorityEnum instance")
        if not (0.0 <= self.conflict_score <= 1.0):
            raise ValueError("conflict_score must be 0.0-1.0")
    
    def to_dict(self) -> dict:
        """Convert to dict for serialization."""
        return {
            "action_type": self.action_type,
            "parameters": self.parameters,
            "priority": self.priority.value,
            "sender": self.sender.uuid.hex,
            "conflict_score": self.conflict_score,
            "sequence": self.sequence,
            "timestamp": self.timestamp.isoformat(),
        }