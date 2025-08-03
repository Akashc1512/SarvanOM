"use client";

import { useEffect, useState, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { ArrowLeft, Calendar, Edit, Trash2, Tag, BookOpen } from "lucide-react";
import Link from "next/link";

interface MemoryDetail {
  id: string;
  title: string;
  content: string;
  summary: string;
  created_at: string;
  updated_at: string;
  tags?: string[];
  category?: string;
  source_query?: string;
  confidence?: number;
}

export default function MemoryDetail() {
  const params = useParams();
  const router = useRouter();
  const [detail, setDetail] = useState<MemoryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (params['id']) {
      fetchMemoryDetail(params['id'] as string);
    }
  }, [params, fetchMemoryDetail]);

  const fetchMemoryDetail = useCallback(async (id: string) => {
    try {
      setLoading(true);
      const response = await fetch(`/api/memory/${id}`);
      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Memory not found');
        }
        throw new Error('Failed to fetch memory details');
      }
      const data = await response.json();
      setDetail(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "bg-green-100 text-green-800";
    if (confidence >= 0.6) return "bg-yellow-100 text-yellow-800";
    return "bg-red-100 text-red-800";
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <h3 className="text-red-800 font-medium">Error</h3>
          <p className="text-red-600">{error}</p>
          <div className="mt-4 flex gap-2">
            <Button 
              onClick={() => router.back()} 
              variant="outline"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Go Back
            </Button>
            <Button 
              onClick={() => fetchMemoryDetail(params['id'] as string)} 
              variant="outline"
            >
              Try Again
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="p-6">
        <div className="text-center py-12">
          <BookOpen className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Memory not found</h3>
          <p className="text-gray-600 mb-4">
            The memory you&apos;re looking for doesn&apos;t exist or has been removed.
          </p>
          <Link href="/memory">
            <Button>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Memory Workspace
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Link href="/memory">
            <Button variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{detail.title}</h1>
            <div className="flex items-center gap-4 mt-2 text-sm text-gray-600">
              <div className="flex items-center">
                <Calendar className="h-4 w-4 mr-1" />
                Created {formatDate(detail.created_at)}
              </div>
              {detail.updated_at !== detail.created_at && (
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 mr-1" />
                  Updated {formatDate(detail.updated_at)}
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Edit className="h-4 w-4 mr-2" />
            Edit
          </Button>
          <Button variant="outline" size="sm" className="text-red-600 hover:text-red-700">
            <Trash2 className="h-4 w-4 mr-2" />
            Delete
          </Button>
        </div>
      </div>

      {/* Metadata */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {detail.category && (
              <div>
                <p className="font-medium text-gray-700 mb-1">Category</p>
                <Badge variant="secondary">{detail.category}</Badge>
              </div>
            )}
            {detail.confidence && (
              <div>
                <p className="font-medium text-gray-700 mb-1">Confidence</p>
                <Badge className={getConfidenceColor(detail.confidence)}>
                  {(detail.confidence * 100).toFixed(0)}% confidence
                </Badge>
              </div>
            )}
            {detail.tags && detail.tags.length > 0 && (
              <div className="md:col-span-2">
                <p className="font-medium text-gray-700 mb-2 flex items-center">
                  <Tag className="h-4 w-4 mr-1" />
                  Tags
                </p>
                <div className="flex flex-wrap gap-2">
                  {detail.tags.map((tag, index) => (
                    <Badge key={index} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
            {detail.source_query && (
              <div className="md:col-span-2">
                <p className="font-medium text-gray-700 mb-1">Original Query</p>
                <p className="text-gray-600 italic">&quot;{detail.source_query}&quot;</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Content */}
      <Card>
        <CardHeader>
          <CardTitle>Content</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="prose prose-gray max-w-none">
            <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {detail.content}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 