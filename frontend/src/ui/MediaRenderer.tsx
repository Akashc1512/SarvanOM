"use client";

import { useState } from "react";
import Image from "next/image";
import { Play, ExternalLink, Image as ImageIcon, Video, AlertCircle } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent } from "@/ui/ui/card";
import { cn } from "@/lib/utils";

interface MediaItem {
  type: "image" | "video";
  url: string;
  alt?: string;
  title?: string;
  description?: string;
  thumbnail?: string;
}

interface MediaRendererProps {
  media: MediaItem[];
  className?: string;
}

export function MediaRenderer({ media, className = "" }: MediaRendererProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);
  const [imageErrors, setImageErrors] = useState<Set<number>>(new Set());

  const handleImageError = (index: number) => {
    setImageErrors(prev => new Set(prev).add(index));
  };

  const isYouTubeUrl = (url: string): boolean => {
    return url.includes('youtube.com') || url.includes('youtu.be');
  };

  const getYouTubeEmbedUrl = (url: string): string => {
    const videoId = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/)?.[1];
    return videoId ? `https://www.youtube.com/embed/${videoId}` : url;
  };

  const isVideoUrl = (url: string): boolean => {
    return url.includes('.mp4') || url.includes('.webm') || url.includes('.ogg') || isYouTubeUrl(url);
  };

  if (!media || media.length === 0) {
    return null;
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center space-x-2 mb-4">
        <div className="flex items-center space-x-1">
          <ImageIcon className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          <Video className="h-4 w-4 text-blue-600 dark:text-blue-400" />
        </div>
        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
          Media ({media.length})
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {media.map((item, index) => (
          <Card 
            key={index}
            className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-purple-200/50 dark:border-purple-800/50 overflow-hidden hover:shadow-lg transition-all duration-300"
          >
            <CardContent className="p-0">
              {/* Media Content */}
              <div className="relative aspect-video bg-gray-100 dark:bg-slate-700">
                {item.type === "image" && !imageErrors.has(index) ? (
                  <Image
                    src={item.url}
                    alt={item.alt || item.title || "Media content"}
                    fill
                    className="object-cover"
                    onError={() => handleImageError(index)}
                    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                  />
                ) : item.type === "video" || isVideoUrl(item.url) ? (
                  <div className="relative w-full h-full">
                    {isYouTubeUrl(item.url) ? (
                      <iframe
                        src={getYouTubeEmbedUrl(item.url)}
                        title={item.title || "YouTube video"}
                        className="w-full h-full"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
                    ) : (
                      <video
                        src={item.url}
                        controls
                        className="w-full h-full object-cover"
                        poster={item.thumbnail}
                      >
                        <source src={item.url} type="video/mp4" />
                        Your browser does not support the video tag.
                      </video>
                    )}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="bg-black/50 rounded-full p-2">
                        <Play className="h-6 w-6 text-white" />
                      </div>
                    </div>
                  </div>
                ) : imageErrors.has(index) ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <AlertCircle className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Image failed to load
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center">
                      <ImageIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        Loading...
                      </p>
                    </div>
                  </div>
                )}
              </div>

              {/* Media Info */}
              {(item.title || item.description) && (
                <div className="p-4">
                  {item.title && (
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-1 line-clamp-2">
                      {item.title}
                    </h4>
                  )}
                  {item.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-3">
                      {item.description}
                    </p>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="p-4 pt-0">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                    {item.type}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => window.open(item.url, '_blank')}
                    className="text-xs"
                  >
                    <ExternalLink className="h-3 w-3 mr-1" />
                    View
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Expanded View Modal */}
      {expandedIndex !== null && media[expandedIndex] && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="relative max-w-4xl max-h-[90vh] bg-white dark:bg-slate-800 rounded-lg overflow-hidden">
            <div className="absolute top-4 right-4 z-10">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setExpandedIndex(null)}
                className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm"
              >
                ×
              </Button>
            </div>
            
            <div className="relative aspect-video">
              {media[expandedIndex].type === "image" ? (
                <Image
                  src={media[expandedIndex].url}
                  alt={media[expandedIndex].alt || media[expandedIndex].title || "Expanded media"}
                  fill
                  className="object-contain"
                  sizes="90vw"
                />
              ) : (
                <video
                  src={media[expandedIndex].url}
                  controls
                  className="w-full h-full object-contain"
                  poster={media[expandedIndex].thumbnail}
                >
                  <source src={media[expandedIndex].url} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              )}
            </div>

            {(media[expandedIndex].title || media[expandedIndex].description) && (
              <div className="p-6">
                {media[expandedIndex].title && (
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {media[expandedIndex].title}
                  </h3>
                )}
                {media[expandedIndex].description && (
                  <p className="text-gray-600 dark:text-gray-300">
                    {media[expandedIndex].description}
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
