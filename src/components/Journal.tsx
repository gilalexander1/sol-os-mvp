'use client'

import React, { useState, useEffect } from 'react'
import { Plus, BookOpen, Heart, Brain, Zap, Frown, Smile, Star, Calendar, Edit, Trash2, ChevronLeft, ChevronRight, Save, X } from 'lucide-react'

interface JournalEntry {
  id: string
  title: string
  content: string
  mood_rating?: number        // 1-10
  energy_level?: number       // 1-10
  focus_level?: number        // 1-10
  anxiety_level?: number      // 1-10
  accomplishments?: string
  challenges?: string
  gratitude?: string
  tomorrow_focus?: string
  emotional_tags: string[]
  entry_date: string
  is_favorite: boolean
  created_at: string
  updated_at: string
}

const MOOD_EMOTIONS = [
  'happy', 'grateful', 'calm', 'excited', 'productive', 'focused',
  'anxious', 'overwhelmed', 'frustrated', 'tired', 'sad', 'stressed',
  'creative', 'motivated', 'peaceful', 'energetic'
]

const RATING_LABELS = {
  mood: ['Terrible', 'Very Bad', 'Bad', 'Poor', 'Below Average', 'Average', 'Good', 'Very Good', 'Great', 'Amazing'],
  energy: ['Exhausted', 'Very Low', 'Low', 'Below Average', 'Slightly Low', 'Average', 'Good', 'High', 'Very High', 'Energized'],
  focus: ['Cannot Focus', 'Very Scattered', 'Scattered', 'Unfocused', 'Slightly Unfocused', 'Average', 'Good', 'Very Focused', 'Laser Focused', 'In The Zone'],
  anxiety: ['Panic', 'Very High', 'High', 'Elevated', 'Moderate', 'Mild', 'Low', 'Very Low', 'Minimal', 'Calm']
}

export function Journal() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [selectedEntry, setSelectedEntry] = useState<JournalEntry | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    mood_rating: 5,
    energy_level: 5,
    focus_level: 5,
    anxiety_level: 5,
    accomplishments: '',
    challenges: '',
    gratitude: '',
    tomorrow_focus: '',
    emotional_tags: [] as string[],
    is_favorite: false
  })
  const [currentView, setCurrentView] = useState<'list' | 'entry' | 'create'>('list')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    loadEntries()
  }, [])

  const loadEntries = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/journal', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setEntries(data.entries)
      } else {
        console.error('Failed to load journal entries')
      }
    } catch (error) {
      console.error('Error loading journal entries:', error)
    } finally {
      setLoading(false)
    }
  }

  const createEntry = async () => {
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/journal', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        const newEntry = await response.json()
        setEntries([newEntry, ...entries])
        resetForm()
        setCurrentView('list')
        setIsCreating(false)
      } else {
        console.error('Failed to create journal entry')
      }
    } catch (error) {
      console.error('Error creating journal entry:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateEntry = async () => {
    if (!selectedEntry) return
    
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/journal/${selectedEntry.id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      })
      
      if (response.ok) {
        const updatedEntry = await response.json()
        setEntries(entries.map(e => e.id === selectedEntry.id ? updatedEntry : e))
        setSelectedEntry(updatedEntry)
        setIsEditing(false)
      } else {
        console.error('Failed to update journal entry')
      }
    } catch (error) {
      console.error('Error updating journal entry:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteEntry = async (entryId: string) => {
    if (!confirm('Are you sure you want to delete this journal entry?')) return
    
    try {
      setLoading(true)
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/journal/${entryId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        setEntries(entries.filter(e => e.id !== entryId))
        if (selectedEntry?.id === entryId) {
          setSelectedEntry(null)
          setCurrentView('list')
        }
      } else {
        console.error('Failed to delete journal entry')
      }
    } catch (error) {
      console.error('Error deleting journal entry:', error)
    } finally {
      setLoading(false)
    }
  }

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      mood_rating: 5,
      energy_level: 5,
      focus_level: 5,
      anxiety_level: 5,
      accomplishments: '',
      challenges: '',
      gratitude: '',
      tomorrow_focus: '',
      emotional_tags: [],
      is_favorite: false
    })
  }

  const startEdit = (entry: JournalEntry) => {
    setSelectedEntry(entry)
    setFormData({
      title: entry.title,
      content: entry.content,
      mood_rating: entry.mood_rating || 5,
      energy_level: entry.energy_level || 5,
      focus_level: entry.focus_level || 5,
      anxiety_level: entry.anxiety_level || 5,
      accomplishments: entry.accomplishments || '',
      challenges: entry.challenges || '',
      gratitude: entry.gratitude || '',
      tomorrow_focus: entry.tomorrow_focus || '',
      emotional_tags: entry.emotional_tags || [],
      is_favorite: entry.is_favorite
    })
    setIsEditing(true)
  }

  const toggleEmotionalTag = (tag: string) => {
    setFormData({
      ...formData,
      emotional_tags: formData.emotional_tags.includes(tag)
        ? formData.emotional_tags.filter(t => t !== tag)
        : [...formData.emotional_tags, tag]
    })
  }

  const getRatingColor = (value: number, type: 'mood' | 'energy' | 'focus' | 'anxiety') => {
    if (type === 'anxiety') {
      // For anxiety, lower is better
      if (value <= 3) return 'text-green-500'
      if (value <= 6) return 'text-yellow-500'
      return 'text-red-500'
    } else {
      // For mood, energy, focus, higher is better
      if (value <= 3) return 'text-red-500'
      if (value <= 6) return 'text-yellow-500'
      return 'text-green-500'
    }
  }

  const RatingSlider = ({ label, value, onChange, type }: {
    label: string
    value: number
    onChange: (value: number) => void
    type: keyof typeof RATING_LABELS
  }) => (
    <div className="mb-4">
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-300">{label}</label>
        <span className={`text-sm font-bold ${getRatingColor(value, type)}`}>
          {value}/10 - {RATING_LABELS[type][value - 1]}
        </span>
      </div>
      <input
        type="range"
        min="1"
        max="10"
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className="w-full h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
      />
    </div>
  )

  // Journal Entry List View
  if (currentView === 'list') {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-purple-400" />
            <h2 className="text-xl font-semibold text-white">Your Journal</h2>
          </div>
          <button
            onClick={() => {
              resetForm()
              setIsCreating(true)
              setCurrentView('create')
            }}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
          >
            <Plus className="w-4 h-4" />
            New Entry
          </button>
        </div>

        {/* Entries Grid */}
        {loading ? (
          <div className="text-center text-gray-400 py-8">Loading journal entries...</div>
        ) : entries.length === 0 ? (
          <div className="text-center py-12">
            <BookOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-400 mb-2">Start Your Journal Journey</h3>
            <p className="text-gray-500 mb-6">Capture your thoughts, track your mood, and celebrate your wins.</p>
            <button
              onClick={() => {
                resetForm()
                setIsCreating(true)
                setCurrentView('create')
              }}
              className="px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
            >
              Write Your First Entry
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {entries.map((entry) => (
              <div
                key={entry.id}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all cursor-pointer group"
                onClick={() => {
                  setSelectedEntry(entry)
                  setCurrentView('entry')
                }}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {entry.is_favorite && <Star className="w-4 h-4 text-yellow-400 fill-current" />}
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-400">
                      {new Date(entry.entry_date).toLocaleDateString()}
                    </span>
                  </div>
                </div>
                
                <h3 className="font-semibold text-white mb-2 line-clamp-2 group-hover:text-purple-400 transition-colors">
                  {entry.title}
                </h3>
                
                <p className="text-gray-400 text-sm mb-3 line-clamp-3">
                  {entry.content}
                </p>
                
                {/* Mood indicators */}
                <div className="flex gap-2 mb-3">
                  {entry.mood_rating && (
                    <div className="flex items-center gap-1">
                      <Smile className={`w-4 h-4 ${getRatingColor(entry.mood_rating, 'mood')}`} />
                      <span className={`text-xs ${getRatingColor(entry.mood_rating, 'mood')}`}>
                        {entry.mood_rating}
                      </span>
                    </div>
                  )}
                  {entry.energy_level && (
                    <div className="flex items-center gap-1">
                      <Zap className={`w-4 h-4 ${getRatingColor(entry.energy_level, 'energy')}`} />
                      <span className={`text-xs ${getRatingColor(entry.energy_level, 'energy')}`}>
                        {entry.energy_level}
                      </span>
                    </div>
                  )}
                  {entry.focus_level && (
                    <div className="flex items-center gap-1">
                      <Brain className={`w-4 h-4 ${getRatingColor(entry.focus_level, 'focus')}`} />
                      <span className={`text-xs ${getRatingColor(entry.focus_level, 'focus')}`}>
                        {entry.focus_level}
                      </span>
                    </div>
                  )}
                </div>
                
                {/* Emotional tags */}
                {entry.emotional_tags.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {entry.emotional_tags.slice(0, 3).map((tag) => (
                      <span key={tag} className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded">
                        {tag}
                      </span>
                    ))}
                    {entry.emotional_tags.length > 3 && (
                      <span className="px-2 py-1 bg-gray-600 text-gray-300 text-xs rounded">
                        +{entry.emotional_tags.length - 3}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  // Single Entry View
  if (currentView === 'entry' && selectedEntry && !isEditing) {
    return (
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentView('list')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            Back to Journal
          </button>
          <div className="flex gap-2">
            <button
              onClick={() => startEdit(selectedEntry)}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={() => deleteEntry(selectedEntry.id)}
              className="flex items-center gap-2 px-3 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>

        {/* Entry Content */}
        <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
          <div className="flex items-center gap-3 mb-4">
            {selectedEntry.is_favorite && <Star className="w-5 h-5 text-yellow-400 fill-current" />}
            <span className="text-gray-400">
              {new Date(selectedEntry.entry_date).toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </span>
          </div>
          
          <h1 className="text-2xl font-bold text-white mb-6">{selectedEntry.title}</h1>
          
          {/* Ratings */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            {selectedEntry.mood_rating && (
              <div className="text-center">
                <Smile className={`w-6 h-6 mx-auto mb-2 ${getRatingColor(selectedEntry.mood_rating, 'mood')}`} />
                <div className="text-sm text-gray-400">Mood</div>
                <div className={`font-bold ${getRatingColor(selectedEntry.mood_rating, 'mood')}`}>
                  {selectedEntry.mood_rating}/10
                </div>
              </div>
            )}
            {selectedEntry.energy_level && (
              <div className="text-center">
                <Zap className={`w-6 h-6 mx-auto mb-2 ${getRatingColor(selectedEntry.energy_level, 'energy')}`} />
                <div className="text-sm text-gray-400">Energy</div>
                <div className={`font-bold ${getRatingColor(selectedEntry.energy_level, 'energy')}`}>
                  {selectedEntry.energy_level}/10
                </div>
              </div>
            )}
            {selectedEntry.focus_level && (
              <div className="text-center">
                <Brain className={`w-6 h-6 mx-auto mb-2 ${getRatingColor(selectedEntry.focus_level, 'focus')}`} />
                <div className="text-sm text-gray-400">Focus</div>
                <div className={`font-bold ${getRatingColor(selectedEntry.focus_level, 'focus')}`}>
                  {selectedEntry.focus_level}/10
                </div>
              </div>
            )}
            {selectedEntry.anxiety_level && (
              <div className="text-center">
                <Frown className={`w-6 h-6 mx-auto mb-2 ${getRatingColor(selectedEntry.anxiety_level, 'anxiety')}`} />
                <div className="text-sm text-gray-400">Anxiety</div>
                <div className={`font-bold ${getRatingColor(selectedEntry.anxiety_level, 'anxiety')}`}>
                  {selectedEntry.anxiety_level}/10
                </div>
              </div>
            )}
          </div>

          {/* Main Content */}
          <div className="prose prose-invert max-w-none mb-6">
            <div className="whitespace-pre-wrap text-gray-300">{selectedEntry.content}</div>
          </div>

          {/* Structured Sections */}
          <div className="space-y-4">
            {selectedEntry.accomplishments && (
              <div>
                <h3 className="font-semibold text-green-400 mb-2">🎉 Today's Wins</h3>
                <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3 text-green-300">
                  {selectedEntry.accomplishments}
                </div>
              </div>
            )}
            
            {selectedEntry.challenges && (
              <div>
                <h3 className="font-semibold text-orange-400 mb-2">🤔 Challenges</h3>
                <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 text-orange-300">
                  {selectedEntry.challenges}
                </div>
              </div>
            )}
            
            {selectedEntry.gratitude && (
              <div>
                <h3 className="font-semibold text-pink-400 mb-2">❤️ Grateful For</h3>
                <div className="bg-pink-500/10 border border-pink-500/20 rounded-lg p-3 text-pink-300">
                  {selectedEntry.gratitude}
                </div>
              </div>
            )}
            
            {selectedEntry.tomorrow_focus && (
              <div>
                <h3 className="font-semibold text-blue-400 mb-2">🎯 Tomorrow's Focus</h3>
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-blue-300">
                  {selectedEntry.tomorrow_focus}
                </div>
              </div>
            )}
          </div>

          {/* Emotional Tags */}
          {selectedEntry.emotional_tags.length > 0 && (
            <div className="mt-6">
              <h3 className="font-semibold text-gray-300 mb-3">How I felt</h3>
              <div className="flex flex-wrap gap-2">
                {selectedEntry.emotional_tags.map((tag) => (
                  <span key={tag} className="px-3 py-1 bg-purple-500/20 border border-purple-500/30 text-purple-300 rounded-full text-sm">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  // Create/Edit Form View
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => {
            if (isEditing) {
              setIsEditing(false)
              setCurrentView('entry')
            } else {
              setCurrentView('list')
              setIsCreating(false)
            }
          }}
          className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
        >
          <ChevronLeft className="w-4 h-4" />
          {isEditing ? 'Back to Entry' : 'Back to Journal'}
        </button>
        <div className="flex gap-2">
          <button
            onClick={isEditing ? updateEntry : createEntry}
            disabled={loading || !formData.title.trim() || !formData.content.trim()}
            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Save className="w-4 h-4" />
            {loading ? 'Saving...' : isEditing ? 'Update Entry' : 'Save Entry'}
          </button>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6">
        <div className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Entry Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              placeholder="How was your day?"
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              required
            />
          </div>

          {/* Main Content */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Your Thoughts *
            </label>
            <textarea
              value={formData.content}
              onChange={(e) => setFormData({ ...formData, content: e.target.value })}
              placeholder="What's on your mind today? How are you feeling? What happened?"
              rows={6}
              className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 resize-none"
              required
            />
          </div>

          {/* Mood Ratings */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-white mb-4">How are you feeling?</h3>
              <RatingSlider
                label="Mood"
                value={formData.mood_rating}
                onChange={(value) => setFormData({ ...formData, mood_rating: value })}
                type="mood"
              />
              <RatingSlider
                label="Energy Level"
                value={formData.energy_level}
                onChange={(value) => setFormData({ ...formData, energy_level: value })}
                type="energy"
              />
            </div>
            <div className="space-y-4">
              <h3 className="font-semibold text-white mb-4">Mental State</h3>
              <RatingSlider
                label="Focus Level"
                value={formData.focus_level}
                onChange={(value) => setFormData({ ...formData, focus_level: value })}
                type="focus"
              />
              <RatingSlider
                label="Anxiety Level"
                value={formData.anxiety_level}
                onChange={(value) => setFormData({ ...formData, anxiety_level: value })}
                type="anxiety"
              />
            </div>
          </div>

          {/* Emotional Tags */}
          <div>
            <h3 className="font-semibold text-white mb-3">Emotional Tags</h3>
            <p className="text-sm text-gray-400 mb-4">Select emotions that describe your day</p>
            <div className="flex flex-wrap gap-2">
              {MOOD_EMOTIONS.map((emotion) => (
                <button
                  key={emotion}
                  type="button"
                  onClick={() => toggleEmotionalTag(emotion)}
                  className={`px-3 py-1 rounded-full text-sm transition-all ${
                    formData.emotional_tags.includes(emotion)
                      ? 'bg-purple-500 text-white border border-purple-400'
                      : 'bg-white/5 text-gray-300 border border-white/10 hover:bg-white/10'
                  }`}
                >
                  {emotion}
                </button>
              ))}
            </div>
          </div>

          {/* Structured Prompts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-green-400 mb-2">
                  🎉 Today's Wins & Accomplishments
                </label>
                <textarea
                  value={formData.accomplishments}
                  onChange={(e) => setFormData({ ...formData, accomplishments: e.target.value })}
                  placeholder="What went well today? What are you proud of?"
                  rows={3}
                  className="w-full px-3 py-2 bg-green-500/10 border border-green-500/20 rounded-lg text-green-300 placeholder-green-400/70 focus:outline-none focus:border-green-500 resize-none"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-pink-400 mb-2">
                  ❤️ What I'm Grateful For
                </label>
                <textarea
                  value={formData.gratitude}
                  onChange={(e) => setFormData({ ...formData, gratitude: e.target.value })}
                  placeholder="Three things you're grateful for today..."
                  rows={3}
                  className="w-full px-3 py-2 bg-pink-500/10 border border-pink-500/20 rounded-lg text-pink-300 placeholder-pink-400/70 focus:outline-none focus:border-pink-500 resize-none"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-orange-400 mb-2">
                  🤔 Challenges & Struggles
                </label>
                <textarea
                  value={formData.challenges}
                  onChange={(e) => setFormData({ ...formData, challenges: e.target.value })}
                  placeholder="What was difficult? What can you learn from it?"
                  rows={3}
                  className="w-full px-3 py-2 bg-orange-500/10 border border-orange-500/20 rounded-lg text-orange-300 placeholder-orange-400/70 focus:outline-none focus:border-orange-500 resize-none"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-blue-400 mb-2">
                  🎯 Tomorrow's Main Focus
                </label>
                <textarea
                  value={formData.tomorrow_focus}
                  onChange={(e) => setFormData({ ...formData, tomorrow_focus: e.target.value })}
                  placeholder="What's one thing you want to focus on tomorrow?"
                  rows={3}
                  className="w-full px-3 py-2 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-300 placeholder-blue-400/70 focus:outline-none focus:border-blue-500 resize-none"
                />
              </div>
            </div>
          </div>

          {/* Favorite Toggle */}
          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_favorite"
              checked={formData.is_favorite}
              onChange={(e) => setFormData({ ...formData, is_favorite: e.target.checked })}
              className="w-4 h-4 text-yellow-400 bg-white/5 border border-white/10 rounded focus:ring-yellow-500 focus:ring-2"
            />
            <label htmlFor="is_favorite" className="flex items-center gap-2 text-gray-300">
              <Star className="w-4 h-4" />
              Mark as favorite
            </label>
          </div>
        </div>
      </div>
    </div>
  )
}