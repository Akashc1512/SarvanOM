"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { 
  CogIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ChartBarIcon,
  ServerIcon,
  CircleStackIcon,
  CpuChipIcon,
  GlobeAltIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  TrashIcon,
  DocumentArrowDownIcon,
  EyeIcon,
  EyeSlashIcon
} from "@heroicons/react/24/outline";

interface FeatureFlag {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  lastModified: string;
  modifiedBy: string;
}

interface HealthStatus {
  service: string;
  status: "healthy" | "degraded" | "down";
  uptime: string;
  responseTime: string;
  lastCheck: string;
}

interface BudgetConfig {
  provider: string;
  monthlyLimit: number;
  currentUsage: number;
  alertThreshold: number;
}

export default function AdminPage() {
  const [featureFlags, setFeatureFlags] = useState<FeatureFlag[]>([
    {
      id: "1",
      name: "Advanced Search",
      description: "Enable semantic search capabilities",
      enabled: true,
      lastModified: "2024-01-15",
      modifiedBy: "admin"
    },
    {
      id: "2", 
      name: "Real-time Streaming",
      description: "Enable server-sent events for live updates",
      enabled: true,
      lastModified: "2024-01-14",
      modifiedBy: "admin"
    },
    {
      id: "3",
      name: "Knowledge Graph",
      description: "Enable graph visualization features",
      enabled: false,
      lastModified: "2024-01-10",
      modifiedBy: "admin"
    },
    {
      id: "4",
      name: "Multimodal Upload",
      description: "Allow file uploads and processing",
      enabled: true,
      lastModified: "2024-01-12",
      modifiedBy: "admin"
    },
    {
      id: "5",
      name: "Analytics Dashboard",
      description: "Show detailed usage analytics",
      enabled: true,
      lastModified: "2024-01-13",
      modifiedBy: "admin"
    },
    {
      id: "6",
      name: "Beta Features",
      description: "Enable experimental functionality",
      enabled: false,
      lastModified: "2024-01-08",
      modifiedBy: "admin"
    }
  ]);

  const [healthStatus, setHealthStatus] = useState<HealthStatus[]>([
    {
      service: "Database",
      status: "healthy",
      uptime: "99.9%",
      responseTime: "12ms",
      lastCheck: "2 minutes ago"
    },
    {
      service: "Redis Cache",
      status: "degraded", 
      uptime: "98.2%",
      responseTime: "45ms",
      lastCheck: "1 minute ago"
    },
    {
      service: "Vector DB",
      status: "healthy",
      uptime: "99.7%",
      responseTime: "23ms",
      lastCheck: "3 minutes ago"
    },
    {
      service: "LLM Gateway",
      status: "healthy",
      uptime: "99.8%",
      responseTime: "156ms",
      lastCheck: "1 minute ago"
    },
    {
      service: "Search Engine",
      status: "down",
      uptime: "95.1%",
      responseTime: "N/A",
      lastCheck: "5 minutes ago"
    },
    {
      service: "File Storage",
      status: "healthy",
      uptime: "99.9%",
      responseTime: "8ms",
      lastCheck: "2 minutes ago"
    }
  ]);

  const [budgets, setBudgets] = useState<BudgetConfig[]>([
    {
      provider: "OpenAI",
      monthlyLimit: 1000,
      currentUsage: 342,
      alertThreshold: 80
    },
    {
      provider: "Anthropic",
      monthlyLimit: 500,
      currentUsage: 156,
      alertThreshold: 80
    },
    {
      provider: "Hugging Face",
      monthlyLimit: 200,
      currentUsage: 89,
      alertThreshold: 90
    }
  ]);

  const [showDangerZone, setShowDangerZone] = useState(false);
  const [auditNote, setAuditNote] = useState("");

  const toggleFeatureFlag = (id: string) => {
    setFeatureFlags(flags => 
      flags.map(flag => 
        flag.id === id 
          ? { ...flag, enabled: !flag.enabled, lastModified: new Date().toISOString().split('T')[0] || "", modifiedBy: "admin" }
          : flag
      )
    );
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-cosmic-success";
      case "degraded": return "text-cosmic-warning";
      case "down": return "text-cosmic-error";
      default: return "cosmic-text-tertiary";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy": return <CheckCircleIcon className="w-5 h-5" />;
      case "degraded": return <ClockIcon className="w-5 h-5" />;
      case "down": return <XCircleIcon className="w-5 h-5" />;
      default: return <ClockIcon className="w-5 h-5" />;
    }
  };

  const getServiceIcon = (service: string) => {
    switch (service) {
      case "Database": return <CircleStackIcon className="w-5 h-5" />;
      case "Redis Cache": return <ServerIcon className="w-5 h-5" />;
      case "Vector DB": return <CpuChipIcon className="w-5 h-5" />;
      case "LLM Gateway": return <GlobeAltIcon className="w-5 h-5" />;
      case "Search Engine": return <ChartBarIcon className="w-5 h-5" />;
      case "File Storage": return <ServerIcon className="w-5 h-5" />;
      default: return <ServerIcon className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen cosmic-bg-primary">
      <div className="cosmic-container cosmic-section">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold cosmic-text-primary mb-2">Admin Dashboard</h1>
            <p className="cosmic-text-secondary">Manage system configuration, monitor health, and control feature flags</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="cosmic-btn-secondary flex items-center gap-2">
              <DocumentArrowDownIcon className="w-4 h-4" />
              Save Changes
            </div>
            <div className="cosmic-btn-primary flex items-center gap-2">
              <ShieldCheckIcon className="w-4 h-4" />
              System Status
            </div>
          </div>
        </div>

        {/* Feature Flags Grid */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold cosmic-text-primary mb-6 flex items-center gap-2">
            <CogIcon className="w-6 h-6 text-cosmic-primary-500" />
            Feature Flags
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featureFlags.map((flag) => (
              <motion.div
                key={flag.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="cosmic-card p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold cosmic-text-primary">{flag.name}</h3>
                  <button
                    onClick={() => toggleFeatureFlag(flag.id)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      flag.enabled ? 'bg-cosmic-success' : 'bg-cosmic-bg-tertiary'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        flag.enabled ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                <p className="cosmic-text-secondary text-sm mb-4">{flag.description}</p>
                <div className="flex items-center justify-between text-xs cosmic-text-tertiary">
                  <span>Modified: {flag.lastModified}</span>
                  <span>By: {flag.modifiedBy}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Health Tiles */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold cosmic-text-primary mb-6 flex items-center gap-2">
            <ChartBarIcon className="w-6 h-6 text-cosmic-primary-500" />
            System Health
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {healthStatus.map((service, index) => (
              <motion.div
                key={service.service}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="cosmic-card p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    {getServiceIcon(service.service)}
                    <h3 className="text-lg font-semibold cosmic-text-primary">{service.service}</h3>
                  </div>
                  <div className={`flex items-center gap-1 ${getStatusColor(service.status)}`}>
                    {getStatusIcon(service.status)}
                    <span className="text-sm font-medium capitalize">{service.status}</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="cosmic-text-secondary">Uptime:</span>
                    <span className="cosmic-text-primary">{service.uptime}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="cosmic-text-secondary">Response:</span>
                    <span className="cosmic-text-primary">{service.responseTime}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="cosmic-text-secondary">Last Check:</span>
                    <span className="cosmic-text-tertiary">{service.lastCheck}</span>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Budget Sliders */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold cosmic-text-primary mb-6 flex items-center gap-2">
            <ChartBarIcon className="w-6 h-6 text-cosmic-primary-500" />
            Provider Budgets
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {budgets.map((budget) => {
              const usagePercentage = (budget.currentUsage / budget.monthlyLimit) * 100;
              const isOverThreshold = usagePercentage > budget.alertThreshold;
              
              return (
                <motion.div
                  key={budget.provider}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="cosmic-card p-6"
                >
                  <h3 className="text-lg font-semibold cosmic-text-primary mb-4">{budget.provider}</h3>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-2">
                        <span className="cosmic-text-secondary">Usage</span>
                        <span className={`font-medium ${isOverThreshold ? 'text-cosmic-warning' : 'cosmic-text-primary'}`}>
                          ${budget.currentUsage} / ${budget.monthlyLimit}
                        </span>
                      </div>
                      <div className="w-full bg-cosmic-bg-tertiary rounded-full h-2">
                        <div
                          className={`h-2 rounded-full transition-all duration-300 ${
                            isOverThreshold ? 'bg-cosmic-warning' : 'bg-cosmic-primary-500'
                          }`}
                          style={{ width: `${Math.min(usagePercentage, 100)}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="cosmic-text-secondary">Alert at:</span>
                      <span className="cosmic-text-primary">{budget.alertThreshold}%</span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* Danger Zone */}
        <div className="cosmic-card border-cosmic-error/20 bg-cosmic-error/5 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-semibold text-cosmic-error flex items-center gap-2">
              <ExclamationTriangleIcon className="w-6 h-6" />
              Danger Zone
            </h2>
            <button
              onClick={() => setShowDangerZone(!showDangerZone)}
              className="cosmic-btn-secondary text-cosmic-error border-cosmic-error/30 hover:bg-cosmic-error/10"
            >
              {showDangerZone ? <EyeSlashIcon className="w-4 h-4" /> : <EyeIcon className="w-4 h-4" />}
              {showDangerZone ? 'Hide' : 'Show'} Danger Zone
            </button>
          </div>
          
          {showDangerZone && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-4"
            >
              <div className="bg-cosmic-error/10 border border-cosmic-error/20 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-cosmic-error mb-2">Reset All Data</h3>
                <p className="cosmic-text-secondary text-sm mb-4">
                  This will permanently delete all user data, search history, and uploaded files. This action cannot be undone.
                </p>
                <button className="cosmic-btn-secondary text-cosmic-error border-cosmic-error hover:bg-cosmic-error/10">
                  <TrashIcon className="w-4 h-4" />
                  Reset All Data
                </button>
              </div>
              
              <div className="bg-cosmic-warning/10 border border-cosmic-warning/20 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-cosmic-warning mb-2">Clear Cache</h3>
                <p className="cosmic-text-secondary text-sm mb-4">
                  Clear all cached data including search results, embeddings, and temporary files.
                </p>
                <button className="cosmic-btn-secondary text-cosmic-warning border-cosmic-warning hover:bg-cosmic-warning/10">
                  <TrashIcon className="w-4 h-4" />
                  Clear Cache
                </button>
              </div>
            </motion.div>
          )}
        </div>

        {/* Audit Note Field */}
        <div className="mt-8 cosmic-card p-6">
          <h3 className="text-lg font-semibold cosmic-text-primary mb-4">Audit Note</h3>
          <textarea
            value={auditNote}
            onChange={(e) => setAuditNote(e.target.value)}
            placeholder="Add a note about changes made to the system..."
            className="w-full cosmic-input min-h-[100px] resize-none"
          />
          <div className="flex justify-between items-center mt-4">
            <span className="text-sm cosmic-text-tertiary">
              {auditNote.length}/500 characters
            </span>
            <button className="cosmic-btn-primary">
              <DocumentArrowDownIcon className="w-4 h-4" />
              Save Note
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
