import { useState, useEffect, useRef, memo } from 'react';
import type { KeyboardEvent, UIEvent } from 'react';
import { useChat } from '../../../hooks/useChat';
import { useChatInfiniteQuery } from '../../../hooks/useChatInfiniteQuery';

export const ChatInterface = memo(function ChatInterface() {
  const {
    conversations,
    activeConversation,
    messages,
    isLoading,
    isSending,
    error,
    createConversation,
    selectConversation,
    renameConversation,
    deleteConversation,
    sendMessage,
    clearError,
  } = useChat();

  const [input, setInput] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // TanStack Infinite Query for Chat Message Pagination
  const {
    fetchNextPage,
    hasNextPage,
    isFetchingNextPage,
  } = useChatInfiniteQuery(
    activeConversation?.workspace_id || null,
    activeConversation?.id || null
  );

  const handleScroll = (e: UIEvent<HTMLDivElement>) => {
    if (e.currentTarget.scrollTop === 0 && hasNextPage && !isFetchingNextPage) {
      fetchNextPage();
    }
  };

  // Auto-scroll to the bottom of the chat list when messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSend = () => {
    if (!input.trim() || isSending) return;
    sendMessage(input.trim());
    setInput('');
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const startEditing = (id: string, currentTitle: string) => {
    setEditingId(id);
    setEditTitle(currentTitle);
  };

  const saveRename = async (id: string) => {
    if (!editTitle.trim()) return;
    try {
      await renameConversation(id, editTitle.trim());
    } catch (err) {
      console.error(err);
    } finally {
      setEditingId(null);
    }
  };

  const cancelRename = () => {
    setEditingId(null);
  };

  return (
    <div className="chat-container">
      {/* 1. Left Side Pane: Conversations List */}
      <aside className="chat-sidebar" aria-label="Conversation list">
        <button
          className="new-chat-btn"
          onClick={createConversation}
          disabled={isLoading}
        >
          <span>+</span> New Chat
        </button>

        <div className="chat-sessions-list">
          {conversations.length === 0 ? (
            <p className="no-sessions-text">No active chat sessions.</p>
          ) : (
            conversations.map((conv) => {
              const isActive = activeConversation?.id === conv.id;
              const isEditing = editingId === conv.id;

              return (
                <div
                  key={conv.id}
                  className={`chat-session-item ${isActive ? 'active' : ''}`}
                  onClick={() => !isEditing && selectConversation(conv.id)}
                >
                  {isEditing ? (
                    <input
                      type="text"
                      className="rename-input"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onBlur={() => saveRename(conv.id)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') saveRename(conv.id);
                        if (e.key === 'Escape') cancelRename();
                      }}
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  ) : (
                    <>
                      <div className="session-info">
                        <span className="session-title" title={conv.title}>
                          {conv.title}
                        </span>
                        {conv.last_message_preview && (
                          <span className="session-preview">
                            {conv.last_message_preview}
                          </span>
                        )}
                      </div>
                      <div className="session-actions" onClick={(e) => e.stopPropagation()}>
                        <button
                          className="action-icon-btn edit-btn"
                          title="Rename Session"
                          onClick={() => startEditing(conv.id, conv.title)}
                        >
                          ✏️
                        </button>
                        <button
                          className="action-icon-btn delete-btn"
                          title="Delete Session"
                          onClick={() => deleteConversation(conv.id)}
                        >
                          🗑️
                        </button>
                      </div>
                    </>
                  )}
                </div>
              );
            })
          )}
        </div>
      </aside>

      {/* 2. Right Side Pane: Dialog Panel */}
      <main className="chat-dialog-panel">
        {activeConversation ? (
          <>
            {/* Header info bar */}
            <header className="chat-dialog-header">
              <h2>{activeConversation.title}</h2>
              <span className="status-pill active-pill">Active Session</span>
            </header>

            {/* Error notifications */}
            {error && (
              <div className="chat-error-bar">
                <span>⚠️ {error}</span>
                <button onClick={clearError} className="clear-error-btn">✕</button>
              </div>
            )}

            {/* Messages feed with infinite scrolling */}
            <div className="chat-messages-feed" onScroll={handleScroll}>
              {isFetchingNextPage && (
                <div style={{ textAlign: 'center', padding: '8px', color: '#94a3b8', fontSize: '0.8rem' }}>
                  ⏳ Loading older message history...
                </div>
              )}
              {messages.length === 0 ? (
                <div className="chat-empty-state">
                  <span className="chat-empty-icon">💬</span>
                  <h3>Start the Conversation</h3>
                  <p>Ask a question about the uploaded documents in this workspace.</p>
                </div>
              ) : (
                messages.map((msg) => {
                  const isUser = msg.role === 'USER';
                  return (
                    <div
                      key={msg.id}
                      className={`message-row ${isUser ? 'user-row' : 'assistant-row'}`}
                    >
                      <div className="message-bubble">
                        <div className="message-content">{msg.content}</div>

                        {/* Render Citations if Assistant response has any */}
                        {!isUser && msg.citations && msg.citations.length > 0 && (
                          <div className="message-citations">
                            <span className="citations-label">Sources matched:</span>
                            <div className="citations-grid">
                              {msg.citations.map((cite, index) => (
                                <div key={index} className="citation-badge" title={`Score: ${(cite.score * 100).toFixed(0)}%`}>
                                  <span className="cite-icon">📄</span>
                                  <span className="cite-name">{cite.document_name}</span>
                                  <span className="cite-score">
                                    {Math.round(cite.score * 100)}% Match
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })
              )}

              {/* Bouncing Dot typing loader */}
              {isSending && (
                <div className="message-row assistant-row">
                  <div className="message-bubble loading-bubble">
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                    <span className="typing-dot"></span>
                  </div>
                </div>
              )}

              {/* Anchor for auto-scroll */}
              <div ref={messagesEndRef} />
            </div>

            {/* Footer Input Area */}
            <footer className="chat-input-container">
              <textarea
                placeholder="Ask anything about your workspace documents..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyPress}
                disabled={isSending}
                rows={1}
              />
              <button
                className="chat-send-btn"
                onClick={handleSend}
                disabled={isSending || !input.trim()}
              >
                Send ➔
              </button>
            </footer>
          </>
        ) : (
          <div className="chat-welcome-state">
            <div className="welcome-graphic">💬</div>
            <h2>AI Study Assistant Chat</h2>
            <p>Select an existing session from the sidebar, or click <strong>+ New Chat</strong> to begin querying your ingested documents using RAG.</p>
          </div>
        )}
      </main>
    </div>
  );
});

export default ChatInterface;
