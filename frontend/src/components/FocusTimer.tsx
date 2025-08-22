'use client'

import React, { useState, useEffect, useRef } from 'react'
import { Play, Pause, Square, Timer, RotateCcw, Settings } from 'lucide-react'

interface FocusSession {
  id?: string
  session_type: string
  planned_duration: number
  actual_duration?: number
  started_at: Date
  ended_at?: Date
  completed: boolean
  interruptions: number
  focus_rating?: number
  productivity_rating?: number
}

interface FocusTimerProps {
  onSessionComplete?: (session: FocusSession) => void
}

export function FocusTimer({ onSessionComplete }: FocusTimerProps) {
  const [duration, setDuration] = useState(25) // Default 25 minutes
  const [timeLeft, setTimeLeft] = useState(duration * 60)
  const [isActive, setIsActive] = useState(false)
  const [isPaused, setIsPaused] = useState(false)
  const [sessionType, setSessionType] = useState<'pomodoro' | 'custom'>('pomodoro')
  const [interruptions, setInterruptions] = useState(0)
  const [currentSession, setCurrentSession] = useState<FocusSession | null>(null)
  const [showSettings, setShowSettings] = useState(false)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (isActive && !isPaused && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft(timeLeft => timeLeft - 1)
      }, 1000)
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [isActive, isPaused, timeLeft])

  useEffect(() => {
    if (timeLeft === 0 && isActive) {
      handleSessionComplete()
    }
  }, [timeLeft, isActive])

  const startSession = async () => {
    const session: FocusSession = {
      session_type: sessionType,
      planned_duration: duration,
      started_at: new Date(),
      completed: false,
      interruptions: 0
    }

    try {
      const token = localStorage.getItem('access_token')
      const response = await fetch('/api/v1/focus-sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(session)
      })

      if (response.ok) {
        const data = await response.json()
        session.id = data.id
      }
    } catch (error) {
      console.error('Error starting session:', error)
    }

    setCurrentSession(session)
    setTimeLeft(duration * 60)
    setIsActive(true)
    setIsPaused(false)
    setInterruptions(0)
  }

  const pauseSession = () => {
    setIsPaused(true)
    setInterruptions(prev => prev + 1)
  }

  const resumeSession = () => {
    setIsPaused(false)
  }

  const stopSession = () => {
    setIsActive(false)
    setIsPaused(false)
    
    if (currentSession) {
      const actualDuration = Math.round((duration * 60 - timeLeft) / 60)
      const updatedSession: FocusSession = {
        ...currentSession,
        actual_duration: actualDuration,
        ended_at: new Date(),
        completed: false,
        interruptions
      }
      
      if (onSessionComplete) {
        onSessionComplete(updatedSession)
      }
    }
    
    setCurrentSession(null)
    setTimeLeft(duration * 60)
    setInterruptions(0)
  }

  const handleSessionComplete = () => {
    setIsActive(false)
    setIsPaused(false)
    
    if (currentSession) {
      const completedSession: FocusSession = {
        ...currentSession,
        actual_duration: duration,
        ended_at: new Date(),
        completed: true,
        interruptions
      }
      
      if (onSessionComplete) {
        onSessionComplete(completedSession)
      }
    }
    
    setCurrentSession(null)
    setTimeLeft(duration * 60)
    setInterruptions(0)
  }

  const resetTimer = () => {
    setIsActive(false)
    setIsPaused(false)
    setTimeLeft(duration * 60)
    setCurrentSession(null)
    setInterruptions(0)
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const getProgressPercentage = () => {
    const totalSeconds = duration * 60
    const elapsed = totalSeconds - timeLeft
    return (elapsed / totalSeconds) * 100
  }

  const presetDurations = [
    { name: 'Pomodoro', minutes: 25, type: 'pomodoro' as const },
    { name: 'Short Break', minutes: 5, type: 'custom' as const },
    { name: 'Long Break', minutes: 15, type: 'custom' as const },
    { name: 'Deep Work', minutes: 90, type: 'custom' as const }
  ]

  return (
    <div className="w-full max-w-md mx-auto bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-2xl p-6 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-orange-500 to-red-500 shadow-lg">
            <Timer className="w-5 h-5 text-white" />
          </div>
          <h3 className="text-lg font-semibold text-white">Focus Timer</h3>
        </div>
        <button
          onClick={() => setShowSettings(!showSettings)}
          className="p-2 text-gray-400 hover:text-white transition-colors"
        >
          <Settings className="w-5 h-5" />
        </button>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="mb-6 p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
          <h4 className="text-white font-medium mb-3">Session Type</h4>
          <div className="grid grid-cols-2 gap-2 mb-4">
            {presetDurations.map((preset) => (
              <button
                key={preset.name}
                onClick={() => {
                  setDuration(preset.minutes)
                  setSessionType(preset.type)
                  setTimeLeft(preset.minutes * 60)
                }}
                className={`p-2 rounded-lg text-sm transition-all ${
                  duration === preset.minutes
                    ? 'bg-purple-600 text-white'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
              >
                {preset.name}
                <br />
                <span className="text-xs opacity-75">{preset.minutes}m</span>
              </button>
            ))}
          </div>
          
          <div className="flex items-center gap-2">
            <label className="text-white text-sm">Custom:</label>
            <input
              type="number"
              value={duration}
              onChange={(e) => {
                const newDuration = parseInt(e.target.value) || 1
                setDuration(newDuration)
                setTimeLeft(newDuration * 60)
                setSessionType('custom')
              }}
              className="w-16 px-2 py-1 bg-white/10 border border-white/20 rounded text-white text-sm"
              min="1"
              max="180"
              disabled={isActive}
            />
            <span className="text-gray-300 text-sm">minutes</span>
          </div>
        </div>
      )}

      {/* Timer Display */}
      <div className="text-center mb-6">
        <div className="relative w-48 h-48 mx-auto mb-4">
          {/* Background Circle */}
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="rgba(255,255,255,0.1)"
              strokeWidth="8"
              fill="none"
            />
            {/* Progress Circle */}
            <circle
              cx="50"
              cy="50"
              r="45"
              stroke="url(#progress-gradient)"
              strokeWidth="8"
              fill="none"
              strokeLinecap="round"
              strokeDasharray={`${2 * Math.PI * 45}`}
              strokeDashoffset={`${2 * Math.PI * 45 * (1 - getProgressPercentage() / 100)}`}
              className="transition-all duration-1000 ease-linear"
            />
            <defs>
              <linearGradient id="progress-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="#f59e0b" />
                <stop offset="100%" stopColor="#ef4444" />
              </linearGradient>
            </defs>
          </svg>
          
          {/* Time Display */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="text-3xl font-mono font-bold text-white mb-1">
                {formatTime(timeLeft)}
              </div>
              <div className="text-xs text-gray-400 uppercase tracking-wide">
                {sessionType === 'pomodoro' ? 'Pomodoro' : 'Focus'}
              </div>
            </div>
          </div>
        </div>

        {/* Session Info */}
        {currentSession && (
          <div className="mb-4 p-3 bg-white/5 rounded-lg">
            <div className="text-xs text-gray-400 mb-1">Current Session</div>
            <div className="text-sm text-white">
              Started: {currentSession.started_at.toLocaleTimeString()}
            </div>
            {interruptions > 0 && (
              <div className="text-xs text-orange-400">
                Interruptions: {interruptions}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-3 mb-4">
        {!isActive ? (
          <button
            onClick={startSession}
            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg"
          >
            <Play className="w-5 h-5" />
            Start
          </button>
        ) : (
          <>
            {!isPaused ? (
              <button
                onClick={pauseSession}
                className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-yellow-600 to-orange-600 text-white rounded-xl hover:from-yellow-700 hover:to-orange-700 transition-all shadow-lg"
              >
                <Pause className="w-5 h-5" />
                Pause
              </button>
            ) : (
              <button
                onClick={resumeSession}
                className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg"
              >
                <Play className="w-5 h-5" />
                Resume
              </button>
            )}
            
            <button
              onClick={stopSession}
              className="flex items-center gap-2 px-4 py-3 bg-gradient-to-r from-red-600 to-pink-600 text-white rounded-xl hover:from-red-700 hover:to-pink-700 transition-all shadow-lg"
            >
              <Square className="w-5 h-5" />
              Stop
            </button>
          </>
        )}
        
        <button
          onClick={resetTimer}
          disabled={isActive && !isPaused}
          className="flex items-center gap-2 px-4 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <RotateCcw className="w-5 h-5" />
          Reset
        </button>
      </div>

      {/* ADHD-Friendly Tips */}
      {!isActive && (
        <div className="p-3 bg-blue-500/20 border border-blue-500/30 rounded-lg">
          <div className="text-xs text-blue-300 font-medium mb-1">ADHD Tip</div>
          <div className="text-xs text-gray-300">
            Start with shorter sessions (15-20 min) and gradually increase. 
            It's okay to pause if you need to - progress over perfection!
          </div>
        </div>
      )}
    </div>
  )
}