'use client'

import { motion } from 'framer-motion'
import { Film, RotateCcw } from 'lucide-react'

interface HeaderProps {
    onReset: () => void
    showReset: boolean
}

export function Header({ onReset, showReset }: HeaderProps) {
    return (
        <header className="border-b border-white/5 backdrop-blur-sm sticky top-0 z-50">
            <div className="container mx-auto px-4 py-4 flex items-center justify-between">
                <motion.div
                    className="flex items-center gap-3"
                    whileHover={{ scale: 1.02 }}
                >
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                        <Film className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-white">MovieMood</h1>
                        <p className="text-xs text-dark-400">Find your perfect film</p>
                    </div>
                </motion.div>

                {showReset && (
                    <motion.button
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        onClick={onReset}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-dark-300 hover:text-white"
                    >
                        <RotateCcw className="w-4 h-4" />
                        <span className="text-sm">Start Over</span>
                    </motion.button>
                )}
            </div>
        </header>
    )
}
