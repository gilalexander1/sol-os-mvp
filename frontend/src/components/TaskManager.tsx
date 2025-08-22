'use client'

import React, { useState, useEffect } from 'react'
import { Plus, Check, Clock, AlertCircle, ChevronDown, ChevronRight, Trash2 } from 'lucide-react'

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

  useEffect(() => {
    fetchTasks()
  }, [])

  const fetchTasks = async () => {
    try {
      const token = localStorage.getItem('access_token')
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
      const token = localStorage.getItem('access_token')
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
      const token = localStorage.getItem('access_token')
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
      const token = localStorage.getItem('access_token')
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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'from-red-500 to-pink-500'
      case 'medium': return 'from-yellow-500 to-orange-500'
      case 'low': return 'from-green-500 to-emerald-500'
      default: return 'from-gray-500 to-slate-500'
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

      {/* ADHD Tips */}
      <div className="mt-6 p-3 bg-blue-500/20 border border-blue-500/30 rounded-lg">
        <div className="text-xs text-blue-300 font-medium mb-1">ADHD Pro Tip</div>
        <div className="text-xs text-gray-300">
          Break large tasks into smaller steps of 15-30 minutes each. 
          Celebrate completing each step - progress is progress! 🎉
        </div>
      </div>
    </div>
  )
}