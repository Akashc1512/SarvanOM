"use client";

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, File, Image, Video, Music, Archive, FileText, X, Check } from 'lucide-react';

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

interface MultimodalUploadProps {
  onFileUploaded?: (file: UploadedFile) => void;
  onError?: (error: string) => void;
}

const SUPPORTED_TYPES = {
  images: ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp'],
  videos: ['.mp4', '.avi', '.mov', '.webm', '.mkv'],
  documents: ['.pdf', '.doc', '.docx', '.txt', '.md'],
  audio: ['.mp3', '.wav', '.ogg', '.m4a'],
  archives: ['.zip', '.rar', '.7z', '.tar']
};

const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB

const getFileIcon = (fileType: string) => {
  switch (fileType) {
    case 'image': return <Image className="w-6 h-6" />;
    case 'video': return <Video className="w-6 h-6" />;
    case 'audio': return <Music className="w-6 h-6" />;
    case 'document': return <FileText className="w-6 h-6" />;
    case 'archive': return <Archive className="w-6 h-6" />;
    default: return <File className="w-6 h-6" />;
  }
};

export default function MultimodalUpload({ onFileUploaded, onError }: MultimodalUploadProps) {
  const [uploading, setUploading] = useState(false);
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    for (const file of acceptedFiles) {
      if (file.size > MAX_FILE_SIZE) {
        onError?.(`File ${file.name} is too large. Maximum size is 100MB.`);
        continue;
      }

      setUploading(true);
      try {
        const formData = new FormData();
        formData.append('file', file);

        const apiBase = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${apiBase}/api/multimodal/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({ detail: 'Upload failed' }));
          throw new Error(errorData.detail || 'Upload failed');
        }

        const result: UploadedFile = await response.json();
        setUploadedFiles(prev => [...prev, result]);
        onFileUploaded?.(result);

      } catch (error) {
        console.error('Upload error:', error);
        onError?.(error instanceof Error ? error.message : 'Upload failed');
      } finally {
        setUploading(false);
      }
    }
  }, [onFileUploaded, onError]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    multiple: true,
    accept: {
      'image/*': SUPPORTED_TYPES.images,
      'video/*': SUPPORTED_TYPES.videos,
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/*': ['.txt', '.md'],
      'audio/*': SUPPORTED_TYPES.audio,
      'application/zip': ['.zip'],
      'application/x-rar-compressed': ['.rar'],
      'application/x-7z-compressed': ['.7z'],
    },
    maxSize: MAX_FILE_SIZE,
  });

  const removeFile = (fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.file_id !== fileId));
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${isDragActive 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-gray-400'
          }
          ${uploading ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input {...getInputProps()} />
        <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
        
        {uploading ? (
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-700">Processing file...</p>
            <div className="w-32 mx-auto bg-gray-200 rounded-full h-2">
              <div className="bg-blue-600 h-2 rounded-full animate-pulse w-full"></div>
            </div>
          </div>
        ) : isDragActive ? (
          <p className="text-lg font-medium text-blue-600">Drop files here...</p>
        ) : (
          <div className="space-y-2">
            <p className="text-lg font-medium text-gray-700">
              Drag & drop files here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supports images, videos, documents, audio, and archives (max 100MB)
            </p>
          </div>
        )}
      </div>

      {/* Supported File Types */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Supported File Types:</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xs">
          <div>
            <h4 className="font-medium text-gray-600 mb-1">Images</h4>
            <p className="text-gray-500">{SUPPORTED_TYPES.images.join(', ')}</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-600 mb-1">Videos</h4>
            <p className="text-gray-500">{SUPPORTED_TYPES.videos.join(', ')}</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-600 mb-1">Documents</h4>
            <p className="text-gray-500">{SUPPORTED_TYPES.documents.join(', ')}</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-600 mb-1">Audio</h4>
            <p className="text-gray-500">{SUPPORTED_TYPES.audio.join(', ')}</p>
          </div>
          <div>
            <h4 className="font-medium text-gray-600 mb-1">Archives</h4>
            <p className="text-gray-500">{SUPPORTED_TYPES.archives.join(', ')}</p>
          </div>
        </div>
      </div>

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium text-gray-800">Uploaded Files</h3>
          <div className="space-y-2">
            {uploadedFiles.map((file) => (
              <div
                key={file.file_id}
                className="flex items-center justify-between p-3 bg-white border border-gray-200 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  {getFileIcon(file.file_type)}
                  <div>
                    <p className="font-medium text-gray-800">{file.filename}</p>
                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                      <span className="capitalize">{file.file_type}</span>
                      {file.processed && (
                        <>
                          <span>•</span>
                          <span className="flex items-center space-x-1">
                            <Check className="w-3 h-3 text-green-500" />
                            <span>Processed</span>
                          </span>
                        </>
                      )}
                      {file.indexed && (
                        <>
                          <span>•</span>
                          <span className="flex items-center space-x-1">
                            <Check className="w-3 h-3 text-blue-500" />
                            <span>Indexed</span>
                          </span>
                        </>
                      )}
                    </div>
                    {file.extracted_content?.text && (
                      <p className="text-xs text-gray-400 mt-1 max-w-md truncate">
                        {file.extracted_content.text.slice(0, 100)}...
                      </p>
                    )}
                  </div>
                </div>
                <button
                  onClick={() => removeFile(file.file_id)}
                  className="p-1 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
