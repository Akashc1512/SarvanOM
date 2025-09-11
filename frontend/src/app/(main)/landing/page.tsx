"use client";

import React from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { 
  RocketLaunchIcon,
  SparklesIcon,
  CpuChipIcon,
  GlobeAltIcon,
  CheckIcon,
  ArrowRightIcon,
  PlayIcon,
  StarIcon,
  UsersIcon,
  ChatBubbleLeftRightIcon,
  CodeBracketIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  ClockIcon,
  CurrencyDollarIcon
} from "@heroicons/react/24/outline";
import { Button } from "@/ui/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { MetricTile } from "@/ui/ui/metric-tile";
import { Badge } from "@/ui/ui/badge";

export default function LandingPage() {
  const features = [
    {
      icon: SparklesIcon,
      title: "AI-Powered Search",
      description: "Advanced artificial intelligence that understands context and provides intelligent responses",
      color: "cosmic-primary-500"
    },
    {
      icon: CpuChipIcon,
      title: "Real-time Streaming",
      description: "Get instant, streaming responses as AI generates answers in real-time",
      color: "cosmic-secondary-500"
    },
    {
      icon: GlobeAltIcon,
      title: "Multi-Source Retrieval",
      description: "Search across documents, web, and knowledge graphs simultaneously",
      color: "cosmic-success"
    },
    {
      icon: ShieldCheckIcon,
      title: "Enterprise Security",
      description: "Bank-grade security with end-to-end encryption and compliance",
      color: "cosmic-warning"
    },
    {
      icon: ChartBarIcon,
      title: "Analytics Dashboard",
      description: "Comprehensive insights into your search patterns and knowledge discovery",
      color: "cosmic-info"
    },
    {
      icon: CodeBracketIcon,
      title: "Developer API",
      description: "Integrate SarvanOM's capabilities into your own applications",
      color: "cosmic-primary-600"
    }
  ];

  const testimonials = [
    {
      name: "Sarah Chen",
      role: "AI Researcher",
      company: "TechCorp",
      content: "SarvanOM has revolutionized how we approach knowledge discovery. The real-time streaming and multi-source search capabilities are game-changing.",
      rating: 5,
      avatar: "SC"
    },
    {
      name: "Michael Rodriguez",
      role: "CTO",
      company: "InnovateLab",
      content: "The platform's ability to understand context and provide intelligent responses has significantly improved our research efficiency.",
      rating: 5,
      avatar: "MR"
    },
    {
      name: "Dr. Emily Watson",
      role: "Data Scientist",
      company: "QuantumAI",
      content: "Finally, a search platform that thinks like a human. The AI-powered insights have transformed our data analysis workflow.",
      rating: 5,
      avatar: "EW"
    }
  ];

  return (
    <div className="min-h-screen cosmic-bg-primary">
      {/* Hero Section */}
      <section className="cosmic-section">
        <div className="cosmic-container">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              className="space-y-8"
            >
              <div className="space-y-4">
                <Badge variant="outline" className="cosmic-border-accent">
                  <SparklesIcon className="w-4 h-4 mr-2" />
                  AI-Powered Knowledge Platform
                </Badge>
                <h1 className="text-5xl lg:text-6xl font-bold cosmic-text-primary leading-tight">
                  Unlock Universal
                  <span className="cosmic-text-gradient"> Knowledge</span>
                </h1>
                <p className="text-xl cosmic-text-secondary leading-relaxed">
                  Evidence-first answers across your web, docs, and data — in seconds. 
                  Powered by advanced AI with real-time streaming and comprehensive citations.
                </p>
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Button asChild size="lg" className="cosmic-btn-primary">
                  <Link href="/search">
                    <RocketLaunchIcon className="w-5 h-5 mr-2" />
                    Get Started
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="cosmic-btn-secondary">
                  <Link href="/comprehensive-query">
                    <PlayIcon className="w-5 h-5 mr-2" />
                    Try the Demo
                  </Link>
                </Button>
              </div>

              <div className="flex items-center gap-6 text-sm cosmic-text-tertiary">
                <div className="flex items-center gap-2">
                  <CheckIcon className="w-4 h-4 text-cosmic-success" />
                  <span>Free to start</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckIcon className="w-4 h-4 text-cosmic-success" />
                  <span>No credit card required</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckIcon className="w-4 h-4 text-cosmic-success" />
                  <span>Enterprise ready</span>
                </div>
              </div>
            </motion.div>

            {/* Right Content - Mock Dashboard */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="relative"
            >
              <Card className="cosmic-card-glass p-6">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <ChartBarIcon className="w-5 h-5 text-cosmic-primary-500" />
                    Live Dashboard
                  </CardTitle>
                  <CardDescription>
                    Real-time insights from your knowledge platform
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <MetricTile
                      label="Operations/sec"
                      value="1,247"
                      delta="+12.5%"
                      deltaType="increase"
                      tone="success"
                      size="sm"
                    />
                    <MetricTile
                      label="Avg Latency"
                      value="1.2s"
                      delta="-8.3%"
                      deltaType="increase"
                      tone="primary"
                      size="sm"
                    />
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="cosmic-text-secondary">Active Searches</span>
                      <span className="cosmic-text-primary font-medium">23</span>
                    </div>
                    <div className="w-full bg-cosmic-bg-tertiary rounded-full h-2">
                      <div className="bg-cosmic-primary-500 h-2 rounded-full w-3/4"></div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          </div>
        </div>
      </section>

      {/* KPI Row */}
      <section className="cosmic-section bg-cosmic-bg-secondary/50">
        <div className="cosmic-container">
          <div className="grid md:grid-cols-3 gap-6">
            <MetricTile
              label="Operations/sec"
              value="1,247"
              delta="+12.5%"
              deltaType="increase"
              tone="success"
              icon={<CpuChipIcon className="w-5 h-5" />}
            />
            <MetricTile
              label="Avg Latency"
              value="1.2s"
              delta="-8.3%"
              deltaType="increase"
              tone="primary"
              icon={<ClockIcon className="w-5 h-5" />}
            />
            <MetricTile
              label="Cost/Query"
              value="$0.003"
              delta="-15.2%"
              deltaType="increase"
              tone="warning"
              icon={<CurrencyDollarIcon className="w-5 h-5" />}
            />
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="cosmic-section">
        <div className="cosmic-container">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold cosmic-text-primary">
              Powerful Features for Modern Knowledge Discovery
            </h2>
            <p className="text-xl cosmic-text-secondary max-w-3xl mx-auto">
              Everything you need to unlock insights from your data, documents, and the web
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="cosmic-card h-full hover:cosmic-card-elevated transition-all duration-300">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className={`w-12 h-12 rounded-lg bg-${feature.color}/10 flex items-center justify-center`}>
                        <feature.icon className={`w-6 h-6 text-${feature.color}`} />
                      </div>
                      <div>
                        <h3 className="text-xl font-semibold cosmic-text-primary mb-2">
                          {feature.title}
                        </h3>
                        <p className="cosmic-text-secondary">
                          {feature.description}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="cosmic-section bg-cosmic-bg-secondary/50">
        <div className="cosmic-container">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-4xl font-bold cosmic-text-primary">
              Trusted by Leading Organizations
            </h2>
            <p className="text-xl cosmic-text-secondary">
              See what our users are saying about SarvanOM
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
              >
                <Card className="cosmic-card h-full">
                  <CardContent className="p-6">
                    <div className="space-y-4">
                      <div className="flex items-center gap-1">
                        {[...Array(testimonial.rating)].map((_, i) => (
                          <StarIcon key={i} className="w-5 h-5 text-cosmic-warning fill-current" />
                        ))}
                      </div>
                      <p className="cosmic-text-secondary italic">
                        "{testimonial.content}"
                      </p>
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-cosmic-primary-500 rounded-full flex items-center justify-center text-white font-semibold">
                          {testimonial.avatar}
                        </div>
                        <div>
                          <div className="font-semibold cosmic-text-primary">
                            {testimonial.name}
                          </div>
                          <div className="text-sm cosmic-text-tertiary">
                            {testimonial.role} at {testimonial.company}
                          </div>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cosmic-section">
        <div className="cosmic-container">
          <Card className="cosmic-card-glass text-center p-12">
            <CardContent className="space-y-8">
              <div className="space-y-4">
                <h2 className="text-4xl font-bold cosmic-text-primary">
                  Ready to Transform Your Knowledge Discovery?
                </h2>
                <p className="text-xl cosmic-text-secondary max-w-2xl mx-auto">
                  Join thousands of researchers, analysts, and knowledge workers who trust SarvanOM for their most important queries.
                </p>
              </div>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button asChild size="lg" className="cosmic-btn-primary">
                  <Link href="/search">
                    <RocketLaunchIcon className="w-5 h-5 mr-2" />
                    Start Searching Now
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="cosmic-btn-secondary">
                  <Link href="/analytics">
                    <ChartBarIcon className="w-5 h-5 mr-2" />
                    View Analytics
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>
    </div>
  );
}
