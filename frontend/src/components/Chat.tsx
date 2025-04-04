'use client'

import { useState, useRef, useEffect } from 'react'
import Image from 'next/image'
import { api, ChatMessage, AnalysisResult } from '@/lib/api'

interface Message extends ChatMessage {
  id: string;
  pending?: boolean;
  imageUrl?: string;
  analysis?: AnalysisResult;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [image, setImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() && !image) return

    // Add user message immediately
    const userMessage: Message = {
      id: Date.now().toString(),
      content: input,
      is_user: true,
      imageUrl: imagePreview || undefined,
    }
    
    // Add pending bot message
    const pendingBotMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: '',
      is_user: false,
      pending: true,
    }
    
    setMessages(prev => [...prev, userMessage, pendingBotMessage])
    setSending(true)
    setInput('')

    try {
      // Send message and image to chat
      const response = await api.sendMessage(input || 'Analyze this image', image)
      
      if (!response || !Array.isArray(response) || response.length < 2) {
        throw new Error('Invalid response from server')
      }

      // Update user message and replace pending message with actual response
      setMessages(prev => prev.map(msg => {
        if (msg.id === userMessage.id) {
          return { ...msg, ...response[0] }
        }
        if (msg.id === pendingBotMessage.id) {
          return { ...response[1], id: pendingBotMessage.id }
        }
        return msg
      }))

      // Clear image after successful send
      setImage(null)
      setImagePreview(null)
    } catch (error) {
      console.error('Failed to send message:', error)
      // Remove pending message and show error
      setMessages(prev => prev.filter(msg => msg.id !== pendingBotMessage.id))
      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        content: 'Sorry, there was an error processing your request. Please try again.',
        is_user: false,
      }])
    } finally {
      setSending(false)
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file && file.type.startsWith('image/')) {
      setImage(file)
      setImagePreview(URL.createObjectURL(file))
    }
  }

  return (
    <div className="flex flex-col h-full bg-gray-900">
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 min-h-0">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${
              message.is_user ? 'justify-end' : 'justify-start'
            } animate-fade-in`}
          >
            {/* Avatar */}
            {!message.is_user && (
              <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center mr-2">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23-.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
                </svg>
              </div>
            )}
            
            <div
              className={`max-w-[80%] rounded-lg p-4 shadow-lg ${
                message.is_user
                  ? 'bg-blue-600 text-white ml-4'
                  : 'bg-gray-800 text-gray-100'
              }`}
            >
              {message.pending ? (
                <div className="flex space-x-2 h-6 items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
              ) : (
                <div className="space-y-4">
                  {message.imageUrl && (
                    <div className="relative w-full h-[300px]">
                      <Image
                        src={message.imageUrl}
                        alt={message.is_user ? "Uploaded image" : "Predicted image"}
                        fill
                        className="object-contain rounded-lg"
                      />
                    </div>
                  )}
                  {message.analysis && (
                    <div className="bg-gray-700 p-4 rounded-lg space-y-2">
                      <h3 className="font-medium text-blue-400">Image Analysis Results:</h3>
                      <ul className="space-y-1">
                        {message.analysis.predictions.map((pred, idx) => (
                          <li key={idx} className="text-sm">
                            {pred.class}: {(pred.confidence * 100).toFixed(1)}% confidence
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div className="prose prose-invert max-w-none">
                    {message.content}
                  </div>
                </div>
              )}
            </div>
            
            {/* User Avatar */}
            {message.is_user && (
              <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center ml-2">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21c-2.676 0-5.216-.584-7.499-1.632z" />
                </svg>
              </div>
            )}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Form */}
      <div className="flex-shrink-0 border-t border-gray-800 bg-gray-900">
        <form onSubmit={handleSubmit} className="p-6">
          {imagePreview && (
            <div className="flex items-center gap-4 text-sm text-gray-300 bg-gray-800 p-4 rounded-lg mb-4">
              <div className="relative w-16 h-16">
                <Image
                  src={imagePreview}
                  alt="Selected image"
                  fill
                  className="object-cover rounded-lg"
                />
              </div>
              <div className="flex-1">
                <div className="font-medium">Selected Image</div>
                <div className="text-gray-400 text-sm">Click analyze or add a message</div>
              </div>
              <button
                type="button"
                onClick={() => {
                  setImage(null)
                  setImagePreview(null)
                }}
                className="text-red-400 hover:text-red-300"
              >
                Remove
              </button>
            </div>
          )}

          <div className="flex gap-4 bg-gray-800 p-4 rounded-xl">
            <label className="flex-none">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-lg bg-gray-700 text-gray-300 cursor-pointer hover:bg-gray-600 transition-colors">
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </span>
            </label>

            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={image ? "Add a message or press Enter to analyze" : "Type your message..."}
              className="flex-1 bg-transparent text-gray-100 placeholder-gray-400 px-4 py-2 focus:outline-none"
              disabled={sending}
            />

            <button
              type="submit"
              disabled={sending || (!input.trim() && !image)}
              className={`px-6 py-2 rounded-lg text-white font-medium transition-colors ${
                sending || (!input.trim() && !image)
                  ? 'bg-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 hover:bg-blue-700'
              }`}
            >
              {sending ? 'Sending...' : (image && !input.trim() ? 'Analyze' : 'Send')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}