import type { Metadata } from 'next'
import { Inter, Geist_Mono } from 'next/font/google'
import './globals.css'
import Sidebar from '@/components/nav/Sidebar'

const inter = Inter({ variable: '--font-sans', subsets: ['latin'] })
const geistMono = Geist_Mono({ variable: '--font-geist-mono', subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'SkillMap',
  description: 'Your AI-powered career learning platform',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`dark ${inter.variable} ${geistMono.variable}`}>
      <body className="flex h-screen overflow-hidden bg-background text-foreground antialiased">
        <Sidebar />
        <main className="flex flex-1 flex-col overflow-hidden">{children}</main>
      </body>
    </html>
  )
}
