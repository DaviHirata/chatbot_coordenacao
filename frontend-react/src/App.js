import React, { useState, useEffect, useRef } from 'react';
import { Menu, Send } from 'lucide-react';
import ChatMessage from './components/ChatMessage';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: 'Olá! Meu nome é Ada, a assistente virtual do curso de Sistemas para Internet. Como posso ajudá-lo hoje?',
      isUser: false,
      timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = () => {
    if (inputValue.trim() === '') return;

    const userMessage = {
      id: messages.length + 1,
      text: inputValue,
      isUser: true,
      timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');

    fetch('http://localhost:8080/chat/ask', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question: inputValue }),
    })
    .then(response => response.json())
    .then(data => {
      const botMessage = {
        id: messages.length + 2,
        text: data.answer,
        isUser: false,
        timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMessage]);
    })
    .catch(error => {
      console.error('Error:', error);
      const botMessage = {
        id: messages.length + 2,
        text: 'Desculpe, não consigo me conectar ao servidor. Tente novamente mais tarde.',
        isUser: false,
        timestamp: new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, botMessage]);
    });
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col bg-gray-50">
      {/* Header */}
      <header className="bg-blue-600 text-white shadow-md">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button className="text-white hover:bg-blue-700 p-2 rounded-md lg:hidden">
              <Menu className="h-5 w-5" />
            </button>
            <div>
              <h1 className="text-white font-semibold text-lg">Ada - Chatbot do Curso de Sistemas para Internet</h1>
              <p className="text-sm text-blue-100">Universidade Federal de Santa Maria</p>
            </div>
          </div>
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 max-w-5xl w-full mx-auto flex flex-col overflow-hidden">
        <div className="flex-1 px-4 py-6 overflow-y-auto">
          <div className="space-y-4">
            {messages.map(message => (
              <ChatMessage
                key={message.id}
                message={message.text}
                isUser={message.isUser}
                timestamp={message.timestamp}
              />
            ))}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200 bg-white">
          <div className="max-w-5xl mx-auto px-4 py-4">
            <div className="flex gap-2 items-center">
              <input
                type="text"
                placeholder="Digite sua mensagem..."
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button 
                onClick={handleSendMessage}
                className="bg-blue-600 hover:bg-blue-700 text-white p-2 rounded-md"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
            <p className="mt-2 text-xs text-gray-500 text-center">
              Dúvidas sobre cursos, matrículas, calendário acadêmico e mais
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}