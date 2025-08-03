"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { api } from "@/services/api";
import { useToast } from "@/hooks/useToast";
import {
  CheckCircle,
  Circle,
  Clock,
  AlertCircle,
  Sparkles,
  Loader2,
  RefreshCw,
} from "lucide-react";

interface Task {
  task: string;
  priority: string;
  status: string;
}

interface TaskListProps {
  answer?: string;
  query?: string;
  queryId?: string;
  onTasksGenerated?: (tasks: Task[]) => void;
}

export function TaskList({
  answer,
  query,
  queryId,
  onTasksGenerated,
}: TaskListProps) {
  const { toast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [hasGenerated, setHasGenerated] = useState(false);

  const generateTasks = async () => {
    if (!answer && !query) {
      toast({
        title: "No content available",
        description: "Please provide an answer or query to generate tasks from",
        variant: "destructive",
      });
      return;
    }

    setIsGenerating(true);
    try {
      const result = await api.generateTasks(answer, query);
      setTasks(result.tasks);
      setHasGenerated(true);
      onTasksGenerated?.(result.tasks);

      toast({
        title: "Tasks generated",
        description: `Generated ${result.total_tasks} actionable tasks`,
      });
    } catch (error: any) {
      console.error("Task generation error:", error);
      toast({
        title: "Task generation failed",
        description: error.response?.data?.detail || "Failed to generate tasks",
        variant: "destructive",
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority.toLowerCase()) {
      case "high":
        return "bg-red-100 text-red-800";
      case "medium":
        return "bg-yellow-100 text-yellow-800";
      case "low":
        return "bg-green-100 text-green-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "in_progress":
        return <Clock className="h-4 w-4 text-blue-500" />;
      case "pending":
        return <Circle className="h-4 w-4 text-gray-400" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const updateTaskStatus = (index: number, newStatus: string) => {
    const updatedTasks = [...tasks];
    const currentTask = updatedTasks[index];
    if (!currentTask) return;
    
    updatedTasks[index] = { 
      task: currentTask.task,
      priority: currentTask.priority,
      status: newStatus 
    };
    setTasks(updatedTasks);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="h-5 w-5" />
          Action Items
        </CardTitle>
        <CardDescription>
          AI-generated actionable tasks from your research
        </CardDescription>
      </CardHeader>
      <CardContent>
        {!hasGenerated ? (
          <div className="text-center py-8">
            <Button
              onClick={generateTasks}
              disabled={isGenerating}
              className="flex items-center gap-2"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generating Tasks...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Generate Action Items
                </>
              )}
            </Button>
            <p className="text-sm text-gray-500 mt-2">
              Click to generate actionable tasks from your research
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Generated Tasks:</span>
                <Badge variant="secondary">{tasks.length}</Badge>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={generateTasks}
                disabled={isGenerating}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
            </div>

            {tasks.length === 0 ? (
              <div className="text-center py-4 text-gray-500">
                <AlertCircle className="h-8 w-8 mx-auto mb-2 text-gray-400" />
                <p>
                  No tasks were generated. Try regenerating with different
                  content.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.map((task, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-3 border rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-center gap-2 mt-1">
                      {getStatusIcon(task.status)}
                    </div>
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900 mb-1">
                        {task.task}
                      </p>
                      <div className="flex items-center gap-2">
                        <Badge className={getPriorityColor(task.priority)}>
                          {task.priority}
                        </Badge>
                        <Badge variant="outline">{task.status}</Badge>
                      </div>
                    </div>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => updateTaskStatus(index, "in_progress")}
                        className="h-6 px-2"
                      >
                        Start
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => updateTaskStatus(index, "completed")}
                        className="h-6 px-2"
                      >
                        Complete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {tasks.length > 0 && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                <h4 className="text-sm font-medium text-blue-900 mb-2">
                  Task Management Tips:
                </h4>
                <ul className="text-xs text-blue-700 space-y-1">
                  <li>
                    • Click &quot;Start&quot; to mark a task as in progress
                  </li>
                  <li>• Click &quot;Complete&quot; when you finish a task</li>
                  <li>• High priority tasks should be tackled first</li>
                  <li>• Use these tasks to turn insights into action</li>
                </ul>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
