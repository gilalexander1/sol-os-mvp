'use client'

import React, { useState, useRef, useEffect } from 'react'
import { Send, Brain, MessageCircle } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'sol'
  content: string
  timestamp: Date
  personality_indicators?: Record<string, number>
}

interface ChatInterfaceProps {
  onNewMessage?: (message: Message) => void
}

export function ChatInterface({ onNewMessage }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'sol',
      content: "Hey there. What's on your mind today?",
      timestamp: new Date(),
      personality_indicators: { existential: 0.8, companionship: 0.9 }
    }
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState<string>('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input.trim(),
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId || undefined
        })
      })

      if (!response.ok) {
        throw new Error('Failed to send message')
      }

      const data = await response.json()
      
      // Update session ID if new
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id)
      }

      const solMessage: Message = {
        id: data.conversation_id || Date.now().toString(),
        type: 'sol',
        content: data.response,
        timestamp: new Date(),
        personality_indicators: data.personality_indicators
      }

      setMessages(prev => [...prev, solMessage])
      
      if (onNewMessage) {
        onNewMessage(solMessage)
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'sol',
        content: "I'm having some technical difficulties right now, but I'm here with you. Want to tell me more about what's on your mind?",
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const getPersonalityColor = (indicators?: Record<string, number>) => {
    if (!indicators) return 'from-purple-500 to-blue-500'
    
    const dominant = Object.entries(indicators).reduce((a, b) => 
      indicators[a[0]] > indicators[b[0]] ? a : b
    )?.[0]

    switch (dominant) {
      case 'existential':
        return 'from-purple-600 to-indigo-600'
      case 'thoughtful':
        return 'from-blue-500 to-cyan-500'
      case 'companionship':
        return 'from-green-500 to-teal-500'
      case 'engagement':
        return 'from-orange-500 to-yellow-500'
      default:
        return 'from-purple-500 to-blue-500'
    }
  }

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="p-4 border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg bg-gradient-to-r ${getPersonalityColor(messages[messages.length - 1]?.personality_indicators)} shadow-lg`}>
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Sol</h2>
            <p className="text-sm text-gray-300">Your ADHD companion</p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-3 rounded-2xl ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : `bg-gradient-to-r ${getPersonalityColor(message.personality_indicators)} text-white shadow-lg`
              }`}
            >
              {message.type === 'sol' && (
                <div className="flex items-center gap-2 mb-2 opacity-80">
                  <MessageCircle className="w-3 h-3" />
                  <span className="text-xs">Sol</span>
                </div>
              )}
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              {message.personality_indicators && (
                <div className="mt-2 pt-2 border-t border-white/20">
                  <div className="flex gap-2 text-xs opacity-70">
                    {Object.entries(message.personality_indicators)
                      .filter(([_, value]) => value > 0.3)
                      .map(([trait, value]) => (
                        <span key={trait} className="capitalize">
                          {trait}: {Math.round(value * 100)}%
                        </span>
                      ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="max-w-xs lg:max-w-md px-4 py-3 rounded-2xl bg-gradient-to-r from-purple-500 to-blue-500 text-white">
              <div className="flex items-center gap-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-white rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
                <span className="text-sm opacity-80">Sol is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="What's on your mind? (Shift+Enter for new line)"
            className="flex-1 px-4 py-3 bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500/50"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 focus:outline-none focus:ring-2 focus:ring-purple-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}