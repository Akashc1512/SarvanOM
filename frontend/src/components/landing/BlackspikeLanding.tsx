"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
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
  ShieldCheckIcon
} from "@heroicons/react/24/outline";
import { SearchInput } from "@/components/features/SearchInput";

export default function BlackspikeLanding() {
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);

  const features = [
    {
      icon: SparklesIcon,
      title: "AI-Powered Search",
      description: "Advanced artificial intelligence that understands context and provides intelligent responses",
      color: "from-blue-500 to-cyan-500"
    },
    {
      icon: CpuChipIcon,
      title: "Real-time Streaming",
      description: "Get instant, streaming responses as AI generates answers in real-time",
      color: "from-purple-500 to-pink-500"
    },
    {
      icon: GlobeAltIcon,
      title: "Multi-Source Retrieval",
      description: "Search across documents, web, and knowledge graphs simultaneously",
      color: "from-green-500 to-emerald-500"
    },
    {
      icon: ShieldCheckIcon,
      title: "Enterprise Security",
      description: "Bank-grade security with end-to-end encryption and compliance",
      color: "from-orange-500 to-red-500"
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

  const stats = [
    { label: "Active Users", value: "10K+", icon: UsersIcon },
    { label: "Searches Processed", value: "1M+", icon: ChatBubbleLeftRightIcon },
    { label: "AI Responses", value: "500K+", icon: SparklesIcon },
    { label: "Uptime", value: "99.9%", icon: ShieldCheckIcon }
  ];

  const pricingPlans = [
    {
      name: "Starter",
      price: "Free",
      description: "Perfect for individuals and small teams",
      features: [
        "1,000 searches/month",
        "Basic AI responses",
        "Standard support",
        "Community access"
      ],
      cta: "Get Started",
      popular: false
    },
    {
      name: "Professional",
      price: "$29",
      period: "/month",
      description: "Ideal for growing businesses",
      features: [
        "10,000 searches/month",
        "Advanced AI responses",
        "Priority support",
        "API access",
        "Custom integrations"
      ],
      cta: "Start Free Trial",
      popular: true
    },
    {
      name: "Enterprise",
      price: "Custom",
      description: "For large organizations",
      features: [
        "Unlimited searches",
        "Premium AI models",
        "24/7 dedicated support",
        "Custom deployment",
        "Advanced analytics",
        "SLA guarantee"
      ],
      cta: "Contact Sales",
      popular: false
    }
  ];

  return (
    <div className="min-h-screen cosmic-bg-primary">
      {/* Navigation */}
      <nav className="relative z-50 p-6">
        <div className="cosmic-container flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-2"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold cosmic-text-primary">SarvanOM</span>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="hidden md:flex items-center gap-8"
          >
            <a href="#features" className="cosmic-text-secondary hover:cosmic-text-primary transition-colors">Features</a>
            <a href="#pricing" className="cosmic-text-secondary hover:cosmic-text-primary transition-colors">Pricing</a>
            <a href="#testimonials" className="cosmic-text-secondary hover:cosmic-text-primary transition-colors">Testimonials</a>
            <button className="cosmic-btn-primary">
              Get Started
            </button>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden cosmic-section">
        <div className="absolute inset-0 bg-gradient-to-r from-cosmic-primary-500/20 to-cosmic-secondary-500/20 blur-3xl" />
        <div className="relative cosmic-container py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Hero Left */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
                <RocketLaunchIcon className="w-4 h-4" />
                Next-Generation AI Platform
              </div>
              <h1 className="text-5xl lg:text-6xl font-bold cosmic-text-primary mb-6">
                Unlock Universal
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500">
                  Knowledge
                </span>
              </h1>
              <p className="text-xl cosmic-text-secondary mb-8 leading-relaxed">
                Experience AI-powered search that understands context, provides real-time streaming responses, 
                and delivers intelligent insights across multiple sources.
              </p>
              
              {/* Search Demo */}
              <div className="mb-8">
                <SearchInput 
                  placeholder="Try asking: What are the latest developments in AI?"
                  className="w-full"
                />
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <button className="cosmic-btn-primary flex items-center gap-2 text-lg font-medium">
                  Start Free Trial
                  <ArrowRightIcon className="w-5 h-5" />
                </button>
                <button 
                  onClick={() => setIsVideoPlaying(!isVideoPlaying)}
                  className="cosmic-btn-secondary flex items-center gap-2 text-lg font-medium"
                >
                  <PlayIcon className="w-5 h-5" />
                  Try Demo
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="mt-8 flex items-center gap-6 cosmic-text-tertiary text-sm">
                <div className="flex items-center gap-1">
                  <ShieldCheckIcon className="w-4 h-4" />
                  <span>Enterprise Security</span>
                </div>
                <div className="flex items-center gap-1">
                  <CpuChipIcon className="w-4 h-4" />
                  <span>99.9% Uptime</span>
                </div>
                <div className="flex items-center gap-1">
                  <UsersIcon className="w-4 h-4" />
                  <span>10K+ Users</span>
                </div>
              </div>
            </motion.div>

            {/* Mock Tile Right */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="cosmic-card backdrop-blur-sm border border-cosmic-border-primary rounded-3xl p-8">
                <div className="aspect-video bg-gradient-to-br from-cosmic-primary-500/20 to-cosmic-secondary-500/20 rounded-2xl flex items-center justify-center mb-6">
                  {isVideoPlaying ? (
                    <div className="text-center">
                      <div className="w-16 h-16 bg-cosmic-bg-secondary rounded-full flex items-center justify-center mx-auto mb-4">
                        <PlayIcon className="w-8 h-8 cosmic-text-primary ml-1" />
                      </div>
                      <p className="cosmic-text-primary text-sm">Demo Video Playing</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <div className="w-20 h-20 bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 rounded-full flex items-center justify-center mx-auto mb-4">
                        <SparklesIcon className="w-10 h-10 text-white" />
                      </div>
                      <p className="cosmic-text-primary text-lg font-medium">AI Search in Action</p>
                    </div>
                  )}
                </div>
                
                {/* KPI Row */}
                <div className="grid grid-cols-2 gap-4">
                  {stats.map((stat, index) => (
                    <div key={stat.label} className="text-center p-4 cosmic-bg-secondary rounded-lg">
                      <stat.icon className="w-6 h-6 text-cosmic-primary-500 mx-auto mb-2" />
                      <div className="text-2xl font-bold cosmic-text-primary">{stat.value}</div>
                      <div className="cosmic-text-secondary text-sm">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="cosmic-section">
        <div className="cosmic-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold cosmic-text-primary mb-4">Powerful Features</h2>
            <p className="text-xl cosmic-text-secondary max-w-2xl mx-auto">
              Everything you need to revolutionize your knowledge discovery and research workflow
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="group relative"
              >
                <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-20 transition-opacity duration-300 rounded-2xl blur-xl"
                     style={{ backgroundImage: `linear-gradient(to right, ${feature.color})` }} />
                <div className="relative cosmic-card backdrop-blur-sm border border-cosmic-border-primary rounded-2xl p-6 hover:cosmic-hover-lift transition-all duration-300">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${feature.color} mb-4`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold cosmic-text-primary mb-2">{feature.title}</h3>
                  <p className="cosmic-text-secondary text-sm leading-relaxed">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="cosmic-section">
        <div className="cosmic-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold cosmic-text-primary mb-4">What Our Users Say</h2>
            <p className="text-xl cosmic-text-secondary">Trusted by researchers, developers, and organizations worldwide</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="cosmic-card backdrop-blur-sm border border-cosmic-border-primary rounded-2xl p-6"
              >
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <StarIcon key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="cosmic-text-secondary mb-6 leading-relaxed">"{testimonial.content}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 rounded-full flex items-center justify-center text-white font-medium">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="cosmic-text-primary font-medium">{testimonial.name}</div>
                    <div className="cosmic-text-tertiary text-sm">{testimonial.role} at {testimonial.company}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="cosmic-section">
        <div className="cosmic-container">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold cosmic-text-primary mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl cosmic-text-secondary">Choose the plan that fits your needs</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`relative cosmic-card backdrop-blur-sm border rounded-2xl p-8 ${
                  plan.popular 
                    ? "border-cosmic-primary-500/50" 
                    : "border-cosmic-border-primary"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold cosmic-text-primary mb-2">{plan.name}</h3>
                  <div className="text-4xl font-bold cosmic-text-primary mb-2">
                    {plan.price}
                    {plan.period && <span className="text-lg cosmic-text-secondary">{plan.period}</span>}
                  </div>
                  <p className="cosmic-text-secondary">{plan.description}</p>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center gap-3">
                      <CheckIcon className="w-5 h-5 text-cosmic-success flex-shrink-0" />
                      <span className="cosmic-text-secondary">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button className={`w-full py-3 rounded-lg font-medium transition-all duration-300 ${
                  plan.popular
                    ? "cosmic-btn-primary"
                    : "cosmic-btn-secondary"
                }`}>
                  {plan.cta}
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cosmic-section">
        <div className="cosmic-container text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="cosmic-card backdrop-blur-sm border border-cosmic-border-primary rounded-3xl p-12"
          >
            <h2 className="text-4xl font-bold cosmic-text-primary mb-4">Ready to Transform Your Search?</h2>
            <p className="text-xl cosmic-text-secondary mb-8">
              Join thousands of users who are already experiencing the future of AI-powered knowledge discovery
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="cosmic-btn-primary flex items-center gap-2 text-lg font-medium">
                Start Free Trial
                <ArrowRightIcon className="w-5 h-5" />
              </button>
              <button className="cosmic-btn-secondary flex items-center gap-2 text-lg font-medium">
                <ChatBubbleLeftRightIcon className="w-5 h-5" />
                Talk to Sales
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-cosmic-border-primary">
        <div className="cosmic-container">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-cosmic-primary-500 to-cosmic-secondary-500 rounded-lg flex items-center justify-center">
                  <SparklesIcon className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold cosmic-text-primary">SarvanOM</span>
              </div>
              <p className="cosmic-text-secondary text-sm">
                The future of AI-powered knowledge discovery and search technology.
              </p>
            </div>
            
            <div>
              <h4 className="cosmic-text-primary font-semibold mb-4">Product</h4>
              <ul className="space-y-2 cosmic-text-secondary text-sm">
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Features</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">API</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Documentation</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="cosmic-text-primary font-semibold mb-4">Company</h4>
              <ul className="space-y-2 cosmic-text-secondary text-sm">
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">About</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Blog</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Careers</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="cosmic-text-primary font-semibold mb-4">Support</h4>
              <ul className="space-y-2 cosmic-text-secondary text-sm">
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Community</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Status</a></li>
                <li><a href="#" className="hover:cosmic-text-primary transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-cosmic-border-primary mt-8 pt-8 text-center cosmic-text-secondary text-sm">
            <p>&copy; 2024 SarvanOM. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
