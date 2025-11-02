import { useState, useRef, useEffect } from 'react';
import { Send, Menu, Bot, User } from 'lucide-react';

// ChatMessage Component
export default function ChatMessage({ message, isUser, timestamp }) {
  return (
    <div className={`flex gap-3 mb-4 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`h-8 w-8 rounded-full flex items-center justify-center ${isUser ? 'bg-blue-100' : 'bg-blue-600'}`}>
        {isUser ? (
          <User className={`h-4 w-4 ${isUser ? 'text-blue-600' : 'text-white'}`} />
        ) : (
          <Bot className="h-4 w-4 text-white" />
        )}
      </div>
      
      <div className={`flex flex-col max-w-[75%] ${isUser ? 'items-end' : 'items-start'}`}>
        <div className={`rounded-lg px-4 py-2 ${
          isUser 
            ? 'bg-blue-100 text-blue-900' 
            : 'bg-white border border-gray-200'
        }`}>
          <p className="whitespace-pre-wrap">{message}</p>
        </div>
        <span className="mt-1 text-xs text-gray-500">{timestamp}</span>
      </div>
    </div>
  );
}