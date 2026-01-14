'use client'

import { motion } from 'framer-motion'
import {
    Frown, Smile, Meh, CloudRain, Sun, Coffee,
    Flame, Heart, Zap, Brain, Music, Moon
} from 'lucide-react'

const moods = [
    { id: 'stressed', label: 'Stressed', icon: Flame, color: 'from-red-500 to-orange-500' },
    { id: 'sad', label: 'Sad', icon: CloudRain, color: 'from-blue-500 to-indigo-500' },
    { id: 'bored', label: 'Bored', icon: Meh, color: 'from-gray-500 to-slate-500' },
    { id: 'anxious', label: 'Anxious', icon: Zap, color: 'from-yellow-500 to-amber-500' },
    { id: 'happy', label: 'Happy', icon: Smile, color: 'from-green-500 to-emerald-500' },
    { id: 'lonely', label: 'Lonely', icon: Moon, color: 'from-purple-500 to-violet-500' },
    { id: 'tired', label: 'Tired', icon: Coffee, color: 'from-amber-600 to-orange-600' },
    { id: 'curious', label: 'Curious', icon: Brain, color: 'from-cyan-500 to-teal-500' },
    { id: 'romantic', label: 'Romantic', icon: Heart, color: 'from-pink-500 to-rose-500' },
    { id: 'adventurous', label: 'Adventurous', icon: Sun, color: 'from-orange-500 to-yellow-500' },
]

interface MoodSelectorProps {
    onSelect: (mood: string) => void
}

export function MoodSelector({ onSelect }: MoodSelectorProps) {
    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.05,
            },
        },
    }

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 },
    }

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4 max-w-4xl mx-auto"
        >
            {moods.map((mood) => (
                <motion.button
                    key={mood.id}
                    variants={item}
                    whileHover={{ scale: 1.05, y: -5 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={() => onSelect(mood.id)}
                    className={`
            group relative p-6 rounded-2xl bg-gradient-to-br ${mood.color}
            shadow-lg hover:shadow-2xl transition-shadow
          `}
                >
                    <div className="absolute inset-0 rounded-2xl bg-black/20 group-hover:bg-black/10 transition-colors" />
                    <div className="relative flex flex-col items-center gap-3">
                        <mood.icon className="w-8 h-8 text-white" />
                        <span className="text-white font-medium">{mood.label}</span>
                    </div>
                </motion.button>
            ))}
        </motion.div>
    )
}
