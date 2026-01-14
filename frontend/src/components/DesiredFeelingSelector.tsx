'use client'

import { motion } from 'framer-motion'
import {
    Smile, Zap, Lightbulb, Droplets, Laugh,
    Brain, Ghost, Heart, Sparkles, Leaf, Stars, Loader2
} from 'lucide-react'

const feelings = [
    { id: 'feel-good', label: 'Feel Good', icon: Smile, description: 'Uplifting & positive vibes' },
    { id: 'thrilled', label: 'Thrilled', icon: Zap, description: 'Edge-of-seat excitement' },
    { id: 'inspired', label: 'Inspired', icon: Lightbulb, description: 'Motivation & hope' },
    { id: 'cry', label: 'A Good Cry', icon: Droplets, description: 'Cathartic emotional release' },
    { id: 'laugh', label: 'Laugh', icon: Laugh, description: 'Pure comedy gold' },
    { id: 'think', label: 'Think Deep', icon: Brain, description: 'Mind-bending stories' },
    { id: 'scared', label: 'Scared', icon: Ghost, description: 'Safe thrills & chills' },
    { id: 'romantic', label: 'Romantic', icon: Heart, description: 'Love & connection' },
    { id: 'empowered', label: 'Empowered', icon: Sparkles, description: 'Strength & triumph' },
    { id: 'relaxed', label: 'Relaxed', icon: Leaf, description: 'Calm & cozy' },
    { id: 'amazed', label: 'Amazed', icon: Stars, description: 'Awe & wonder' },
]

interface DesiredFeelingSelectorProps {
    onSelect: (feeling: string) => void
    isLoading: boolean
}

export function DesiredFeelingSelector({ onSelect, isLoading }: DesiredFeelingSelectorProps) {
    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.03,
            },
        },
    }

    const item = {
        hidden: { opacity: 0, scale: 0.8 },
        show: { opacity: 1, scale: 1 },
    }

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 max-w-5xl mx-auto"
        >
            {feelings.map((feeling) => (
                <motion.button
                    key={feeling.id}
                    variants={item}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.97 }}
                    onClick={() => onSelect(feeling.id)}
                    disabled={isLoading}
                    className={`
            group relative p-5 rounded-2xl glass-card
            hover:bg-white/10 transition-all duration-300
            hover:border-purple-500/50 hover:shadow-lg hover:shadow-purple-500/10
            disabled:opacity-50 disabled:cursor-not-allowed
            text-left
          `}
                >
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center group-hover:from-purple-500/30 group-hover:to-pink-500/30 transition-colors">
                            {isLoading ? (
                                <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
                            ) : (
                                <feeling.icon className="w-6 h-6 text-purple-400" />
                            )}
                        </div>
                        <div>
                            <h3 className="font-semibold text-white group-hover:text-purple-300 transition-colors">
                                {feeling.label}
                            </h3>
                            <p className="text-sm text-dark-400 mt-1">
                                {feeling.description}
                            </p>
                        </div>
                    </div>
                </motion.button>
            ))}
        </motion.div>
    )
}
