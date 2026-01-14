import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
    title: 'MovieMood - Find Films That Match Your Feelings',
    description: 'Discover movies based on your mood. Tell us how you feel, and we\'ll recommend the perfect film.',
    keywords: ['movies', 'mood', 'recommendations', 'feelings', 'entertainment'],
    authors: [{ name: 'Abhinav Choudhry' }],
    openGraph: {
        title: 'MovieMood - Find Films That Match Your Feelings',
        description: 'Discover movies based on your mood.',
        type: 'website',
    },
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className="dark">
            <body className={inter.className}>
                <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-950">
                    {/* Background effects */}
                    <div className="fixed inset-0 overflow-hidden pointer-events-none">
                        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl" />
                        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-pink-500/20 rounded-full blur-3xl" />
                        <div className="absolute -bottom-40 right-1/3 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl" />
                    </div>

                    {/* Content */}
                    <div className="relative z-10">
                        {children}
                    </div>
                </div>
            </body>
        </html>
    )
}
