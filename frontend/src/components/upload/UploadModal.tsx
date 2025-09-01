"use client";

import React, { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { 
  XMarkIcon, 
  CloudArrowUpIcon, 
  DocumentIcon,
  PhotoIcon,
  VideoCameraIcon,
  MusicalNoteIcon,
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from "@heroicons/react/24/outline";
import { cn } from "@/lib/utils";

interface UploadedFile {
  id: string;
  file: File;
  progress: number;
  status: "uploading" | "completed" | "error";
  error?: string;
}

interface UploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpload?: (files: File[]) => void;
  className?: string;
}

export function UploadModal({ 
  isOpen, 
  onClose, 
  onUpload,
  className 
}: UploadModalProps) {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      progress: 0,
      status: "uploading" as const
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
    setIsUploading(true);

    // Simulate upload progress
    newFiles.forEach((fileObj, index) => {
      const interval = setInterval(() => {
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileObj.id 
              ? { ...f, progress: Math.min(f.progress + 10, 100) }
              : f
          )
        );
      }, 200);

      // Simulate completion
      setTimeout(() => {
        clearInterval(interval);
        setUploadedFiles(prev => 
          prev.map(f => 
            f.id === fileObj.id 
              ? { ...f, status: "completed" as const }
              : f
          )
        );
        
        if (index === newFiles.length - 1) {
          setIsUploading(false);
        }
      }, 2000 + index * 500);
    });

    if (onUpload) {
      onUpload(acceptedFiles);
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/*': ['.txt', '.md', '.pdf', '.doc', '.docx'],
      'image/*': ['.png', '.jpg', '.jpeg', '.gif', '.svg'],
      'video/*': ['.mp4', '.avi', '.mov', '.wmv'],
      'audio/*': ['.mp3', '.wav', '.flac', '.aac'],
      'application/json': ['.json'],
      'application/xml': ['.xml'],
      'text/csv': ['.csv']
    },
    multiple: true
  });

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id));
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return PhotoIcon;
    if (file.type.startsWith('video/')) return VideoCameraIcon;
    if (file.type.startsWith('audio/')) return MusicalNoteIcon;
    return DocumentIcon;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="upload-modal-title"
          id="upload-modal"
        >
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className={cn(
              "relative w-full max-w-2xl bg-cosmos-card/90 backdrop-blur-xl border border-cosmos-accent/20 rounded-2xl shadow-2xl",
              className
            )}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-cosmos-accent/20">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-cosmos-accent/20 rounded-xl flex items-center justify-center">
                  <CloudArrowUpIcon className="w-6 h-6 text-cosmos-accent" />
                </div>
                <div>
                  <h2 id="upload-modal-title" className="text-xl font-semibold text-cosmos-fg">Upload Files</h2>
                  <p className="text-sm text-cosmos-fg/60">Add documents, images, or media to your knowledge base</p>
                </div>
              </div>
              
              <button
                onClick={onClose}
                className="p-2 rounded-lg hover:bg-cosmos-accent/10 transition-colors"
              >
                <XMarkIcon className="w-6 h-6 text-cosmos-fg/60" />
              </button>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6">
              {/* Drop Zone */}
              <div
                {...getRootProps()}
                className={cn(
                  "border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer",
                  isDragActive
                    ? "border-cosmos-accent bg-cosmos-accent/10"
                    : "border-cosmos-accent/30 hover:border-cosmos-accent/50 hover:bg-cosmos-accent/5"
                )}
              >
                <input {...getInputProps()} />
                
                <div className="space-y-4">
                  <div className="w-16 h-16 bg-cosmos-accent/20 rounded-2xl flex items-center justify-center mx-auto">
                    <CloudArrowUpIcon className="w-8 h-8 text-cosmos-accent" />
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold text-cosmos-fg mb-2">
                      {isDragActive ? "Drop files here" : "Drag & drop files here"}
                    </h3>
                    <p className="text-cosmos-fg/60 mb-4">
                      or click to browse files
                    </p>
                    <p className="text-xs text-cosmos-fg/50">
                      Supports: PDF, DOC, TXT, Images, Videos, Audio, JSON, CSV
                    </p>
                  </div>
                </div>
              </div>

              {/* Uploaded Files */}
              {uploadedFiles.length > 0 && (
                <div className="space-y-3">
                  <h4 className="font-medium text-cosmos-fg">Uploaded Files</h4>
                  
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {uploadedFiles.map((fileObj) => {
                      const FileIcon = getFileIcon(fileObj.file);
                      
                      return (
                        <motion.div
                          key={fileObj.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          className="flex items-center gap-3 p-3 bg-cosmos-bg/20 border border-cosmos-accent/10 rounded-lg"
                        >
                          <FileIcon className="w-8 h-8 text-cosmos-accent" />
                          
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-cosmos-fg truncate">
                              {fileObj.file.name}
                            </p>
                            <p className="text-sm text-cosmos-fg/60">
                              {formatFileSize(fileObj.file.size)}
                            </p>
                          </div>

                          <div className="flex items-center gap-2">
                            {/* Status Icon */}
                            {fileObj.status === "uploading" && (
                              <div className="w-5 h-5 border-2 border-cosmos-accent border-t-transparent rounded-full animate-spin" />
                            )}
                            {fileObj.status === "completed" && (
                              <CheckCircleIcon className="w-5 h-5 text-green-400" />
                            )}
                            {fileObj.status === "error" && (
                              <ExclamationTriangleIcon className="w-5 h-5 text-red-400" />
                            )}

                            {/* Progress Bar */}
                            {fileObj.status === "uploading" && (
                              <div className="w-16 h-2 bg-cosmos-accent/20 rounded-full overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${fileObj.progress}%` }}
                                  className="h-full bg-cosmos-accent rounded-full"
                                />
                              </div>
                            )}

                            {/* Remove Button */}
                            <button
                              onClick={() => removeFile(fileObj.id)}
                              className="p-1 rounded hover:bg-red-500/20 text-red-400 transition-colors"
                            >
                              <TrashIcon className="w-4 h-4" />
                            </button>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between p-6 border-t border-cosmos-accent/20">
              <div className="text-sm text-cosmos-fg/60">
                {uploadedFiles.length} file{uploadedFiles.length !== 1 ? 's' : ''} selected
              </div>
              
              <div className="flex items-center gap-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-cosmos-fg/80 hover:text-cosmos-fg transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={onClose}
                  disabled={isUploading || uploadedFiles.length === 0}
                  className="px-6 py-2 bg-cosmos-accent hover:bg-cosmos-accent/90 disabled:bg-cosmos-accent/30 disabled:cursor-not-allowed text-cosmos-bg rounded-lg transition-all"
                >
                  {isUploading ? "Uploading..." : "Upload Files"}
                </button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
