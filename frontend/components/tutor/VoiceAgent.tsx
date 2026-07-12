'use client'

import { useState } from 'react'
import {
  LiveKitRoom,
  BarVisualizer,
  RoomAudioRenderer,
  useVoiceAssistant,
  useTrackToggle,
  type AgentState,
} from '@livekit/components-react'
import { Track } from 'livekit-client'
import { Mic, MicOff, Phone, PhoneOff, Loader2 } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'

type ConnectState = 'idle' | 'connecting' | 'connected'

const STATUS_LABEL: Partial<Record<AgentState, string>> = {
  connecting: 'Connecting...',
  'pre-connect-buffering': 'Getting ready...',
  initializing: 'Initializing...',
  idle: 'Ready',
  listening: 'Listening...',
  thinking: 'Thinking...',
  speaking: 'Speaking...',
  disconnected: 'Disconnected',
  failed: 'Failed to connect',
}

export default function VoiceAgent() {
  const [connectState, setConnectState] = useState<ConnectState>('idle')
  const [token, setToken] = useState('')
  const [serverUrl, setServerUrl] = useState('')
  const [fetchError, setFetchError] = useState('')

  async function connect() {
    setFetchError('')
    setConnectState('connecting')
    try {
      const res = await fetch(`${API_URL}/api/voice/token`)
      if (!res.ok) throw new Error(`Token fetch failed: ${res.status}`)
      const data = await res.json()
      setToken(data.token)
      setServerUrl(data.url)
      setConnectState('connected')
    } catch (err) {
      setFetchError(err instanceof Error ? err.message : 'Could not connect')
      setConnectState('idle')
    }
  }

  function disconnect() {
    setToken('')
    setServerUrl('')
    setConnectState('idle')
  }

  if (connectState !== 'connected') {
    return (
      <div className="flex h-full flex-col items-center justify-center gap-8">
        <div className="flex flex-col items-center gap-2 text-center">
          <p className="text-2xl font-semibold text-foreground">Voice Tutor</p>
          <p className="max-w-xs text-sm text-muted-foreground">
            Ask any questions related to curriculum topics and concepts
          </p>
        </div>

        <button
          onClick={connect}
          disabled={connectState === 'connecting'}
          className="flex h-20 w-20 items-center justify-center rounded-full bg-primary text-primary-foreground shadow-lg transition-opacity hover:opacity-90 disabled:opacity-60"
        >
          {connectState === 'connecting' ? (
            <Loader2 size={32} className="animate-spin" />
          ) : (
            <Phone size={32} />
          )}
        </button>

        {fetchError && (
          <p className="text-sm text-destructive">{fetchError}</p>
        )}
      </div>
    )
  }

  return (
    <LiveKitRoom
      token={token}
      serverUrl={serverUrl}
      connect={true}
      audio={true}
      video={false}
      onDisconnected={disconnect}
      className="flex h-full flex-col items-center justify-center"
    >
      <TutorSession onDisconnect={disconnect} />
      <RoomAudioRenderer />
    </LiveKitRoom>
  )
}

function TutorSession({ onDisconnect }: { onDisconnect: () => void }) {
  const { state, audioTrack, agentTranscriptions } = useVoiceAssistant()
  const { buttonProps, enabled } = useTrackToggle({ source: Track.Source.Microphone })

  const latestTranscript = agentTranscriptions.at(-1)?.text ?? ''

  return (
    <div className="flex flex-col items-center gap-8">
      {/* Agent audio visualizer */}
      <div className="lk-visualizer-container h-28 w-72">
        <BarVisualizer
          state={state}
          track={audioTrack}
          className="h-full w-full"
        />
      </div>

      {/* Latest agent transcript */}
      <p
        className={`max-w-sm text-center text-lg font-semibold text-foreground drop-shadow-md transition-all duration-300 ease-in-out ${
          latestTranscript ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-1 select-none'
        }`}
      >
        {latestTranscript ? <>&ldquo;{latestTranscript}&rdquo;</> : ' '}
      </p>

      {/* Agent state label */}
      <p className="text-sm text-muted-foreground">
        {STATUS_LABEL[state] ?? state}
      </p>

      {/* Mic + disconnect controls */}
      <div className="flex items-center gap-5">
        <button
          {...buttonProps}
          className={`flex h-16 w-16 items-center justify-center rounded-full transition-colors ${
            enabled
              ? 'bg-primary text-primary-foreground hover:opacity-90'
              : 'bg-muted text-muted-foreground hover:bg-muted/70'
          }`}
        >
          {enabled ? <Mic size={24} /> : <MicOff size={24} />}
        </button>

        <button
          onClick={onDisconnect}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-destructive text-destructive-foreground transition-opacity hover:opacity-90"
        >
          <PhoneOff size={20} />
        </button>
      </div>

      <p className="max-w-xs text-center text-xs text-muted-foreground">
        Ask any questions related to curriculum topics and concepts
      </p>
    </div>
  )
}
