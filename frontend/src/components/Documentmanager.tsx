import { useState } from "react";
import type {FormEvent , ChangeEvent} from "react"
import {useDcocument} from '../hooks/useDocument'
import type { DocumentItem } from "../types/document";


function formatBytes(bytes:number , decimal=2):
string{
    if (bytes==0) return '0 Bytes';

    const k=1024;
    const dm=decimal < 0?0 :decimal;
    const sizes =['Bytes' , 'KB' , 'MB' , 'GB'];
    const i =Math.floor(Math.log(bytes)) / Math.log(k);
    return parseFloat((bytes /Math.pow(k,i)).toFixed(dm))+' ' +sizes[i];
}


export function DocumentManger(){
    const{
        documents,
        isLoading,
        error:apiError,
        totalCount,
        currentPage,
        total_pages,
        fetchDocuments,
        uploadDocument,
        deleteDocument,
        clearError
    }=useDcocument();
}