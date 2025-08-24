'use client'

import React, { useState, useEffect } from 'react'
import { Plus, Check, Clock, AlertCircle, ChevronDown, ChevronRight, Trash2, Calendar, CalendarPlus, CalendarCheck } from 'lucide-react'

interface Task {
  id: string
  title: string
  description?: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high'
  category?: string
  is_broken_down: boolean
  breakdown_steps: string[]
  created_at: string
  completed_at?: string
  scheduled_start?: string
  scheduled_end?: string
}

interface TimeBlock {
  id?: string
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
  linked_task_id?: string
  google_calendar_sync_enabled: boolean
}

interface TaskManagerProps {
  onTaskUpdate?: (task: Task) => void
}

export function TaskManager({ onTaskUpdate }: TaskManagerProps) {
  const [tasks, setTasks] = useState<Task[]>([])
  const [newTaskTitle, setNewTaskTitle] = useState('')
  const [newTaskDescription, setNewTaskDescription] = useState('')
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high'>('medium')
  const [showAddForm, setShowAddForm] = useState(false)
  const [expandedTasks, setExpandedTasks] = useState<Set<string>>(new Set())
  const [filter, setFilter] = useState<'all' | 'pending' | 'in_progress' | 'completed'>('all')
  const [showScheduleModal, setShowScheduleModal] = useState<string | null>(null)
  const [linkedTimeBlocks, setLinkedTimeBlocks] = useState<{[taskId: string]: string}>({})

  useEffect(() => {
    fetchTasks()
    loadLinkedTimeBlocks()
  }, [])

  const loadLinkedTimeBlocks = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/calendar/time-blocks', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      
      if (response.ok) {
        const timeBlocks = await response.json()
        const linkMap: {[taskId: string]: string} = {}
        timeBlocks.forEach((block: any) => {
          if (block.linked_task_id) {
            linkMap[block.linked_task_id] = block.id
          }
        })
        setLinkedTimeBlocks(linkMap)
      }
    } catch (error) {
      console.error('Error loading linked time blocks:', error)
    }
  }

  const fetchTasks = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/tasks', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setTasks(data)
      }
    } catch (error) {
      console.error('Error fetching tasks:', error)
    }
  }

  const createTask = async () => {
    if (!newTaskTitle.trim()) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch('/api/v1/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: newTaskTitle,
          description: newTaskDescription || undefined,
          priority: newTaskPriority
        })
      })

      if (response.ok) {
        const newTask = await response.json()
        setTasks(prev => [newTask, ...prev])
        setNewTaskTitle('')
        setNewTaskDescription('')
        setNewTaskPriority('medium')
        setShowAddForm(false)
        
        if (onTaskUpdate) {
          onTaskUpdate(newTask)
        }
      }
    } catch (error) {
      console.error('Error creating task:', error)
    }
  }

  const updateTaskStatus = async (taskId: string, newStatus: Task['status']) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: newStatus })
      })

      if (response.ok) {
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, status: newStatus, completed_at: newStatus === 'completed' ? new Date().toISOString() : undefined }
            : task
        ))
      }
    } catch (error) {
      console.error('Error updating task:', error)
    }
  }

  const deleteTask = async (taskId: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/tasks/${taskId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })

      if (response.ok) {
        setTasks(prev => prev.filter(task => task.id !== taskId))
      }
    } catch (error) {
      console.error('Error deleting task:', error)
    }
  }

  const toggleTaskExpansion = (taskId: string) => {
    setExpandedTasks(prev => {
      const newSet = new Set(prev)
      if (newSet.has(taskId)) {
        newSet.delete(taskId)
      } else {
        newSet.add(taskId)
      }
      return newSet
    })
  }

  const scheduleTaskToCalendar = async (taskId: string, scheduleData: {
    start_time: string
    end_time: string
    location?: string
    block_type: string
    buffer_time_minutes: number
  }) => {
    try {
      const task = tasks.find(t => t.id === taskId)
      if (!task) return

      const token = localStorage.getItem('token')
      const timeBlockData: Partial<TimeBlock> = {
        title: task.title,
        description: task.description,
        location: scheduleData.location,
        start_time: scheduleData.start_time,
        end_time: scheduleData.end_time,
        all_day: false,
        block_type: scheduleData.block_type as any,
        color: getPriorityColorHex(task.priority),
        is_flexible: true, // Tasks are often flexible
        buffer_time_minutes: scheduleData.buffer_time_minutes,
        linked_task_id: taskId,
        google_calendar_sync_enabled: true
      }

      const response = await fetch('/api/v1/calendar/time-blocks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(timeBlockData)
      })

      if (response.ok) {
        const newTimeBlock = await response.json()
        setLinkedTimeBlocks(prev => ({ ...prev, [taskId]: newTimeBlock.id }))
        setShowScheduleModal(null)
        
        // Update task with schedule info
        await updateTaskSchedule(taskId, scheduleData.start_time, scheduleData.end_time)
      }
    } catch (error) {
      console.error('Error scheduling task to calendar:', error)
    }
  }

  const updateTaskSchedule = async (taskId: string, startTime: string, endTime: string) => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ 
          scheduled_start: startTime,
          scheduled_end: endTime 
        })
      })

      if (response.ok) {
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, scheduled_start: startTime, scheduled_end: endTime }
            : task
        ))
      }
    } catch (error) {
      console.error('Error updating task schedule:', error)
    }
  }

  const unlinkFromCalendar = async (taskId: string) => {
    try {
      const timeBlockId = linkedTimeBlocks[taskId]
      if (!timeBlockId) return

      const token = localStorage.getItem('token')
      const response = await fetch(`/api/v1/calendar/time-blocks/${timeBlockId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (response.ok) {
        setLinkedTimeBlocks(prev => {
          const newMap = { ...prev }
          delete newMap[taskId]
          return newMap
        })
        
        // Clear task schedule
        await updateTaskSchedule(taskId, '', '')
      }
    } catch (error) {
      console.error('Error unlinking from calendar:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'from-red-500 to-pink-500'
      case 'medium': return 'from-yellow-500 to-orange-500'
      case 'low': return 'from-green-500 to-emerald-500'
      default: return 'from-gray-500 to-slate-500'
    }
  }

  const getPriorityColorHex = (priority: string) => {
    switch (priority) {
      case 'high': return '#EF4444' // red-500
      case 'medium': return '#F59E0B' // yellow-500
      case 'low': return '#10B981' // emerald-500
      default: return '#6B7280' // gray-500
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <Check className="w-4 h-4 text-green-400" />
      case 'in_progress': return <Clock className="w-4 h-4 text-yellow-400" />
      default: return <AlertCircle className="w-4 h-4 text-gray-400" />
    }
  }

  const filteredTasks = tasks.filter(task => {
    if (filter === 'all') return true
    return task.status === filter
  })

  return (
    <div className="w-full max-w-2xl mx-auto bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-2xl p-6 shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-white">Task Manager</h3>
          <p className="text-sm text-gray-400">ADHD-friendly task breakdown</p>
        </div>
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg"
        >
          <Plus className="w-4 h-4" />
          Add Task
        </button>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {(['all', 'pending', 'in_progress', 'completed'] as const).map((status) => (
          <button
            key={status}
            onClick={() => setFilter(status)}
            className={`px-3 py-1 rounded-lg text-sm transition-all ${
              filter === status
                ? 'bg-purple-600 text-white'
                : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            {status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            <span className="ml-1 text-xs opacity-75">
              ({status === 'all' ? tasks.length : tasks.filter(t => t.status === status).length})
            </span>
          </button>
        ))}
      </div>

      {/* Add Task Form */}
      {showAddForm && (
        <div className="mb-6 p-4 bg-white/10 backdrop-blur-sm rounded-xl border border-white/20">
          <div className="space-y-3">
            <input
              type="text"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="What needs to be done?"
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            />
            
            <textarea
              value={newTaskDescription}
              onChange={(e) => setNewTaskDescription(e.target.value)}
              placeholder="Add details (optional)"
              rows={2}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/50"
            />
            
            <div className="flex items-center gap-3">
              <label className="text-white text-sm">Priority:</label>
              <select
                value={newTaskPriority}
                onChange={(e) => setNewTaskPriority(e.target.value as 'low' | 'medium' | 'high')}
                className="px-3 py-1 bg-white/10 border border-white/20 rounded-lg text-white text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            
            <div className="flex gap-2 pt-2">
              <button
                onClick={createTask}
                disabled={!newTaskTitle.trim()}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Task
              </button>
              <button
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tasks List */}
      <div className="space-y-3">
        {filteredTasks.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            {filter === 'all' ? 'No tasks yet' : `No ${filter.replace('_', ' ')} tasks`}
            <br />
            <span className="text-sm">
              {filter === 'all' && 'Add your first task to get started!'}
            </span>
          </div>
        ) : (
          filteredTasks.map((task) => (
            <div
              key={task.id}
              className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-4 hover:bg-white/10 transition-all"
            >
              <div className="flex items-start gap-3">
                {/* Status Icon */}
                <button
                  onClick={() => {
                    const nextStatus = task.status === 'pending' ? 'in_progress' 
                      : task.status === 'in_progress' ? 'completed' 
                      : 'pending'
                    updateTaskStatus(task.id, nextStatus)
                  }}
                  className="mt-1 p-1 rounded-full hover:bg-white/20 transition-colors"
                >
                  {getStatusIcon(task.status)}
                </button>

                {/* Task Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className={`font-medium ${task.status === 'completed' ? 'line-through text-gray-400' : 'text-white'}`}>
                      {task.title}
                    </h4>
                    <div className={`px-2 py-1 rounded-full bg-gradient-to-r ${getPriorityColor(task.priority)} text-white text-xs font-medium`}>
                      {task.priority}
                    </div>
                  </div>
                  
                  {task.description && (
                    <p className="text-sm text-gray-300 mb-2">{task.description}</p>
                  )}
                  
                  <div className="flex items-center gap-4 text-xs text-gray-400">
                    <span>Created: {new Date(task.created_at).toLocaleDateString()}</span>
                    {task.completed_at && (
                      <span>Completed: {new Date(task.completed_at).toLocaleDateString()}</span>
                    )}
                    {task.scheduled_start && (
                      <span className="text-blue-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {new Date(task.scheduled_start).toLocaleDateString()} {new Date(task.scheduled_start).toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}
                      </span>
                    )}
                    {task.is_broken_down && (
                      <span className="text-green-400">• Broken down</span>
                    )}
                  </div>

                  {/* Breakdown Steps */}
                  {task.breakdown_steps && task.breakdown_steps.length > 0 && (
                    <div className="mt-3">
                      <button
                        onClick={() => toggleTaskExpansion(task.id)}
                        className="flex items-center gap-1 text-sm text-purple-400 hover:text-purple-300 transition-colors"
                      >
                        {expandedTasks.has(task.id) ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
                        {task.breakdown_steps.length} breakdown steps
                      </button>
                      
                      {expandedTasks.has(task.id) && (
                        <ul className="mt-2 space-y-1">
                          {task.breakdown_steps.map((step, index) => (
                            <li key={index} className="flex items-center gap-2 text-sm text-gray-300">
                              <div className="w-1.5 h-1.5 bg-purple-400 rounded-full flex-shrink-0"></div>
                              {step}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-1">
                  {/* Calendar Integration Button */}
                  {linkedTimeBlocks[task.id] ? (
                    <button
                      onClick={() => unlinkFromCalendar(task.id)}
                      className="p-1 text-green-400 hover:text-yellow-400 transition-colors"
                      title="Remove from calendar"
                    >
                      <CalendarCheck className="w-4 h-4" />
                    </button>
                  ) : (
                    <button
                      onClick={() => setShowScheduleModal(task.id)}
                      className="p-1 text-gray-400 hover:text-blue-400 transition-colors"
                      title="Add to calendar"
                    >
                      <CalendarPlus className="w-4 h-4" />
                    </button>
                  )}
                  
                  <button
                    onClick={() => deleteTask(task.id)}
                    className="p-1 text-gray-400 hover:text-red-400 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Schedule Task Modal */}
      {showScheduleModal && (
        <ScheduleTaskModal
          taskId={showScheduleModal}
          taskTitle={tasks.find(t => t.id === showScheduleModal)?.title || ''}
          onClose={() => setShowScheduleModal(null)}
          onSchedule={scheduleTaskToCalendar}
        />
      )}

      {/* ADHD Tips */}
      <div className="mt-6 p-3 bg-blue-500/20 border border-blue-500/30 rounded-lg">
        <div className="text-xs text-blue-300 font-medium mb-1">ADHD Pro Tip</div>
        <div className="text-xs text-gray-300">
          Break large tasks into smaller steps of 15-30 minutes each. 
          Use the calendar button to schedule tasks at optimal times for your energy levels! 📅✨
        </div>
      </div>
    </div>
  )
}

// Schedule Task Modal Component
function ScheduleTaskModal({ 
  taskId, 
  taskTitle, 
  onClose, 
  onSchedule 
}: { 
  taskId: string
  taskTitle: string
  onClose: () => void
  onSchedule: (taskId: string, scheduleData: any) => void
}) {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)
  tomorrow.setHours(9, 0, 0, 0)

  const [scheduleData, setScheduleData] = useState({
    start_time: tomorrow.toISOString().slice(0, 16),
    end_time: new Date(tomorrow.getTime() + 60 * 60 * 1000).toISOString().slice(0, 16), // +1 hour
    location: '',
    block_type: 'work',
    buffer_time_minutes: 10
  })

  const blockTypes = [
    { value: 'work', label: 'Work Session', color: '#4A90E2' },
    { value: 'focus', label: 'Deep Focus', color: '#FF6B6B' },
    { value: 'personal', label: 'Personal Time', color: '#7B68EE' }
  ]

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSchedule(taskId, scheduleData)
  }

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 rounded-2xl p-6 w-full max-w-md mx-4 shadow-2xl border border-white/20">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-white">Schedule Task</h3>
            <p className="text-sm text-gray-400 truncate">{taskTitle}</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors text-xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-white mb-2">Start Time</label>
              <input
                type="datetime-local"
                value={scheduleData.start_time}
                onChange={(e) => setScheduleData({ ...scheduleData, start_time: e.target.value })}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-white mb-2">End Time</label>
              <input
                type="datetime-local"
                value={scheduleData.end_time}
                onChange={(e) => setScheduleData({ ...scheduleData, end_time: e.target.value })}
                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-purple-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">Location (Optional)</label>
            <input
              type="text"
              value={scheduleData.location}
              onChange={(e) => setScheduleData({ ...scheduleData, location: e.target.value })}
              className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-purple-500"
              placeholder="Where will you work on this?"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">Session Type</label>
            <div className="grid grid-cols-3 gap-2">
              {blockTypes.map(type => (
                <button
                  key={type.value}
                  type="button"
                  onClick={() => setScheduleData({ ...scheduleData, block_type: type.value })}
                  className={`p-2 rounded-lg text-xs transition-all ${
                    scheduleData.block_type === type.value
                      ? 'bg-purple-600 text-white'
                      : 'bg-white/10 text-gray-300 hover:bg-white/20'
                  }`}
                >
                  <div className="w-2 h-2 rounded-full mx-auto mb-1" style={{ backgroundColor: type.color }} />
                  {type.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-white mb-2">
              Buffer Time: {scheduleData.buffer_time_minutes} minutes
            </label>
            <input
              type="range"
              min="0"
              max="30"
              step="5"
              value={scheduleData.buffer_time_minutes}
              onChange={(e) => setScheduleData({ ...scheduleData, buffer_time_minutes: parseInt(e.target.value) })}
              className="w-full h-2 bg-white/20 rounded-lg appearance-none cursor-pointer"
            />
            <div className="text-xs text-gray-400 mt-1">
              Transition time between tasks (ADHD-friendly)
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
              className="flex-1 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg"
            >
              Schedule Task
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}