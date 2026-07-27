import { createContext, useState, useEffect, useMemo } from 'react';
import type { ReactNode } from 'react';
import axios from 'axios';
import { conversationApi, chatApi } from '../api/chat';
import { usageTracker } from '../utils/usageTracker';
import { useWorkspace } from '../hooks/useWorkspace';
import type {
  ConversationSummaryItem,
  ConversationItem,
  MessageItem,
} from '../types/chat.ts';

interface ChatContextType {
  conversations: ConversationSummaryItem[];
  activeConversation: ConversationItem | null;
  messages: MessageItem[];
  isLoading: boolean;
  isSending: boolean;
  error: string | null;
  createConversation: () => Promise<ConversationItem>;
  selectConversation: (id: string | null) => Promise<void>;
  renameConversation: (id: string, title: string) => Promise<void>;
  deleteConversation: (id: string) => Promise<void>;
  sendMessage: (question: string) => Promise<void>;
  clearError: () => void;
}

export const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const { activeWorkspace } = useWorkspace();
  const [conversations, setConversations] = useState<ConversationSummaryItem[]>([]);
  const [activeConversation, setActiveConversation] = useState<ConversationItem | null>(null);
  const [messages, setMessages] = useState<MessageItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const clearError = () => setError(null);

  // Helper to extract Axios error messages safely
  const getErrorMessage = (err: unknown, defaultMsg: string): string => {
    if (axios.isAxiosError(err)) {
      const data = err.response?.data;
      if (data && typeof data === 'object' && 'detail' in data) {
        return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
      }
      return err.message;
    }
    if (err instanceof Error) {
      return err.message;
    }
    return defaultMsg;
  };

  /**
   * Load active conversation threads for current workspace.
   */
  const fetchConversations = async (workspaceId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await conversationApi.list(workspaceId, 1, 100);
      setConversations(res.items);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to load conversations.'));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Select a conversation and fetch its message list.
   */
  const selectConversation = async (id: string | null) => {
    if (!id) {
      setActiveConversation(null);
      setMessages([]);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const details = await conversationApi.get(id);
      setActiveConversation(details);
      
      const msgRes = await conversationApi.getMessages(id, 1, 200);
      setMessages(msgRes.messages);
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to retrieve chat messages.'));
      setActiveConversation(null);
      setMessages([]);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Create a new conversation session.
   */
  const createConversation = async (): Promise<ConversationItem> => {
    if (!activeWorkspace) throw new Error('No active workspace selected.');

    setIsLoading(true);
    setError(null);
    try {
      const newConv = await conversationApi.create(activeWorkspace.id);
      
      // Update list
      setConversations((prev) => [
        {
          id: newConv.id,
          title: newConv.title,
          last_message_preview: null,
          last_message_at: newConv.last_message_at,
        },
        ...prev,
      ]);
      
      // Automatically select the new thread
      setActiveConversation(newConv);
      setMessages([]);
      return newConv;
    } catch (err) {
      const errMsg = getErrorMessage(err, 'Failed to create new conversation.');
      setError(errMsg);
      throw err;
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Rename a conversation session.
   */
  const renameConversation = async (id: string, title: string) => {
    setError(null);
    try {
      const updated = await conversationApi.rename(id, title);
      
      // Update list preview
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title: updated.title } : c))
      );

      // Update current details if active
      if (activeConversation?.id === id) {
        setActiveConversation(updated);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to rename conversation.'));
      throw err;
    }
  };

  /**
   * Delete (archive/delete) a conversation session.
   */
  const deleteConversation = async (id: string) => {
    setError(null);
    try {
      await conversationApi.delete(id);
      
      // Remove from list
      setConversations((prev) => prev.filter((c) => c.id !== id));
      
      // Reset if we deleted the currently active thread
      if (activeConversation?.id === id) {
        setActiveConversation(null);
        setMessages([]);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to delete conversation.'));
      throw err;
    }
  };

  /**
   * Send user message to conversation and await AI answer.
   */
  const sendMessage = async (question: string) => {
    if (!activeConversation) return;

    // Create optimistic user message
    const userMsg: MessageItem = {
      id: `temp-${Date.now()}`,
      role: 'USER',
      content: question,
      created_at: new Date().toISOString(),
      citations: [],
    };

    // Optimistically update message feed
    setMessages((prev) => [...prev, userMsg]);
    setIsSending(true);
    setError(null);

    try {
      const res = await chatApi.send(activeConversation.id, question);

      // Auto-log AI token & cost usage
      if (activeWorkspace) {
        const pTokens = (res as any).token_usage?.prompt_tokens || Math.floor(question.length * 1.5 + 800);
        const cTokens = (res as any).token_usage?.completion_tokens || Math.floor(res.answer.length * 0.4);
        usageTracker.logUsage(
          activeWorkspace.id,
          'RAG Chat',
          'gemini-2.5-flash',
          pTokens,
          cTokens,
          1250,
          `Query: "${question.slice(0, 30)}..." | Citations: ${res.citations?.length || 0}`
        );
      }

      const assistantMsg: MessageItem = {
        id: res.message_id,
        role: 'ASSISTANT',
        content: res.answer,
        created_at: new Date().toISOString(),
        citations: res.citations,
      };

      // Replace optimistic message list
      setMessages((prev) => [...prev, assistantMsg]);

      // Fetch updated conversation title (in case it auto-generated a name)
      const updatedConv = await conversationApi.get(activeConversation.id);
      setActiveConversation(updatedConv);

      // Refresh list to show updated names and previews
      if (activeWorkspace) {
        await fetchConversations(activeWorkspace.id);
      }
    } catch (err) {
      setError(getErrorMessage(err, 'Failed to obtain answer from Gemini.'));
    } finally {
      setIsSending(false);
    }
  };

  // Sync: Reload conversations whenever workspace changes
  useEffect(() => {
    if (!activeWorkspace) {
      setConversations([]);
      setActiveConversation(null);
      setMessages([]);
      return;
    }

    fetchConversations(activeWorkspace.id);
    setActiveConversation(null);
    setMessages([]);
  }, [activeWorkspace]);

  const value = useMemo(
    () => ({
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
    }),
    [conversations, activeConversation, messages, isLoading, isSending, error]
  );

  return <ChatContext.Provider value={value}>{children}</ChatContext.Provider>;
}
