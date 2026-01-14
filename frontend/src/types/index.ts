export interface MovieRecommendation {
    title: string
    overview: string
    genres: string[]
    poster_url: string
    dominant_emotions: string[]
    intensity_score: number
    comfort_score: number
    match_score: number
    explanation: string
}

export interface MoodOption {
    id: string
    label: string
    icon: string
    color: string
}

export interface FeelingOption {
    id: string
    label: string
    description: string
    icon: string
}
