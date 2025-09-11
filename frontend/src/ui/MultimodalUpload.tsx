"use client";

import React, { useState, useCallback, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  CloudArrowUpIcon,
  DocumentIcon,
  PhotoIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  ArchiveBoxIcon,
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

interface UploadedFile {
  id: string;
  file: File;
  progress: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  error?: string;
  processed?: boolean;
  indexed?: boolean;
  extractedContent?: {
    text: string;
    metadata: any;
  };
}

interface MultimodalUploadProps {
  onFileUploaded?: (file: UploadedFile) => void;
  onError?: (error: string) => void;
  className?: string;
  maxFiles?: number;
  maxFileSize?: number; // in MB
  acceptedTypes?: string[];
}

export default function MultimodalUpload({
  onFileUploaded,
  onError,
  className,
  maxFiles = 10,
  maxFileSize = 100, // 100MB
  acceptedTypes = [
    'image/*',
    'video/*',
    'audio/*',
    'application/pdf',
    'text/*',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/zip',
    'application/x-rar-compressed'
  ]
}: MultimodalUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const getFileIcon = (fileType: string) => {
    if (fileType.startsWith('image/')) return PhotoIcon;
    if (fileType.startsWith('video/')) return VideoCameraIcon;
    if (fileType.startsWith('audio/')) return MusicalNoteIcon;
    if (fileType === 'application/pdf') return DocumentIcon;
    if (fileType.includes('zip') || fileType.includes('rar')) return ArchiveBoxIcon;
    return DocumentIcon;
  };

  const getFileTypeColor = (fileType: string) => {
    if (fileType.startsWith('image/')) return 'text-cosmic-success';
    if (fileType.startsWith('video/')) return 'text-cosmic-primary-500';
    if (fileType.startsWith('audio/')) return 'text-cosmic-secondary-500';
    if (fileType === 'application/pdf') return 'text-cosmic-error';
    if (fileType.includes('zip') || fileType.includes('rar')) return 'text-cosmic-warning';
    return 'text-cosmic-text-primary';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const validateFile = (file: File): string | null => {
    if (file.size > maxFileSize * 1024 * 1024) {
      return `File size exceeds ${maxFileSize}MB limit`;
    }
    
    const isValidType = acceptedTypes.some(type => {
      if (type.endsWith('/*')) {
        return file.type.startsWith(type.slice(0, -1));
      }
      return file.type === type;
    });
    
    if (!isValidType) {
      return 'File type not supported';
    }
    
    return null;
  };

  const handleFiles = useCallback((fileList: FileList) => {
    const newFiles: UploadedFile[] = [];
    const errors: string[] = [];

    Array.from(fileList).forEach((file) => {
      const error = validateFile(file);
      if (error) {
        errors.push(`${file.name}: ${error}`);
        return;
      }

      if (files.length + newFiles.length >= maxFiles) {
        errors.push(`Maximum ${maxFiles} files allowed`);
        return;
      }

      const uploadedFile: UploadedFile = {
        id: Math.random().toString(36).substr(2, 9),
        file,
        progress: 0,
        status: 'uploading'
      };

      newFiles.push(uploadedFile);
    });

    if (errors.length > 0) {
      onError?.(errors.join(', '));
    }

    if (newFiles.length > 0) {
      setFiles(prev => [...prev, ...newFiles]);
      uploadFiles(newFiles);
    }
  }, [files.length, maxFiles, maxFileSize, acceptedTypes, onError]);

  const uploadFiles = async (filesToUpload: UploadedFile[]) => {
    setUploading(true);

    for (const fileData of filesToUpload) {
      try {
        // Simulate upload progress
        for (let progress = 0; progress <= 100; progress += 10) {
          await new Promise(resolve => setTimeout(resolve, 100));
          setFiles(prev => prev.map(f => 
            f.id === fileData.id 
              ? { ...f, progress }
              : f
          ));
        }

        // Simulate processing
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: 'processing' as const }
            : f
        ));

        await new Promise(resolve => setTimeout(resolve, 1000));

        // Complete upload
        const completedFile = {
          ...fileData,
          status: 'completed' as const,
          progress: 100,
          processed: true,
          indexed: Math.random() > 0.3, // Random for demo
          extractedContent: {
            text: `Extracted content from ${fileData.file.name}`,
            metadata: {
              size: fileData.file.size,
              type: fileData.file.type,
              lastModified: fileData.file.lastModified
            }
          }
        };

        setFiles(prev => prev.map(f => 
          f.id === fileData.id ? completedFile : f
        ));

        onFileUploaded?.(completedFile);
      } catch (error) {
        setFiles(prev => prev.map(f => 
          f.id === fileData.id 
            ? { ...f, status: 'error' as const, error: 'Upload failed' }
            : f
        ));
        onError?.('Upload failed');
      }
    }

    setUploading(false);
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFiles(e.dataTransfer.files);
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files);
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={cn("space-y-6", className)}>
      {/* Dropzone */}
      <Card className="cosmic-card">
        <CardHeader>
          <CardTitle className="cosmic-text-primary">Upload Files</CardTitle>
        </CardHeader>
        <CardContent>
          <div
            className={cn(
              "relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200",
              isDragOver
                ? "border-cosmic-primary-500 bg-cosmic-primary-500/10 cosmic-glow-primary"
                : "border-cosmic-border-primary hover:border-cosmic-primary-500/50"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept={acceptedTypes.join(',')}
              onChange={handleFileInput}
              className="hidden"
            />
            
            <motion.div
              initial={{ scale: 1 }}
              animate={{ scale: isDragOver ? 1.05 : 1 }}
              transition={{ duration: 0.2 }}
            >
              <CloudArrowUpIcon className="h-12 w-12 text-cosmic-primary-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold cosmic-text-primary mb-2">
                {isDragOver ? 'Drop files here' : 'Drag & drop files here'}
              </h3>
              <p className="cosmic-text-secondary mb-4">
                or click to browse files
              </p>
              <Button
                onClick={openFileDialog}
                className="cosmic-btn-primary"
                disabled={uploading}
              >
                Choose Files
              </Button>
            </motion.div>
            
            <div className="mt-4 text-sm cosmic-text-tertiary">
              <p>Supported: Images, Videos, Audio, PDFs, Documents, Archives</p>
              <p>Max file size: {maxFileSize}MB • Max files: {maxFiles}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* File Queue */}
      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
          >
            <Card className="cosmic-card">
              <CardHeader>
                <CardTitle className="cosmic-text-primary flex items-center gap-2">
                  <ClockIcon className="h-5 w-5" />
                  Upload Queue ({files.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {files.map((fileData) => {
                    const FileIcon = getFileIcon(fileData.file.type);
                    const typeColor = getFileTypeColor(fileData.file.type);
                    
                    return (
                      <motion.div
                        key={fileData.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="flex items-center gap-4 p-3 cosmic-bg-secondary rounded-lg border border-cosmic-border-primary"
                      >
                        <FileIcon className={cn("h-8 w-8 flex-shrink-0", typeColor)} />
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <p className="font-medium cosmic-text-primary truncate">
                              {fileData.file.name}
                            </p>
                            <Badge variant="outline" className="text-xs border-cosmic-border-primary text-cosmic-text-primary">
                              {formatFileSize(fileData.file.size)}
                            </Badge>
          </div>
                          
                          <div className="flex items-center gap-2 mb-2">
                            {fileData.status === 'uploading' && (
                              <Badge variant="outline" className="text-xs border-cosmic-primary-500 text-cosmic-primary-500">
                                Uploading
                              </Badge>
                            )}
                            {fileData.status === 'processing' && (
                              <Badge variant="outline" className="text-xs border-cosmic-warning text-cosmic-warning">
                                Processing
                              </Badge>
                            )}
                            {fileData.status === 'completed' && (
                              <Badge variant="outline" className="text-xs border-cosmic-success text-cosmic-success">
                                <CheckCircleIcon className="h-3 w-3 mr-1" />
                                Completed
                              </Badge>
                            )}
                            {fileData.status === 'error' && (
                              <Badge variant="outline" className="text-xs border-cosmic-error text-cosmic-error">
                                <ExclamationTriangleIcon className="h-3 w-3 mr-1" />
                                Error
                              </Badge>
                            )}
                            
                            {fileData.processed && (
                              <Badge variant="outline" className="text-xs border-cosmic-border-primary text-cosmic-text-primary">
                                Processed
                              </Badge>
                            )}
                            {fileData.indexed && (
                              <Badge variant="outline" className="text-xs border-cosmic-success text-cosmic-success">
                                Indexed
                              </Badge>
        )}
      </div>

                          {(fileData.status === 'uploading' || fileData.status === 'processing') && (
                            <Progress value={fileData.progress} className="h-2" />
                          )}
                          
                          {fileData.error && (
                            <p className="text-sm text-cosmic-error mt-1">{fileData.error}</p>
                      )}
                    </div>
                        
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => removeFile(fileData.id)}
                          className="cosmic-btn-secondary"
                        >
                          <XMarkIcon className="h-4 w-4" />
                        </Button>
                      </motion.div>
                    );
                  })}
              </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
