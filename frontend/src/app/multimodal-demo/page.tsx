"use client";

import React, { useState } from 'react';
import { Toaster, toast } from 'sonner';
import MultimodalUpload from '@/ui/MultimodalUpload';
import QueryForm from '@/ui/QueryForm';

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

  const handleFileUploaded = (file: UploadedFile) => {
    setUploadedFiles(prev => [...prev, file]);
    toast.success(`File "${file.filename}" uploaded and processed successfully!`, {
      description: file.indexed 
        ? 'Content has been indexed and is now searchable'
        : 'File processed but content not indexed',
    });
  };

  const handleUploadError = (error: string) => {
    toast.error('Upload failed', {
      description: error,
    });
  };

  const handleQuerySubmit = (response: any) => {
    // Query submitted successfully
    console.log('Query response:', response);
  };

  return (
    <div className="min-h-screen cosmic-bg-primary">
      <div className="cosmic-container cosmic-section">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold cosmic-text-primary mb-4">
            SarvanOM Multimodal Knowledge Platform
          </h1>
          <p className="text-lg cosmic-text-secondary max-w-3xl mx-auto">
            Upload images, videos, documents, audio files, and archives. Our AI will extract content, 
            index it for search, and you can query across all your uploaded knowledge.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="cosmic-card p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-cosmic-primary-500/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-cosmic-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold cosmic-text-primary mb-2">Visual Content</h3>
            <p className="cosmic-text-secondary">
              Upload images and videos. We extract metadata and can transcribe audio from videos.
            </p>
          </div>

          <div className="cosmic-card p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-cosmic-success/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-cosmic-success" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold cosmic-text-primary mb-2">Documents</h3>
            <p className="cosmic-text-secondary">
              Process PDFs, Word docs, and text files. Full text extraction and indexing for search.
            </p>
          </div>

          <div className="cosmic-card p-6 rounded-lg shadow-sm">
            <div className="w-12 h-12 bg-cosmic-secondary-500/20 rounded-lg flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-cosmic-secondary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold cosmic-text-primary mb-2">Audio & Archives</h3>
            <p className="cosmic-text-secondary">
              Transcribe audio files to text and extract content from ZIP/RAR archives.
            </p>
          </div>
        </div>

        {/* Upload Section */}
        <div className="cosmic-card rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-2xl font-bold cosmic-text-primary mb-4">Upload Your Files</h2>
          <MultimodalUpload 
            onFileUploaded={handleFileUploaded}
            onError={handleUploadError}
          />
        </div>

        {/* Query Section */}
        <div className="cosmic-card rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-2xl font-bold cosmic-text-primary mb-4">Query Your Knowledge</h2>
          <p className="cosmic-text-secondary mb-6">
            Ask questions about your uploaded content, web search results, or general knowledge. 
            Our AI will search across all sources to provide comprehensive answers.
          </p>
          <QueryForm onQuerySubmit={handleQuerySubmit} />
        </div>

        {/* Uploaded Files Summary */}
        {uploadedFiles.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Your Knowledge Base</h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
              {uploadedFiles.map((file) => (
                <div key={file.file_id} className="border rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 mb-2">{file.filename}</h3>
                  <div className="text-sm text-gray-600 space-y-1">
                    <p>Type: <span className="capitalize">{file.file_type}</span></p>
                    <p>Status: <span className="text-green-600">
                      {file.processed ? 'Processed' : 'Processing...'}
                    </span></p>
                    <p>Searchable: <span className={file.indexed ? 'text-blue-600' : 'text-gray-400'}>
                      {file.indexed ? 'Yes' : 'No'}
                    </span></p>
                    {file.extracted_content?.text && (
                      <p className="text-xs text-gray-500 mt-2 line-clamp-3">
                        {file.extracted_content.text.slice(0, 150)}...
                      </p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Real-time Features Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mt-8">
          <h3 className="text-lg font-semibold text-blue-900 mb-2">🚀 Real-time AI Features Enabled</h3>
          <ul className="text-blue-800 space-y-1">
            <li>✅ <strong>Live LLM Queries:</strong> Real OpenAI/Anthropic API calls (no mocking)</li>
            <li>✅ <strong>Vector Database:</strong> Automatic indexing of web search results and uploaded content</li>
            <li>✅ <strong>Hybrid Search:</strong> Combines vector similarity with keyword search and Wikipedia</li>
            <li>✅ <strong>Content Processing:</strong> Extract text from PDFs, transcribe videos/audio</li>
            <li>✅ <strong>Knowledge Integration:</strong> Query across uploaded files and web knowledge</li>
          </ul>
        </div>
      </div>

      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
        }}
      />
    </div>
  );
}
