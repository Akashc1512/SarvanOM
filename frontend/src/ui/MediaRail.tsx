"use client";

import React, { useState } from "react";
import { Image, Play, ExternalLink, X, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { Card, CardContent } from "@/ui/ui/card";
import { Badge } from "@/ui/ui/badge";
import { cn } from "@/lib/utils";

interface MediaItem {
  type: "image" | "video";
  url: string;
  alt?: string;
  title?: string;
  description?: string;
  thumbnail?: string;
  duration?: string;
  source?: string;
}

interface MediaRailProps {
  media: MediaItem[];
  className?: string;
  maxItems?: number;
  showThumbnails?: boolean;
}

export function MediaRail({ 
  media, 
  className, 
  maxItems = 6,
  showThumbnails = true 
}: MediaRailProps) {
  const [selectedMedia, setSelectedMedia] = useState<MediaItem | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  if (!media || media.length === 0) {
    return null;
  }

  const displayedMedia = media.slice(0, maxItems);
  const hasMore = media.length > maxItems;

  const openModal = (item: MediaItem, index: number) => {
    setSelectedMedia(item);
    setCurrentIndex(index);
  };

  const closeModal = () => {
    setSelectedMedia(null);
  };

  const navigateModal = (direction: 'prev' | 'next') => {
    if (!selectedMedia) return;
    
    const newIndex = direction === 'prev' 
      ? (currentIndex - 1 + media.length) % media.length
      : (currentIndex + 1) % media.length;
    
    setCurrentIndex(newIndex);
    setSelectedMedia(media[newIndex] || null);
  };

  const renderMediaItem = (item: MediaItem, index: number) => {
    const isImage = item.type === "image";
    const displayUrl = item.thumbnail || item.url;

    return (
      <Card 
        key={index}
        className="flex-shrink-0 w-32 h-24 cursor-pointer hover:shadow-lg transition-all duration-200 hover:scale-105 group"
        onClick={() => openModal(item, index)}
      >
        <CardContent className="p-0 relative overflow-hidden rounded-lg h-full">
          {isImage ? (
            <img
              src={displayUrl}
              alt={item.alt || item.title || `Media ${index + 1}`}
              className="w-full h-full object-cover"
              loading="lazy"
              onError={(e) => {
                const target = e.target as HTMLImageElement;
                target.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjI0IiBoZWlnaHQ9IjI0IiBmaWxsPSIjZjMuNGY0ZjUiLz4KPHN2ZyB3aWR0aD0iNDgiIGhlaWdodD0iNDgiIHZpZXdCb3g9IjAgMCA0OCA0OCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTAgMGg0OHY0OEgweiIgZmlsbD0iI2Y5ZmFmYiIvPgo8L3N2Zz4K";
              }}
            />
          ) : (
            <div className="relative w-full h-full bg-gray-900 flex items-center justify-center">
              {item.thumbnail ? (
                <img
                  src={item.thumbnail}
                  alt={item.title || `Video ${index + 1}`}
                  className="w-full h-full object-cover"
                  loading="lazy"
                />
              ) : (
                <div className="w-full h-full bg-gradient-to-br from-gray-700 to-gray-900 flex items-center justify-center">
                  <Play className="h-6 w-6 text-white" />
                </div>
              )}
              <div className="absolute inset-0 flex items-center justify-center bg-black/20 group-hover:bg-black/40 transition-colors">
                <Play className="h-6 w-6 text-white drop-shadow-lg" />
              </div>
              {item.duration && (
                <Badge 
                  variant="secondary" 
                  className="absolute bottom-1 right-1 text-xs bg-black/70 text-white border-0"
                >
                  {item.duration}
                </Badge>
              )}
            </div>
          )}
          
          {/* Type indicator */}
          <Badge 
            variant="outline" 
            className="absolute top-1 left-1 text-xs bg-white/80 dark:bg-black/80"
          >
            <Image className="h-3 w-3 mr-1" />
            {item.type}
          </Badge>
        </CardContent>
      </Card>
    );
  };

  return (
    <>
      <Card className={cn("w-full", className)}>
        <CardContent className="p-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-900 dark:text-white flex items-center">
              <Image className="h-4 w-4 mr-2" />
              Media ({media.length})
            </h3>
            {hasMore && (
              <Badge variant="outline" className="text-xs">
                +{media.length - maxItems} more
              </Badge>
            )}
          </div>
          
          <div className="flex space-x-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600">
            {displayedMedia.map(renderMediaItem)}
          </div>
          
          {hasMore && (
            <p className="text-xs text-gray-500 mt-2">
              Scroll horizontally to see more media items
            </p>
          )}
        </CardContent>
      </Card>

      {/* Modal for full-size media */}
      {selectedMedia && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="relative max-w-4xl max-h-full w-full">
            {/* Navigation */}
            <div className="absolute top-4 right-4 z-10 flex space-x-2">
              {media.length > 1 && (
                <>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigateModal('prev')}
                    className="bg-black/50 border-white/20 text-white hover:bg-black/70"
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => navigateModal('next')}
                    className="bg-black/50 border-white/20 text-white hover:bg-black/70"
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </>
              )}
              <Button
                size="sm"
                variant="outline"
                onClick={closeModal}
                className="bg-black/50 border-white/20 text-white hover:bg-black/70"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>

            {/* Media content */}
            <div className="bg-white dark:bg-gray-900 rounded-lg overflow-hidden">
              {selectedMedia.type === "image" ? (
                <img
                  src={selectedMedia.url}
                  alt={selectedMedia.alt || selectedMedia.title}
                  className="w-full h-auto max-h-[70vh] object-contain"
                />
              ) : (
                <div className="relative">
                  {selectedMedia.url.includes('youtube.com') || selectedMedia.url.includes('youtu.be') ? (
                    <iframe
                      src={selectedMedia.url.replace('watch?v=', 'embed/')}
                      className="w-full h-[50vh]"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  ) : (
                    <video
                      src={selectedMedia.url}
                      controls
                      className="w-full h-auto max-h-[70vh]"
                      poster={selectedMedia.thumbnail}
                    >
                      Your browser does not support the video tag.
                    </video>
                  )}
                </div>
              )}
              
              {/* Media info */}
              {(selectedMedia.title || selectedMedia.description) && (
                <div className="p-4 border-t">
                  {selectedMedia.title && (
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                      {selectedMedia.title}
                    </h4>
                  )}
                  {selectedMedia.description && (
                    <p className="text-gray-600 dark:text-gray-300 text-sm">
                      {selectedMedia.description}
                    </p>
                  )}
                  {selectedMedia.source && (
                    <div className="mt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        asChild
                      >
                        <a
                          href={selectedMedia.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center"
                        >
                          <ExternalLink className="h-3 w-3 mr-1" />
                          View Source
                        </a>
                      </Button>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Counter */}
            {media.length > 1 && (
              <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                <Badge variant="outline" className="bg-black/50 border-white/20 text-white">
                  {currentIndex + 1} of {media.length}
                </Badge>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}

export default MediaRail;
