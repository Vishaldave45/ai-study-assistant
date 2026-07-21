import apiClient from "./client";
import type {
    WorkspaceCreateRequest,
     WorkspaceUpdateRequest,
      WorkspaceDetails,
      WorkSpaceListResponse,
      WorkspaceSummary,
} from '../types/workspace.ts';

import type { MessageResponse } from "../types/auth";



export const workspaceApi={


    list:async(params?:{
        page?:number,
        page_size?:number,
        query?:string;
        sort_by?:'name'|'created_at'|'updated_at';
        sort_order?:'asc'|'desc';
    }):Promise<WorkSpaceListResponse>=>{
        const response = await apiClient.get<WorkSpaceListResponse>('/workspaces',{params});
        return response.data;
    },

    create:async(data:WorkspaceCreateRequest):Promise<WorkspaceDetails>=>{
        const response = await apiClient.post<WorkspaceDetails>('/workspaces',data);
        return response.data;
    },

    get:async(workspaceId:string):Promise<WorkspaceDetails>=>{
        const response=await apiClient.get<WorkspaceDetails>(`/workspaces/${workspaceId}`);
        return response.data;
    },

    update:async(workspaceId:string,data:WorkspaceUpdateRequest):Promise<WorkspaceDetails>=>{
        const response = await apiClient.patch<WorkspaceDetails>(`/workspaces/${workspaceId}`,data);
        return response.data;
    },
    
    delete:async(workspaceId:string):Promise<MessageResponse>=>{
        const response = await apiClient.delete<MessageResponse>(`/workspaces/${workspaceId}`);
        return response.data;
    },

    summarize:async(workspaceId:string):Promise<WorkspaceSummary>=>{
        const response=await apiClient.get<WorkspaceSummary>(`/workspaces/${workspaceId}/summarize`);
        return response.data;
    },

}