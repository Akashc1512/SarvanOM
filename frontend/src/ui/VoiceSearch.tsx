"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, MicOff, Volume2, Sparkles, AlertCircle } from "lucide-react";
import { Button } from "@/ui/ui/button";
import { cn } from "@/lib/utils";

interface VoiceSearchProps {
  onTranscript: (transcript: string) => void;
  isListening?: boolean;
  className?: string;
  size?: "sm" | "md" | "lg";
}

export function VoiceSearch({ 
  onTranscript, 
  isListening = false, 
  className = "",
  size = "md" 
}: VoiceSearchProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [confidence, setConfidence] = useState(0);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const animationRef = useRef<number | null>(null);

  const sizeClasses = {
    sm: "h-8 w-8",
    md: "h-10 w-10",
    lg: "h-12 w-12"
  };

  const iconSizes = {
    sm: "h-4 w-4",
    md: "h-5 w-5",
    lg: "h-6 w-6"
  };

  useEffect(() => {
    // Check if browser supports SpeechRecognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError("Speech recognition not supported in this browser");
      return;
    }

    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    
    const recognition = recognitionRef.current;
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsRecording(true);
      setError(null);
      setTranscript("");
      setConfidence(0);
      startPulseAnimation();
    };

    recognition.onresult = (event) => {
      let finalTranscript = "";
      let interimTranscript = "";
      let maxConfidence = 0;

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        const confidence = event.results[i][0].confidence;
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
        
        maxConfidence = Math.max(maxConfidence, confidence);
      }

      const fullTranscript = finalTranscript + interimTranscript;
      setTranscript(fullTranscript);
      setConfidence(maxConfidence);
    };

    recognition.onerror = (event) => {
      setIsRecording(false);
      stopPulseAnimation();
      
      switch (event.error) {
        case 'no-speech':
          setError("No speech detected. Please try again.");
          break;
        case 'audio-capture':
          setError("Microphone access denied. Please allow microphone access.");
          break;
        case 'not-allowed':
          setError("Microphone access denied. Please allow microphone access.");
          break;
        case 'network':
          setError("Network error. Please check your connection.");
          break;
        default:
          setError("Speech recognition error. Please try again.");
      }
    };

    recognition.onend = () => {
      setIsRecording(false);
      stopPulseAnimation();
      
      if (transcript.trim()) {
        onTranscript(transcript.trim());
      }
    };

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      stopPulseAnimation();
    };
  }, [onTranscript]);

  const startPulseAnimation = () => {
    const button = document.querySelector('[data-voice-button]') as HTMLElement;
    if (button) {
      button.style.animation = 'pulse 1.5s ease-in-out infinite';
    }
  };

  const stopPulseAnimation = () => {
    const button = document.querySelector('[data-voice-button]') as HTMLElement;
    if (button) {
      button.style.animation = '';
    }
  };

  const toggleRecording = () => {
    if (!recognitionRef.current) return;

    if (isRecording) {
      recognitionRef.current.stop();
    } else {
      try {
        recognitionRef.current.start();
      } catch (error) {
        setError("Failed to start speech recognition");
      }
    }
  };

  const getStatusColor = () => {
    if (error) return "text-red-500 dark:text-red-400";
    if (isRecording) return "text-purple-500 dark:text-purple-400";
    return "text-gray-500 dark:text-gray-400";
  };

  const getButtonVariant = () => {
    if (error) return "destructive";
    if (isRecording) return "default";
    return "outline";
  };

  return (
    <div className={cn("relative", className)}>
      <Button
        variant={getButtonVariant()}
        size={size}
        onClick={toggleRecording}
        disabled={!recognitionRef.current}
        className={cn(
          "relative overflow-hidden transition-all duration-300",
          "bg-gradient-to-r from-purple-500/10 to-blue-500/10",
          "border-purple-200/50 dark:border-purple-800/50",
          "hover:from-purple-500/20 hover:to-blue-500/20",
          "hover:scale-105 active:scale-95",
          "group",
          isRecording && "ring-2 ring-purple-500/50 dark:ring-purple-400/50",
          error && "ring-2 ring-red-500/50 dark:ring-red-400/50"
        )}
        data-voice-button
        aria-label={isRecording ? "Stop voice recording" : "Start voice recording"}
      >
        {/* Cosmic background effect */}
        <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-blue-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* Particle effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1 left-2 w-1 h-1 bg-purple-400/60 rounded-full animate-pulse" />
          <div className="absolute top-3 right-1 w-0.5 h-0.5 bg-blue-400/60 rounded-full animate-pulse delay-100" />
          <div className="absolute bottom-2 left-3 w-0.5 h-0.5 bg-purple-300/60 rounded-full animate-pulse delay-200" />
        </div>

        {/* Icon */}
        <div className="relative z-10 transition-transform duration-300 group-hover:rotate-12">
          {error ? (
            <AlertCircle className={cn(iconSizes[size], "text-red-500 dark:text-red-400")} />
          ) : isRecording ? (
            <MicOff className={cn(iconSizes[size], "text-purple-600 dark:text-purple-400")} />
          ) : (
            <Mic className={cn(iconSizes[size], getStatusColor())} />
          )}
        </div>

        {/* Recording indicator */}
        {isRecording && (
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
        )}

        {/* Sparkles effect on hover */}
        <Sparkles className="absolute -top-1 -right-1 h-3 w-3 text-purple-400 opacity-0 group-hover:opacity-100 transition-all duration-300 group-hover:animate-pulse" />
      </Button>

      {/* Confidence indicator */}
      {isRecording && confidence > 0 && (
        <div className="absolute -bottom-8 left-1/2 transform -translate-x-1/2">
          <div className="flex items-center space-x-1 bg-white/90 dark:bg-slate-800/90 backdrop-blur-sm rounded-full px-2 py-1 shadow-lg">
            <Volume2 className="h-3 w-3 text-purple-500 dark:text-purple-400" />
            <div className="w-12 h-1 bg-gray-200 dark:bg-slate-700 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full transition-all duration-300"
                style={{ width: `${confidence * 100}%` }}
              />
            </div>
            <span className="text-xs text-gray-600 dark:text-gray-300">
              {Math.round(confidence * 100)}%
            </span>
          </div>
        </div>
      )}

      {/* Error tooltip */}
      {error && (
        <div className="absolute -bottom-12 left-1/2 transform -translate-x-1/2 z-50">
          <div className="bg-red-500 dark:bg-red-600 text-white text-xs px-2 py-1 rounded shadow-lg whitespace-nowrap">
            {error}
          </div>
          <div className="absolute top-0 left-1/2 transform -translate-x-1/2 -translate-y-1 w-0 h-0 border-l-4 border-r-4 border-b-4 border-transparent border-b-red-500 dark:border-b-red-600" />
        </div>
      )}

      {/* Live transcript preview */}
      {isRecording && transcript && (
        <div className="absolute -bottom-16 left-0 right-0 z-40">
          <div className="bg-white/95 dark:bg-slate-800/95 backdrop-blur-sm rounded-lg p-3 shadow-xl border border-purple-200/50 dark:border-purple-800/50">
            <div className="flex items-center space-x-2 mb-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-gray-700 dark:text-gray-300">
                Live transcript
              </span>
            </div>
            <p className="text-sm text-gray-900 dark:text-white">
              "{transcript}"
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export function useVoiceSearch() {
  const [isSupported, setIsSupported] = useState(false);

  useEffect(() => {
    setIsSupported(
      'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
    );
  }, []);

  return { isSupported };
}
