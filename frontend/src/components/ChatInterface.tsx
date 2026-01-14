'use client'

import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Bot, User, Sparkles, Film, Loader2 } from 'lucide-react'
import { MovieRecommendation } from '@/types'

interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    movies?: MovieRecommendation[]
    timestamp: Date
}

interface ChatInterfaceProps {
    onMoviesReceived?: (movies: MovieRecommendation[]) => void
}

const SUGGESTIONS = [
    "I'm feeling stressed and need something uplifting",
    "Suggest a movie for a rainy Sunday afternoon",
    "I want to watch something mind-bending",
    "Need a good cry, what should I watch?",
    "Something romantic but not cheesy",
    "I'm bored, give me an action-packed thriller",
]

export function ChatInterface({ onMoviesReceived }: ChatInterfaceProps) {
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            role: 'assistant',
            content: "Hey! 👋 I'm your movie mood assistant. Tell me how you're feeling or what kind of movie experience you're looking for, and I'll find the perfect films for you!",
            timestamp: new Date(),
        }
    ])
    const [input, setInput] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const messagesEndRef = useRef<HTMLDivElement>(null)
    const inputRef = useRef<HTMLInputElement>(null)

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    const handleSend = async () => {
        if (!input.trim() || isLoading) return

        const userMessage: Message = {
            id: Date.now().toString(),
            role: 'user',
            content: input,
            timestamp: new Date(),
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setIsLoading(true)

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: input }),
            })

            if (!response.ok) throw new Error('Failed to get response')

            const data = await response.json()

            const assistantMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: data.response,
                movies: data.movies,
                timestamp: new Date(),
            }

            setMessages(prev => [...prev, assistantMessage])

            if (data.movies && onMoviesReceived) {
                onMoviesReceived(data.movies)
            }
        } catch (error) {
            const errorMessage: Message = {
                id: (Date.now() + 1).toString(),
                role: 'assistant',
                content: "Oops! I couldn't process that. Make sure the backend is running. Try describing your mood or what kind of movie experience you want!",
                timestamp: new Date(),
            }
            setMessages(prev => [...prev, errorMessage])
        } finally {
            setIsLoading(false)
        }
    }

    const handleSuggestionClick = (suggestion: string) => {
        setInput(suggestion)
        inputRef.current?.focus()
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSend()
        }
    }

    return (
        <div className="flex flex-col h-[600px] max-w-3xl mx-auto">
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                <AnimatePresence>
                    {messages.map((message) => (
                        <motion.div
                            key={message.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            {message.role === 'assistant' && (
                                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center flex-shrink-0">
                                    <Bot className="w-4 h-4 text-white" />
                                </div>
                            )}

                            <div className={`max-w-[80%] ${message.role === 'user' ? 'order-first' : ''}`}>
                                <div
                                    className={`rounded-2xl px-4 py-3 ${message.role === 'user'
                                            ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white'
                                            : 'glass-card text-white'
                                        }`}
                                >
                                    <p className="text-sm leading-relaxed">{message.content}</p>
                                </div>

                                {/* Movie recommendations in chat */}
                                {message.movies && message.movies.length > 0 && (
                                    <div className="mt-3 space-y-2">
                                        {message.movies.slice(0, 4).map((movie, idx) => (
                                            <motion.div
                                                key={idx}
                                                initial={{ opacity: 0, x: -20 }}
                                                animate={{ opacity: 1, x: 0 }}
                                                transition={{ delay: idx * 0.1 }}
                                                className="glass-card p-3 rounded-xl"
                                            >
                                                <div className="flex gap-3">
                                                    {movie.poster_url && (
                                                        <img
                                                            src={movie.poster_url}
                                                            alt={movie.title}
                                                            className="w-12 h-18 object-cover rounded-lg"
                                                        />
                                                    )}
                                                    <div className="flex-1 min-w-0">
                                                        <h4 className="font-semibold text-white text-sm truncate">
                                                            {movie.title}
                                                        </h4>
                                                        <p className="text-xs text-dark-400 mt-1 line-clamp-2">
                                                            {movie.explanation}
                                                        </p>
                                                        <div className="flex items-center gap-2 mt-2">
                                                            <span className="text-xs px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-400">
                                                                {Math.round(movie.match_score * 100)}% match
                                                            </span>
                                                            <span className="text-xs text-dark-500">
                                                                {movie.genres?.slice(0, 2).join(', ')}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            {message.role === 'user' && (
                                <div className="w-8 h-8 rounded-full bg-dark-700 flex items-center justify-center flex-shrink-0">
                                    <User className="w-4 h-4 text-dark-300" />
                                </div>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>

                {isLoading && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-3"
                    >
                        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="glass-card rounded-2xl px-4 py-3">
                            <div className="flex items-center gap-2">
                                <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />
                                <span className="text-sm text-dark-400">Finding perfect movies for you...</span>
                            </div>
                        </div>
                    </motion.div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            {messages.length <= 1 && (
                <div className="px-4 pb-3">
                    <p className="text-xs text-dark-500 mb-2">Try asking:</p>
                    <div className="flex flex-wrap gap-2">
                        {SUGGESTIONS.slice(0, 3).map((suggestion, idx) => (
                            <button
                                key={idx}
                                onClick={() => handleSuggestionClick(suggestion)}
                                className="text-xs px-3 py-1.5 rounded-full glass-card hover:bg-white/10 transition-colors text-dark-300 hover:text-white"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-white/5">
                <div className="flex gap-3">
                    <div className="flex-1 relative">
                        <input
                            ref={inputRef}
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={handleKeyDown}
                            placeholder="Describe your mood or what you want to watch..."
                            className="w-full px-4 py-3 rounded-xl bg-dark-800 border border-white/10 text-white placeholder-dark-500 focus:outline-none focus:border-purple-500/50 focus:ring-2 focus:ring-purple-500/20 transition-all"
                            disabled={isLoading}
                        />
                        <Sparkles className="absolute right-4 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-500" />
                    </div>
                    <button
                        onClick={handleSend}
                        disabled={!input.trim() || isLoading}
                        className="px-4 py-3 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                        <Send className="w-5 h-5 text-white" />
                    </button>
                </div>
            </div>
        </div>
    )
}
