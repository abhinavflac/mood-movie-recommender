'use client'

import { motion } from 'framer-motion'
import Image from 'next/image'
import { Star, Gauge, Heart, Zap } from 'lucide-react'
import { MovieRecommendation } from '@/types'

interface MovieGridProps {
    movies: MovieRecommendation[]
}

export function MovieGrid({ movies }: MovieGridProps) {
    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1,
            },
        },
    }

    const item = {
        hidden: { opacity: 0, y: 30 },
        show: { opacity: 1, y: 0 },
    }

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
        >
            {movies.map((movie, index) => (
                <motion.div
                    key={index}
                    variants={item}
                    className="group"
                >
                    <div className="glass-card overflow-hidden card-hover">
                        {/* Poster */}
                        <div className="relative aspect-[2/3] bg-dark-800">
                            {movie.poster_url ? (
                                <Image
                                    src={movie.poster_url}
                                    alt={movie.title}
                                    fill
                                    className="object-cover group-hover:scale-105 transition-transform duration-500"
                                    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 25vw"
                                />
                            ) : (
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-dark-500 text-6xl">🎬</span>
                                </div>
                            )}

                            {/* Match score badge */}
                            <div className="absolute top-3 right-3">
                                <div className="px-3 py-1 rounded-full bg-black/70 backdrop-blur-sm">
                                    <span className="text-sm font-semibold text-gradient">
                                        {Math.round(movie.match_score * 100)}% match
                                    </span>
                                </div>
                            </div>

                            {/* Gradient overlay */}
                            <div className="absolute inset-x-0 bottom-0 h-1/2 bg-gradient-to-t from-dark-950 to-transparent" />
                        </div>

                        {/* Content */}
                        <div className="p-5 space-y-4">
                            <div>
                                <h3 className="font-bold text-lg text-white line-clamp-1 group-hover:text-purple-300 transition-colors">
                                    {movie.title}
                                </h3>
                                <p className="text-sm text-dark-400 mt-1 line-clamp-2">
                                    {movie.overview}
                                </p>
                            </div>

                            {/* Genres */}
                            <div className="flex flex-wrap gap-2">
                                {movie.genres?.slice(0, 3).map((genre, i) => (
                                    <span
                                        key={i}
                                        className="px-2 py-1 text-xs rounded-full bg-white/5 text-dark-300"
                                    >
                                        {genre}
                                    </span>
                                ))}
                            </div>

                            {/* Scores */}
                            <div className="flex items-center justify-between pt-2 border-t border-white/5">
                                <div className="flex items-center gap-1 text-sm">
                                    <Zap className="w-4 h-4 text-yellow-500" />
                                    <span className="text-dark-300">{movie.intensity_score}</span>
                                </div>
                                <div className="flex items-center gap-1 text-sm">
                                    <Heart className="w-4 h-4 text-pink-500" />
                                    <span className="text-dark-300">{movie.comfort_score}</span>
                                </div>
                            </div>

                            {/* Emotions */}
                            <div className="pt-2">
                                <p className="text-xs text-dark-500 mb-2">Dominant emotions</p>
                                <div className="flex flex-wrap gap-1">
                                    {movie.dominant_emotions?.slice(0, 3).map((emotion, i) => (
                                        <span
                                            key={i}
                                            className="px-2 py-1 text-xs rounded-md bg-purple-500/10 text-purple-400"
                                        >
                                            {emotion.replace('_', ' ')}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            {/* Explanation */}
                            <p className="text-sm text-dark-400 italic">
                                "{movie.explanation}"
                            </p>
                        </div>
                    </div>
                </motion.div>
            ))}
        </motion.div>
    )
}
