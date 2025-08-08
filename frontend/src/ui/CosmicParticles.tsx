"use client";

import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  size: number;
  opacity: number;
  color: string;
  life: number;
  maxLife: number;
}

interface CosmicParticlesProps {
  className?: string;
  particleCount?: number;
  speed?: number;
  size?: "sm" | "md" | "lg";
  theme?: "purple" | "blue" | "mixed";
  interactive?: boolean;
}

export function CosmicParticles({
  className = "",
  particleCount = 50,
  speed = 1,
  size = "md",
  theme = "mixed",
  interactive = true
}: CosmicParticlesProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const particlesRef = useRef<Particle[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  const sizeConfig = {
    sm: { minSize: 1, maxSize: 3, speed: 0.5 },
    md: { minSize: 2, maxSize: 4, speed: 1 },
    lg: { minSize: 3, maxSize: 6, speed: 1.5 }
  };

  const themeColors = {
    purple: ["#8b5cf6", "#a855f7", "#c084fc", "#ddd6fe"],
    blue: ["#3b82f6", "#60a5fa", "#93c5fd", "#dbeafe"],
    mixed: ["#8b5cf6", "#3b82f6", "#a855f7", "#60a5fa", "#c084fc", "#93c5fd"]
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Set canvas size
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * window.devicePixelRatio;
      canvas.height = rect.height * window.devicePixelRatio;
      ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Initialize particles
    const initParticles = () => {
      particlesRef.current = [];
      const colors = themeColors[theme];
      
      for (let i = 0; i < particleCount; i++) {
        particlesRef.current.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * sizeConfig[size].speed * speed,
          vy: (Math.random() - 0.5) * sizeConfig[size].speed * speed,
          size: Math.random() * (sizeConfig[size].maxSize - sizeConfig[size].minSize) + sizeConfig[size].minSize,
          opacity: Math.random() * 0.8 + 0.2,
          color: colors[Math.floor(Math.random() * colors.length)],
          life: Math.random() * 100,
          maxLife: 100
        });
      }
    };

    initParticles();

    // Animation loop
    const animate = () => {
      if (!ctx || !canvas) return;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particlesRef.current.forEach((particle, index) => {
        // Update position
        particle.x += particle.vx;
        particle.y += particle.vy;

        // Wrap around edges
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;

        // Update life
        particle.life -= 0.5;
        if (particle.life <= 0) {
          particle.life = particle.maxLife;
          particle.x = Math.random() * canvas.width;
          particle.y = Math.random() * canvas.height;
        }

        // Draw particle
        const alpha = (particle.life / particle.maxLife) * particle.opacity;
        ctx.globalAlpha = alpha;
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();

        // Draw glow effect
        const gradient = ctx.createRadialGradient(
          particle.x, particle.y, 0,
          particle.x, particle.y, particle.size * 3
        );
        gradient.addColorStop(0, `${particle.color}40`);
        gradient.addColorStop(1, "transparent");
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size * 3, 0, Math.PI * 2);
        ctx.fill();
      });

      // Draw connections between nearby particles
      if (interactive) {
        ctx.globalAlpha = 0.3;
        ctx.strokeStyle = "#8b5cf6";
        ctx.lineWidth = 0.5;

        for (let i = 0; i < particlesRef.current.length; i++) {
          for (let j = i + 1; j < particlesRef.current.length; j++) {
            const p1 = particlesRef.current[i];
            const p2 = particlesRef.current[j];
            const distance = Math.sqrt(
              Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2)
            );

            if (distance < 100) {
              const opacity = (100 - distance) / 100;
              ctx.globalAlpha = opacity * 0.3;
              ctx.beginPath();
              ctx.moveTo(p1.x, p1.y);
              ctx.lineTo(p2.x, p2.y);
              ctx.stroke();
            }
          }
        }
      }

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    // Mouse interaction
    let mouseX = 0;
    let mouseY = 0;
    let isMouseDown = false;

    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive) return;
      
      const rect = canvas.getBoundingClientRect();
      mouseX = e.clientX - rect.left;
      mouseY = e.clientY - rect.top;

      // Attract particles to mouse
      particlesRef.current.forEach(particle => {
        const dx = mouseX - particle.x;
        const dy = mouseY - particle.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        if (distance < 150) {
          const force = (150 - distance) / 150;
          particle.vx += (dx / distance) * force * 0.1;
          particle.vy += (dy / distance) * force * 0.1;
        }
      });
    };

    const handleMouseDown = () => {
      isMouseDown = true;
    };

    const handleMouseUp = () => {
      isMouseDown = false;
    };

    if (interactive) {
      canvas.addEventListener("mousemove", handleMouseMove);
      canvas.addEventListener("mousedown", handleMouseDown);
      canvas.addEventListener("mouseup", handleMouseUp);
    }

    // Intersection Observer for performance
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          setIsVisible(entry.isIntersecting);
        });
      },
      { threshold: 0.1 }
    );

    observer.observe(canvas);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      window.removeEventListener("resize", resizeCanvas);
      if (interactive) {
        canvas.removeEventListener("mousemove", handleMouseMove);
        canvas.removeEventListener("mousedown", handleMouseDown);
        canvas.removeEventListener("mouseup", handleMouseUp);
      }
      observer.disconnect();
    };
  }, [particleCount, speed, size, theme, interactive]);

  return (
    <canvas
      ref={canvasRef}
      className={cn(
        "absolute inset-0 pointer-events-none",
        className
      )}
      style={{
        pointerEvents: interactive ? "auto" : "none"
      }}
    />
  );
}

export function StarField({ className = "" }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 overflow-hidden", className)}>
      <CosmicParticles
        particleCount={30}
        speed={0.5}
        size="sm"
        theme="purple"
        interactive={false}
      />
    </div>
  );
}

export function NebulaEffect({ className = "" }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 overflow-hidden", className)}>
      <CosmicParticles
        particleCount={80}
        speed={0.3}
        size="lg"
        theme="mixed"
        interactive={true}
      />
    </div>
  );
}

export function ConstellationEffect({ className = "" }: { className?: string }) {
  return (
    <div className={cn("absolute inset-0 overflow-hidden", className)}>
      <CosmicParticles
        particleCount={20}
        speed={0.2}
        size="md"
        theme="blue"
        interactive={true}
      />
    </div>
  );
}
