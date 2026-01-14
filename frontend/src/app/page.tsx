'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { MessageSquare, Palette, Film } from 'lucide-react'
import { MoodSelector } from '@/components/MoodSelector'
import { DesiredFeelingSelector } from '@/components/DesiredFeelingSelector'
import { MovieGrid } from '@/components/MovieGrid'
import { ChatInterface } from '@/components/ChatInterface'
import { Header } from '@/components/Header'
import { MovieRecommendation } from '@/types'

type Step = 'choose' | 'mood' | 'feeling' | 'results' | 'chat'

export default function Home() {
    const [step, setStep] = useState<Step>('choose')
    const [currentMood, setCurrentMood] = useState<string>('')
    const [desiredFeeling, setDesiredFeeling] = useState<string>('')
    const [recommendations, setRecommendations] = useState<MovieRecommendation[]>([])
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleMoodSelect = (mood: string) => {
        setCurrentMood(mood)
        setStep('feeling')
    }

    const handleFeelingSelect = async (feeling: string) => {
        setDesiredFeeling(feeling)
        setIsLoading(true)
        setError(null)

        try {
            const response = await fetch('/api/recommend/mood', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    current_mood: currentMood,
                    desired_feeling: feeling,
                    n_recommendations: 8,
                }),
            })

            if (!response.ok) {
                throw new Error('Failed to get recommendations')
            }

            const data = await response.json()
            setRecommendations(data)
            setStep('results')
        } catch (err) {
            setError('Could not fetch recommendations. Is the API running?')
            console.error(err)
        } finally {
            setIsLoading(false)
        }
    }

    const handleReset = () => {
        setStep('choose')
        setCurrentMood('')
        setDesiredFeeling('')
        setRecommendations([])
        setError(null)
    }

    const handleChatMovies = (movies: MovieRecommendation[]) => {
        setRecommendations(movies)
    }

    return (
        <main className="min-h-screen">
            <Header onReset={handleReset} showReset={step !== 'choose'} />

            <div className="container mx-auto px-4 py-8">
                <AnimatePresence mode="wait">
                    {/* Choose Mode */}
                    {step === 'choose' && (
                        <motion.div
                            key="choose"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="flex flex-col items-center justify-center min-h-[70vh]"
                        >
                            <motion.div
                                initial={{ scale: 0.9 }}
                                animate={{ scale: 1 }}
                                className="text-center mb-12"
                            >
                                <h1 className="text-5xl md:text-7xl font-bold mb-4">
                                    <span className="text-gradient">Find Your</span>
                                    <br />
                                    <span className="text-white">Perfect Movie</span>
                                </h1>
                                <p className="text-dark-400 text-lg md:text-xl max-w-2xl mx-auto">
                                    Choose how you'd like to discover your next film
                                </p>
                            </motion.div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto">
                                {/* Visual Selection */}
                                <motion.button
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setStep('mood')}
                                    className="glass-card p-8 text-left group hover:border-purple-500/50 transition-all"
                                >
                                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center mb-4 group-hover:from-purple-500/30 group-hover:to-pink-500/30 transition-colors">
                                        <Palette className="w-7 h-7 text-purple-400" />
                                    </div>
                                    <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-purple-300 transition-colors">
                                        Visual Mood Picker
                                    </h3>
                                    <p className="text-dark-400 text-sm">
                                        Select your current mood and desired feeling from beautiful visual cards
                                    </p>
                                    <div className="flex flex-wrap gap-2 mt-4">
                                        <span className="text-xs px-2 py-1 rounded-full bg-white/5 text-dark-400">Quick</span>
                                        <span className="text-xs px-2 py-1 rounded-full bg-white/5 text-dark-400">Easy</span>
                                        <span className="text-xs px-2 py-1 rounded-full bg-white/5 text-dark-400">Visual</span>
                                    </div>
                                </motion.button>

                                {/* Chat Mode */}
                                <motion.button
                                    whileHover={{ scale: 1.03 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setStep('chat')}
                                    className="glass-card p-8 text-left group hover:border-purple-500/50 transition-all"
                                >
                                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center mb-4 group-hover:from-blue-500/30 group-hover:to-cyan-500/30 transition-colors">
                                        <MessageSquare className="w-7 h-7 text-blue-400" />
                                    </div>
                                    <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-blue-300 transition-colors">
                                        Chat with AI
                                    </h3>
                                    <p className="text-dark-400 text-sm">
                                        Describe what you're in the mood for and get personalized suggestions
                                    </p>
                                    <div className="flex flex-wrap gap-2 mt-4">
                                        <span className="text-xs px-2 py-1 rounded-full bg-white/5 text-dark-400">Natural</span>
                                        <span className="text-xs px-2 py-1 rounded-full bg-white/5 text-dark-400">Conversational</span>
                                        <span className="text-xs px-2 py-1 rounded-full bg-white/5 text-dark-400">Smart</span>
                                    </div>
                                </motion.button>
                            </div>
                        </motion.div>
                    )}

                    {/* Mood Selection */}
                    {step === 'mood' && (
                        <motion.div
                            key="mood"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="flex flex-col items-center justify-center min-h-[70vh]"
                        >
                            <motion.div
                                initial={{ scale: 0.9 }}
                                animate={{ scale: 1 }}
                                className="text-center mb-12"
                            >
                                <h1 className="text-5xl md:text-7xl font-bold mb-4">
                                    <span className="text-gradient">How are you</span>
                                    <br />
                                    <span className="text-white">feeling today?</span>
                                </h1>
                                <p className="text-dark-400 text-lg md:text-xl max-w-2xl mx-auto">
                                    Tell us your mood, and we'll find the perfect movie to match or transform it.
                                </p>
                            </motion.div>

                            <MoodSelector onSelect={handleMoodSelect} />
                        </motion.div>
                    )}

                    {/* Feeling Selection */}
                    {step === 'feeling' && (
                        <motion.div
                            key="feeling"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                            className="flex flex-col items-center justify-center min-h-[70vh]"
                        >
                            <motion.div className="text-center mb-12">
                                <p className="text-purple-400 text-sm uppercase tracking-wider mb-2">
                                    Feeling {currentMood}
                                </p>
                                <h1 className="text-5xl md:text-6xl font-bold mb-4">
                                    <span className="text-white">What do you want</span>
                                    <br />
                                    <span className="text-gradient">to feel?</span>
                                </h1>
                                <p className="text-dark-400 text-lg max-w-xl mx-auto">
                                    Choose your desired emotional experience.
                                </p>
                            </motion.div>

                            <DesiredFeelingSelector
                                onSelect={handleFeelingSelect}
                                isLoading={isLoading}
                            />

                            {error && (
                                <motion.p
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="mt-6 text-red-400 text-center"
                                >
                                    {error}
                                </motion.p>
                            )}
                        </motion.div>
                    )}

                    {/* Chat Interface */}
                    {step === 'chat' && (
                        <motion.div
                            key="chat"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                        >
                            <div className="text-center mb-8">
                                <h1 className="text-4xl md:text-5xl font-bold mb-2">
                                    <span className="text-white">Chat with</span>{' '}
                                    <span className="text-gradient">MovieMood AI</span>
                                </h1>
                                <p className="text-dark-400">
                                    Describe what you're looking for in natural language
                                </p>
                            </div>

                            <ChatInterface onMoviesReceived={handleChatMovies} />
                        </motion.div>
                    )}

                    {/* Results */}
                    {step === 'results' && (
                        <motion.div
                            key="results"
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -20 }}
                        >
                            <div className="text-center mb-12">
                                <p className="text-purple-400 text-sm uppercase tracking-wider mb-2">
                                    {currentMood} → {desiredFeeling}
                                </p>
                                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                                    <span className="text-white">Your Perfect</span>{' '}
                                    <span className="text-gradient">Picks</span>
                                </h1>
                                <p className="text-dark-400 text-lg">
                                    Curated just for your mood journey
                                </p>
                            </div>

                            <MovieGrid movies={recommendations} />
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </main>
    )
}
