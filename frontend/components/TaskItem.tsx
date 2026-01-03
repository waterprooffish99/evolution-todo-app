"use client";

import { useState } from "react";
import { taskApi } from "@/lib/api";

interface Task {
  id: number;
  title: string;
  description: string | null;
  completed: boolean;
  created_at: string;
  updated_at: string;
}

interface TaskItemProps {
  task: Task;
  userId: number;
  onTaskUpdated: () => void;
  onTaskDeleted: () => void;
}

export default function TaskItem({ task, userId, onTaskUpdated, onTaskDeleted }: TaskItemProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleToggle = async () => {
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      await taskApi.toggleComplete(userId, task.id);
      onTaskUpdated();
    } catch (err) {
      setError("Failed to update task. Please try again.");
      console.error("Error toggling task:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (loading) return;

    setLoading(true);
    setError(null);

    try {
      await taskApi.delete(userId, task.id);
      onTaskDeleted();
    } catch (err) {
      setError("Failed to delete task. Please try again.");
      console.error("Error deleting task:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <li className={`flex flex-col p-4 border rounded-md ${task.completed ? 'bg-green-50' : 'bg-white'}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <input
            type="checkbox"
            checked={task.completed}
            onChange={handleToggle}
            disabled={loading}
            className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 mt-1"
          />
          <div className="flex-1">
            <span className={`text-base ${task.completed ? 'line-through text-gray-500' : 'text-gray-900'}`}>
              {task.title}
            </span>
            {task.description && (
              <p className={`text-sm mt-1 ${task.completed ? 'line-through text-gray-400' : 'text-gray-600'}`}>
                {task.description}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleDelete}
            disabled={loading}
            className="text-red-600 hover:text-red-800 text-sm font-medium disabled:opacity-50"
          >
            Delete
          </button>
        </div>
      </div>

      {error && (
        <div className="text-red-600 text-sm mt-2">
          {error}
        </div>
      )}
    </li>
  );
}