from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"


class DocumentStatus(str, Enum):
    UPLOADING = "uploading"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    EMBEDDING = "embedding"
    EMBEDDED = "embedded"


class ConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class MessageRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
    SYSTEM = "SYSTEM"
