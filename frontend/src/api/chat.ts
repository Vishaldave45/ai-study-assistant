import apiClient from "./client";
import type {
  ConversationListResponse,
  ConversationItem,
  MessageListResponse,
  ChatResponse,
} from "../types/chat.ts";

export const conversationApi = {
  // Lists conversations for a workspace
  list: async (workspaceId: string, page: number = 1, pageSize: number = 10): Promise<ConversationListResponse> => {
    const response = await apiClient.get<ConversationListResponse>("/conversations", {
      params: { workspace_id: workspaceId, page, page_size: pageSize },
    });
    return response.data;
  },

  // Creates a new conversation
  create: async (workspaceId: string): Promise<ConversationItem> => {
    const response = await apiClient.post<ConversationItem>("/conversations", {
      workspace_id: workspaceId,
    });
    return response.data;
  },

  // Retrieves metadata for a single conversation
  get: async (conversationId: string): Promise<ConversationItem> => {
    const response = await apiClient.get<ConversationItem>(`/conversations/${conversationId}`);
    return response.data;
  },

  // Renames a conversation
  rename: async (conversationId: string, title: string): Promise<ConversationItem> => {
    const response = await apiClient.patch<ConversationItem>(`/conversations/${conversationId}`, {
      title,
    });
    return response.data;
  },

  // Archives a conversation
  archive: async (conversationId: string): Promise<ConversationItem> => {
    const response = await apiClient.patch<ConversationItem>(`/conversations/${conversationId}/archive`);
    return response.data;
  },

  // Deletes a conversation
  delete: async (conversationId: string): Promise<{ message: string }> => {
    const response = await apiClient.delete<{ message: string }>(`/conversations/${conversationId}`);
    return response.data;
  },

  // Fetches message history for a conversation (our new backend route!)
  getMessages: async (conversationId: string, page: number = 1, pageSize: number = 100): Promise<MessageListResponse> => {
    const response = await apiClient.get<MessageListResponse>(`/conversations/${conversationId}/messages`, {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },
};

export const chatApi = {
  // Sends a message to the AI and gets RAG-grounded response
  send: async (conversationId: string, question: string): Promise<ChatResponse> => {
    const response = await apiClient.post<ChatResponse>("/chat", {
      conversation_id: conversationId,
      question,
    });
    return response.data;
  },
};
