'use client'

import React, { useState, useEffect } from 'react'
import { 
  Calendar as CalendarIcon, 
  Plus, 
  Clock, 
  MapPin, 
  Edit3, 
  Trash2, 
  Sync, 
  AlertCircle,
  CheckCircle,
  ExternalLink,
  Settings,
  ChevronLeft,
  ChevronRight,
  Google
} from 'lucide-react'

interface TimeBlock {
  id: string
  title: string
  description?: string
  location?: string
  start_time: string
  end_time: string
  all_day: boolean
  block_type: 'work' | 'personal' | 'rest' | 'focus' | 'external'
  color: string
  is_flexible: boolean
  buffer_time_minutes: number
  google_calendar_event_id?: string
  google_calendar_sync_enabled: boolean
  sync_status: 'pending' | 'synced' | 'error' | 'disconnected'
  sync_error?: string
  last_synced_at?: string
  created_at: string
  updated_at: string
}

interface CalendarSyncStatus {
  connected: boolean
  sync_enabled: boolean
  last_sync?: string
}

interface CalendarViewProps {
  onTimeBlockSelect?: (timeBlock: TimeBlock) => void
}

export function CalendarView({ onTimeBlockSelect }: CalendarViewProps) {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [timeBlocks, setTimeBlocks] = useState<TimeBlock[]>([])
  const [syncStatus, setSyncStatus] = useState<CalendarSyncStatus>({ connected: false, sync_enabled: false })
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedTimeBlock, setSelectedTimeBlock] = useState<TimeBlock | null>(null)
  const [viewMode, setViewMode] = useState<'week' | 'month'>('week')
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    loadTimeBlocks()
    loadSyncStatus()
  }, [currentDate])

  const loadTimeBlocks = async () => {
    try {
      const token = localStorage.getItem('token')
      const startDate = getWeekStart(currentDate)
      const endDate = getWeekEnd(currentDate)
      
      const response = await fetch(`/api/v1/calendar/time-blocks?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setTimeBlocks(data)
      }
    } catch (error) {
      console.error('Error loading time blocks:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadSyncStatus = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/calendar/status', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        setSyncStatus(data)
      }
    } catch (error) {
      console.error('Error loading sync status:', error)
    }
  }

  const connectGoogleCalendar = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/calendar/connect', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const data = await response.json()
        window.open(data.auth_url, '_blank', 'width=500,height=600')
        
        // Poll for connection status
        const pollInterval = setInterval(async () => {
          await loadSyncStatus()
          if (syncStatus.connected) {
            clearInterval(pollInterval)
            await syncFromGoogle()
          }
        }, 2000)
      }
    } catch (error) {
      console.error('Error connecting Google Calendar:', error)
    }
  }

  const syncFromGoogle = async () => {
    if (!syncStatus.connected) return
    
    setSyncing(true)
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/calendar/sync/from-google', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        await loadTimeBlocks()
        await loadSyncStatus()
      }
    } catch (error) {
      console.error('Error syncing from Google:', error)
    } finally {
      setSyncing(false)
    }
  }

  const createTimeBlock = async (timeBlockData: Partial<TimeBlock>) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/calendar/time-blocks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(timeBlockData)
      })
      
      if (response.ok) {
        await loadTimeBlocks()
        setShowCreateModal(false)
      }
    } catch (error) {
      console.error('Error creating time block:', error)
    }
  }

  const deleteTimeBlock = async (id: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/calendar/time-blocks/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        await loadTimeBlocks()
        setSelectedTimeBlock(null)
      }
    } catch (error) {
      console.error('Error deleting time block:', error)
    }
  }

  const getWeekStart = (date: Date) => {
    const start = new Date(date)
    const day = start.getDay()
    const diff = start.getDate() - day
    return new Date(start.setDate(diff))
  }

  const getWeekEnd = (date: Date) => {
    const end = new Date(date)
    const day = end.getDay()
    const diff = end.getDate() - day + 6
    return new Date(end.setDate(diff))
  }

  const getWeekDays = (date: Date) => {
    const start = getWeekStart(date)
    const days = []
    for (let i = 0; i < 7; i++) {
      const day = new Date(start)
      day.setDate(start.getDate() + i)
      days.push(day)
    }
    return days
  }

  const getTimeBlocksForDay = (date: Date) => {
    const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate())
    const dayEnd = new Date(date.getFullYear(), date.getMonth(), date.getDate() + 1)
    
    return timeBlocks.filter(block => {
      const blockStart = new Date(block.start_time)
      return blockStart >= dayStart && blockStart < dayEnd
    }).sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
  }

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
  }

  const getBlockTypeColor = (type: string) => {
    const colors = {
      work: '#4A90E2',
      personal: '#7B68EE',
      rest: '#50C878',
      focus: '#FF6B6B',
      external: '#34D399'
    }
    return colors[type as keyof typeof colors] || '#4A90E2'
  }

  const getSyncStatusIcon = (status: string) => {
    switch (status) {
      case 'synced':
        return <CheckCircle className="w-3 h-3 text-green-400" />
      case 'pending':
        return <Clock className="w-3 h-3 text-yellow-400" />
      case 'error':
        return <AlertCircle className="w-3 h-3 text-red-400" />
      default:
        return null
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-gray-400">
          <CalendarIcon className="w-16 h-16 mx-auto mb-4 opacity-50 animate-pulse" />
          <p>Loading calendar...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-2xl p-6 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 shadow-lg">
            <CalendarIcon className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-xl font-semibold text-white">Calendar</h2>
        </div>
        
        <div className="flex items-center gap-2">
          {/* Google Calendar Status */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-lg bg-white/10 backdrop-blur-sm border border-white/20">
            <Google className="w-4 h-4 text-white" />
            <span className={`text-xs ${syncStatus.connected ? 'text-green-400' : 'text-gray-400'}`}>
              {syncStatus.connected ? 'Connected' : 'Disconnected'}
            </span>
            {syncStatus.connected && (
              <button
                onClick={syncFromGoogle}
                disabled={syncing}
                className="text-xs text-blue-400 hover:text-blue-300 transition-colors disabled:opacity-50"
              >
                <Sync className={`w-3 h-3 ${syncing ? 'animate-spin' : ''}`} />
              </button>
            )}
          </div>
          
          {/* Connect/Create buttons */}
          {!syncStatus.connected ? (
            <button
              onClick={connectGoogleCalendar}
              className="px-3 py-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white text-xs rounded-lg hover:from-green-700 hover:to-emerald-700 transition-all shadow-lg"
            >
              Connect Google
            </button>
          ) : (
            <button
              onClick={() => setShowCreateModal(true)}
              className="p-2 text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              <Plus className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      {/* Calendar Navigation */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setCurrentDate(new Date(currentDate.setDate(currentDate.getDate() - 7)))}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
          <h3 className="text-lg font-medium text-white min-w-[200px] text-center">
            {currentDate.toLocaleDateString('en-US', { 
              month: 'long', 
              year: 'numeric',
              day: 'numeric'
            })}
          </h3>
          <button
            onClick={() => setCurrentDate(new Date(currentDate.setDate(currentDate.getDate() + 7)))}
            className="p-2 text-gray-400 hover:text-white transition-colors"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </div>
        
        <button
          onClick={() => setCurrentDate(new Date())}
          className="px-3 py-1 text-xs text-purple-400 hover:text-purple-300 border border-purple-400/30 rounded-lg transition-colors"
        >
          Today
        </button>
      </div>

      {/* Week View */}
      <div className="flex-1 overflow-auto">
        <div className="grid grid-cols-7 gap-1 mb-2">
          {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
            <div key={day} className="p-2 text-center text-xs font-medium text-gray-400 uppercase">
              {day}
            </div>
          ))}
        </div>
        
        <div className="grid grid-cols-7 gap-1 h-full">
          {getWeekDays(currentDate).map((day, index) => {
            const dayBlocks = getTimeBlocksForDay(day)
            const isToday = day.toDateString() === new Date().toDateString()
            
            return (
              <div
                key={index}
                className={`min-h-[200px] p-2 rounded-lg border transition-all ${
                  isToday
                    ? 'bg-purple-500/10 border-purple-500/30'
                    : 'bg-white/5 border-white/10 hover:bg-white/10'
                }`}
              >
                <div className={`text-sm font-medium mb-2 ${
                  isToday ? 'text-purple-400' : 'text-white'
                }`}>
                  {day.getDate()}
                </div>
                
                <div className="space-y-1">
                  {dayBlocks.map(block => (
                    <div
                      key={block.id}
                      onClick={() => setSelectedTimeBlock(block)}
                      className="p-2 rounded-lg cursor-pointer transition-all hover:scale-105 shadow-sm"
                      style={{ 
                        backgroundColor: block.color + '40',
                        borderLeft: `3px solid ${block.color}`
                      }}
                    >
                      <div className="flex items-start justify-between gap-1 mb-1">
                        <div className="text-xs font-medium text-white truncate">
                          {block.title}
                        </div>
                        <div className="flex items-center gap-1 flex-shrink-0">
                          {block.google_calendar_event_id && getSyncStatusIcon(block.sync_status)}
                          {block.google_calendar_event_id && (
                            <ExternalLink className="w-2 h-2 text-gray-400" />
                          )}
                        </div>
                      </div>
                      
                      <div className="text-xs text-gray-300 mb-1">
                        {block.all_day ? 'All Day' : `${formatTime(block.start_time)} - ${formatTime(block.end_time)}`}
                      </div>
                      
                      {block.location && (
                        <div className="flex items-center gap-1 text-xs text-gray-400">
                          <MapPin className="w-2 h-2" />
                          <span className="truncate">{block.location}</span>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
                
                {dayBlocks.length === 0 && (
                  <div
                    onClick={() => setShowCreateModal(true)}
                    className="h-8 flex items-center justify-center text-xs text-gray-500 hover:text-gray-400 cursor-pointer rounded-lg hover:bg-white/5 transition-all"
                  >
                    <Plus className="w-3 h-3" />
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Time Block Detail Modal */}
      {selectedTimeBlock && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl border border-white/20">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-white mb-1">{selectedTimeBlock.title}</h3>
                <div className="flex items-center gap-2 text-sm text-gray-300">
                  <Clock className="w-4 h-4" />
                  {selectedTimeBlock.all_day 
                    ? 'All Day' 
                    : `${formatTime(selectedTimeBlock.start_time)} - ${formatTime(selectedTimeBlock.end_time)}`
                  }
                </div>
              </div>
              <button
                onClick={() => setSelectedTimeBlock(null)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ×
              </button>
            </div>
            
            {selectedTimeBlock.description && (
              <p className="text-gray-300 text-sm mb-4">{selectedTimeBlock.description}</p>
            )}
            
            {selectedTimeBlock.location && (
              <div className="flex items-center gap-2 text-sm text-gray-300 mb-4">
                <MapPin className="w-4 h-4" />
                {selectedTimeBlock.location}
              </div>
            )}
            
            <div className="flex items-center gap-2 text-sm text-gray-400 mb-4">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: selectedTimeBlock.color }}
              />
              <span className="capitalize">{selectedTimeBlock.block_type}</span>
              {selectedTimeBlock.google_calendar_event_id && (
                <>
                  <span>•</span>
                  <div className="flex items-center gap-1">
                    {getSyncStatusIcon(selectedTimeBlock.sync_status)}
                    <span className="text-xs">
                      {selectedTimeBlock.sync_status === 'synced' && 'Synced with Google'}
                      {selectedTimeBlock.sync_status === 'pending' && 'Sync pending'}
                      {selectedTimeBlock.sync_status === 'error' && 'Sync failed'}
                    </span>
                  </div>
                </>
              )}
            </div>
            
            <div className="flex gap-2">
              <button
                onClick={() => {
                  // TODO: Implement edit functionality
                  setSelectedTimeBlock(null)
                }}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
              >
                <Edit3 className="w-4 h-4" />
                Edit
              </button>
              <button
                onClick={() => deleteTimeBlock(selectedTimeBlock.id)}
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Time Block Modal */}
      {showCreateModal && (
        <CreateTimeBlockModal
          onClose={() => setShowCreateModal(false)}
          onCreate={createTimeBlock}
          defaultDate={currentDate}
        />
      )}
    </div>
  )
}

// Create Time Block Modal Component
function CreateTimeBlockModal({ 
  onClose, 
  onCreate, 
  defaultDate 
}: { 
  onClose: () => void
  onCreate: (data: Partial<TimeBlock>) => void
  defaultDate: Date 
}) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    location: '',
    start_time: new Date(defaultDate.getFullYear(), defaultDate.getMonth(), defaultDate.getDate(), 9, 0).toISOString().slice(0, 16),
    end_time: new Date(defaultDate.getFullYear(), defaultDate.getMonth(), defaultDate.getDate(), 10, 0).toISOString().slice(0, 16),
    all_day: false,
    block_type: 'work' as const,
    color: '#4A90E2',
    is_flexible: false,
    buffer_time_minutes: 10
  })

  const blockTypes = [
    { value: 'work', label: 'Work', color: '#4A90E2' },
    { value: 'personal', label: 'Personal', color: '#7B68EE' },
    { value: 'rest', label: 'Rest', color: '#50C878' },
    { value: 'focus', label: 'Focus', color: '#FF6B6B' }
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onCreate(formData)
  }

  const handleTypeChange = (type: string) => {
    const selectedType = blockTypes.find(t => t.value === type)
    setFormData({ 
      ...formData, 
      block_type: type as any,
      color: selectedType?.color || '#4A90E2'
    })
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-2xl p-6 w-full max-w-lg mx-4 shadow-2xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-white">Create Time Block</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ×
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-white mb-2">Title *</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              placeholder="Enter event title"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500 resize-none"
              rows={2}
              placeholder="Optional description"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">Location</label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              placeholder="Optional location"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-white mb-2">Start Time</label>
              <input
                type="datetime-local"
                value={formData.start_time}
                onChange={(e) => setFormData({ ...formData, start_time: e.target.value })}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500"
                disabled={formData.all_day}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white mb-2">End Time</label>
              <input
                type="datetime-local"
                value={formData.end_time}
                onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500"
                disabled={formData.all_day}
              />
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-white cursor-pointer">
              <input
                type="checkbox"
                checked={formData.all_day}
                onChange={(e) => setFormData({ ...formData, all_day: e.target.checked })}
                className="rounded border-white/20 bg-white/10 text-purple-600 focus:ring-purple-500"
              />
              All Day Event
            </label>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white mb-2">Type</label>
            <div className="grid grid-cols-2 gap-2">
              {blockTypes.map(type => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => handleTypeChange(type.value)}
                  className={`p-2 rounded-lg text-sm transition-all flex items-center gap-2 ${
                    formData.block_type === type.value
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/10 text-gray-300 hover:bg-white/20'
                  }`}
                >
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: type.color }} />
                  {type.label}
                </button>
              ))}
            </div>
          </div>
          
          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}