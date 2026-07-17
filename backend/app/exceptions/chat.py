class ChatError(Exception):
    """Base exception for chat and conversation operations."""
    pass


class ConversationNotFoundError(ChatError):
    """Raised when a conversation is not found."""
    pass


class ConversationAccessDeniedError(ChatError):
    """Raised when a user attempts to access a conversation they do not own."""
    pass


class ConversationArchivedError(ChatError):
    """Raised when trying to perform operations (like adding a message) on an archived conversation."""
    pass


class InvalidConversationStateError(ChatError):
    """Raised when the conversation state is invalid for the requested operation."""
    pass
