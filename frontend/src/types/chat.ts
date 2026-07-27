export interface CitationItem {
  document_id: string;
  document_name: string;
  page: string;
  score: number;
}

export interface MessageItem {
  id: string;
  role: "USER" | "ASSISTANT";
  content: string;
  created_at: string;
  citations: CitationItem[];
}

export type ChatMessage = MessageItem;

export interface ConversationItem {
  id: string;
  workspace_id: string;
  title: string;
  status: "ACTIVE" | "ARCHIVED";
  created_at: string;
  updated_at: string;
  last_message_at: string;
}

export interface ConversationSummaryItem {
  id: string;
  title: string;
  last_message_preview: string | null;
  last_message_at: string;
}

export interface ConversationListResponse {
  items: ConversationSummaryItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface MessageListResponse {
  messages: MessageItem[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
}

export interface ChatRequest {
  conversation_id: string;
  question: string;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  answer: string;
  citations: CitationItem[];
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}
