'use client';

import React, { useState } from 'react';
import { apiClient } from '@/services/api-client';
import { Button } from '@/ui/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/ui/ui/card';
import { Input } from '@/ui/ui/input';
import { Badge } from '@/ui/ui/badge';
import { Alert, AlertDescription } from '@/ui/ui/alert';
import { Loader2, CheckCircle, XCircle, Server } from 'lucide-react';

export default function TestApiPage() {
  const [healthStatus, setHealthStatus] = useState<'idle' | 'loading' | 'success' | 'error'>('idle');
  const [healthData, setHealthData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [testQuery, setTestQuery] = useState('What is artificial intelligence?');
  const [queryResult, setQueryResult] = useState<any>(null);
  const [queryLoading, setQueryLoading] = useState(false);

  const testHealthCheck = async () => {
    setHealthStatus('loading');
    setError(null);
    
    try {
      const data = await apiClient.healthCheck();
      setHealthData(data);
      setHealthStatus('success');
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend');
      setHealthStatus('error');
    }
  };

  const testQuerySubmission = async () => {
    setQueryLoading(true);
    setError(null);
    
    try {
      const result = await apiClient.submitQuery(testQuery);
      setQueryResult(result);
    } catch (err: any) {
      setError(err.message || 'Failed to submit query');
    } finally {
      setQueryLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">API Integration Test</h1>
          <p className="text-muted-foreground">
            Test the connection to the backend API and verify proxy configuration
          </p>
        </div>
        <Badge variant="outline" className="flex items-center gap-2">
          <Server className="h-4 w-4" />
          {process.env['NEXT_PUBLIC_API_BASE_URL'] || 'http://localhost:8000'}
        </Badge>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Health Check Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5" />
              Backend Health Check
            </CardTitle>
            <CardDescription>
              Test the connection to the backend API
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Button 
              onClick={testHealthCheck} 
              disabled={healthStatus === 'loading'}
              className="w-full"
            >
              {healthStatus === 'loading' && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Test Connection
            </Button>

            {healthStatus === 'success' && (
              <Alert>
                <CheckCircle className="h-4 w-4" />
                <AlertDescription>
                  Backend is healthy! Response: {JSON.stringify(healthData)}
                </AlertDescription>
              </Alert>
            )}

            {healthStatus === 'error' && (
              <Alert variant="destructive">
                <XCircle className="h-4 w-4" />
                <AlertDescription>
                  {error}
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Query Test Card */}
        <Card>
          <CardHeader>
            <CardTitle>Query Test</CardTitle>
            <CardDescription>
              Test submitting a query to the backend
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="test-query" className="text-sm font-medium">
                Test Query
              </label>
              <Input
                id="test-query"
                value={testQuery}
                onChange={(e) => setTestQuery(e.target.value)}
                placeholder="Enter a test query..."
              />
            </div>
            
            <Button 
              onClick={testQuerySubmission} 
              disabled={queryLoading}
              className="w-full"
            >
              {queryLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Submit Query
            </Button>

            {queryResult && (
              <div className="mt-4 p-4 bg-muted rounded-lg">
                <h4 className="font-semibold mb-2">Query Result:</h4>
                <pre className="text-sm overflow-auto">
                  {JSON.stringify(queryResult, null, 2)}
                </pre>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Environment Info */}
      <Card>
        <CardHeader>
          <CardTitle>Environment Configuration</CardTitle>
          <CardDescription>
            Current API configuration and environment variables
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="font-medium">API Base URL:</span>
              <code className="bg-muted px-2 py-1 rounded">
                {process.env['NEXT_PUBLIC_API_BASE_URL'] || 'http://localhost:8000'}
              </code>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Node Environment:</span>
              <code className="bg-muted px-2 py-1 rounded">
                {process.env.NODE_ENV}
              </code>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Next.js Version:</span>
              <code className="bg-muted px-2 py-1 rounded">
                {process.env['NEXT_PUBLIC_NEXT_VERSION'] || '14.2.5'}
              </code>
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <XCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
} 