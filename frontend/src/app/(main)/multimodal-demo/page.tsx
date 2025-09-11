"use client";

import React, { useState, Suspense } from 'react';
import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';
import { 
  CloudArrowUpIcon,
  DocumentIcon,
  PhotoIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  SparklesIcon,
  CpuChipIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';
import { Card, CardContent, CardHeader, CardTitle } from '@/ui/ui/card';
import { Button } from '@/ui/ui/button';
import { Badge } from '@/ui/ui/badge';
import { Skeleton } from '@/ui/ui/skeleton';
import { useToast } from '@/hooks/useToast';

// Lazy load heavy components
const MultimodalUpload = dynamic(() => import('@/ui/MultimodalUpload'), {
  loading: () => <Skeleton className="h-64 w-full" />
});

const QueryForm = dynamic(() => import('@/ui/QueryForm'), {
  loading: () => <Skeleton className="h-32 w-full" />
});

interface UploadedFile {
  file_id: string;
  filename: string;
  file_type: string;
  processed: boolean;
  indexed: boolean;
  extracted_content?: {
    text: string;
    metadata: any;
  };
}

export default function MultimodalDemoPage() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const { toast } = useToast();

  const handleFileUploaded = (file: UploadedFile) => {
    setUploadedFiles(prev => [...prev, file]);
    toast({
      title: "File Uploaded Successfully",
      description: `"${file.filename}" has been processed and indexed`,
      variant: "success",
    });
  };

  const handleUploadError = (error: string) => {
    toast({
      title: "Upload Failed",
      description: error,
      variant: "destructive",
    });
  };

  const handleQuerySubmit = (response: any) => {
    console.log('Query response:', response);
    toast({
      title: "Query Submitted",
      description: "Your query has been processed successfully",
      variant: "success",
    });
  };

  const features = [
    {
      icon: PhotoIcon,
      title: "Visual Content",
      description: "Upload images and videos. We extract metadata and can transcribe audio from videos.",
      color: "text-cosmic-primary-500"
    },
    {
      icon: DocumentIcon,
      title: "Documents",
      description: "Process PDFs, Word docs, and text files. Full text extraction and indexing for search.",
      color: "text-cosmic-success"
    },
    {
      icon: MusicalNoteIcon,
      title: "Audio & Archives",
      description: "Transcribe audio files to text and extract content from ZIP/RAR archives.",
      color: "text-cosmic-secondary-500"
    }
  ];

  return (
    <div className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center mb-12"
          >
            <h1 className="text-4xl sm:text-5xl font-bold cosmic-text-primary mb-4">
              Multimodal Knowledge Platform
            </h1>
            <p className="text-lg cosmic-text-secondary max-w-3xl mx-auto">
              Upload images, videos, documents, audio files, and archives. Our AI will extract content, 
              index it for search, and you can query across all your uploaded knowledge.
            </p>
          </motion.div>

          {/* Features Grid */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="grid md:grid-cols-3 gap-6 mb-12"
          >
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.4, delay: 0.1 * index }}
              >
                <Card className="cosmic-card p-6 h-full">
                  <div className={`w-12 h-12 bg-cosmic-primary-500/20 rounded-lg flex items-center justify-center mb-4`}>
                    <feature.icon className={`w-6 h-6 ${feature.color}`} />
                  </div>
                  <h3 className="text-lg font-semibold cosmic-text-primary mb-2">{feature.title}</h3>
                  <p className="cosmic-text-secondary">{feature.description}</p>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mb-12"
          >
            <MultimodalUpload 
              onFileUploaded={handleFileUploaded}
              onError={handleUploadError}
            />
          </motion.div>

          {/* Query Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.6 }}
            className="mb-12"
          >
            <Card className="cosmic-card">
              <CardHeader>
                <CardTitle className="cosmic-text-primary flex items-center gap-2">
                  <SparklesIcon className="h-5 w-5 text-cosmic-primary-500" />
                  Query Your Knowledge
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="cosmic-text-secondary mb-6">
                  Ask questions about your uploaded content, web search results, or general knowledge. 
                  Our AI will search across all sources to provide comprehensive answers.
                </p>
                <QueryForm 
                  onSubmit={handleQuerySubmit}
                  placeholder="Ask about your uploaded files or any topic..."
                />
              </CardContent>
            </Card>
          </motion.div>

          {/* Uploaded Files Summary */}
          {uploadedFiles.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="mb-12"
            >
              <Card className="cosmic-card">
                <CardHeader>
                  <CardTitle className="cosmic-text-primary flex items-center gap-2">
                    <CpuChipIcon className="h-5 w-5 text-cosmic-primary-500" />
                    Your Knowledge Base ({uploadedFiles.length} files)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {uploadedFiles.map((file) => (
                      <div key={file.file_id} className="cosmic-bg-secondary rounded-lg p-4 border border-cosmic-border-primary">
                        <h3 className="font-medium cosmic-text-primary mb-2">{file.filename}</h3>
                        <div className="text-sm cosmic-text-secondary space-y-1">
                          <p>Type: <span className="capitalize">{file.file_type}</span></p>
                          <p>Status: <span className="text-cosmic-success">
                            {file.processed ? 'Processed' : 'Processing...'}
                          </span></p>
                          <p>Searchable: <span className={file.indexed ? 'text-cosmic-primary-500' : 'text-cosmic-text-tertiary'}>
                            {file.indexed ? 'Yes' : 'No'}
                          </span></p>
                          {file.extracted_content?.text && (
                            <p className="text-xs cosmic-text-tertiary mt-2 line-clamp-3">
                              {file.extracted_content.text.slice(0, 150)}...
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Real-time Features Notice */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 1.0 }}
          >
            <Card className="cosmic-card border-cosmic-primary-500/20">
              <CardHeader>
                <CardTitle className="cosmic-text-primary flex items-center gap-2">
                  <GlobeAltIcon className="h-5 w-5 text-cosmic-primary-500" />
                  🚀 Real-time AI Features Enabled
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="cosmic-text-secondary space-y-2">
                  <li className="flex items-center gap-2">
                    <span className="text-cosmic-success">✅</span>
                    <span><strong>Live LLM Queries:</strong> Real OpenAI/Anthropic API calls (no mocking)</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-cosmic-success">✅</span>
                    <span><strong>Vector Database:</strong> Automatic indexing of web search results and uploaded content</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-cosmic-success">✅</span>
                    <span><strong>Hybrid Search:</strong> Combines vector similarity with keyword search and Wikipedia</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-cosmic-success">✅</span>
                    <span><strong>Content Processing:</strong> Extract text from PDFs, transcribe videos/audio</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-cosmic-success">✅</span>
                    <span><strong>Knowledge Integration:</strong> Query across uploaded files and web knowledge</span>
                  </li>
                </ul>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
