import { useInfiniteQuery } from '@tanstack/react-query';
import { Axios } from '../base-axios';
import type { ChatMessage } from '../types/chat';

interface MessagePage {
  messages: ChatMessage[];
  nextCursor?: number;
  hasMore: boolean;
}

export function useChatInfiniteQuery(workspaceId: string | null, conversationId: string | null) {
  return useInfiniteQuery<MessagePage>({
    queryKey: ['chatMessagesInfinite', workspaceId, conversationId],
    queryFn: async ({ pageParam = 0 }) => {
      if (!workspaceId || !conversationId) {
        return { messages: [], hasMore: false };
      }

      const response = await Axios.get<ChatMessage[]>(
        `/chat/conversations/${conversationId}/messages`,
        {
          params: { offset: pageParam, limit: 20 },
        }
      );

      const messages = response.data || [];
      const hasMore = messages.length === 20;

      return {
        messages,
        nextCursor: hasMore ? (pageParam as number) + 20 : undefined,
        hasMore,
      };
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage) => lastPage.nextCursor,
    enabled: Boolean(workspaceId && conversationId),
  });
}

export default useChatInfiniteQuery;
