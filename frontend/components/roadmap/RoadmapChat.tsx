'use client'

import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { ArrowUp, Loader2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

export default function RoadmapChat() {
  const [prompt, setPrompt] = useState('')
  const [markdown, setMarkdown] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isRejected, setIsRejected] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [markdown])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!prompt.trim() || loading) return

    setMarkdown('')
    setError('')
    setIsRejected(false)
    setLoading(true)

    try {
      const response = await fetch(`${API_URL}/api/roadmap/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt }),
      })

      if (!response.ok) throw new Error(`Server error: ${response.status}`)
      if (!response.body) throw new Error('No response body')

      const reader = response.body.getReader()
      const decoder = new TextDecoder()

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const text = decoder.decode(value, { stream: true })
        for (const line of text.split('\n')) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()
          if (data === '[DONE]') { setLoading(false); return }
          try {
            const parsed = JSON.parse(data)
            if (parsed.token) {
              if (parsed.type === 'rejection') setIsRejected(true)
              setMarkdown(prev => prev + parsed.token)
            }
            if (parsed.error) setError(parsed.error)
          } catch {}
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as unknown as React.FormEvent)
    }
  }

  return (
    <div className="flex h-full flex-col">
      {/* Roadmap output */}
      <div className="flex-1 overflow-y-auto px-8 py-8">
        {!markdown && !loading && (
          <div className="flex h-full flex-col items-center justify-center gap-3 text-center">
            <p className="text-2xl font-semibold text-foreground">Generate your roadmap</p>
            <p className="max-w-md text-sm text-muted-foreground">
              Tell me about your current role, experience, and where you want to go.
              I'll build you a personalized 6-month learning plan.
            </p>
          </div>
        )}

        {markdown && (
          <div
            className={`prose prose-sm mx-auto max-w-3xl ${
              isRejected
                ? 'prose-invert rounded-lg border border-amber-500/40 bg-amber-500/5 px-6 py-4'
                : 'prose-invert'
            }`}
          >
            <ReactMarkdown>{markdown}</ReactMarkdown>
            <div ref={bottomRef} />
          </div>
        )}

        {error && (
          <p className="mt-4 text-center text-sm text-destructive">{error}</p>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-border bg-background px-6 py-4">
        <form onSubmit={handleSubmit} className="mx-auto flex max-w-3xl items-end gap-3">
          <textarea
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="E.g. I'm a backend engineer with 3 years of Python experience. I want to become an ML engineer."
            rows={2}
            disabled={loading}
            className="flex-1 resize-none rounded-lg border border-border bg-muted px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!prompt.trim() || loading}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-opacity disabled:opacity-40"
          >
            {loading ? <Loader2 size={16} className="animate-spin" /> : <ArrowUp size={16} />}
          </button>
        </form>
        <p className="mt-2 text-center text-xs text-muted-foreground">
          Press Enter to generate · Shift+Enter for new line
        </p>
      </div>
    </div>
  )
}
