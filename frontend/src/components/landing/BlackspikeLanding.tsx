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

export function BlackspikeLanding() {
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
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="relative z-50 p-6">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="flex items-center gap-2"
          >
            <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-white">SarvanOM</span>
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6 }}
            className="hidden md:flex items-center gap-8"
          >
            <a href="#features" className="text-gray-300 hover:text-white transition-colors">Features</a>
            <a href="#pricing" className="text-gray-300 hover:text-white transition-colors">Pricing</a>
            <a href="#testimonials" className="text-gray-300 hover:text-white transition-colors">Testimonials</a>
            <button className="px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300">
              Get Started
            </button>
          </motion.div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/20 to-purple-600/20 blur-3xl" />
        <div className="relative max-w-7xl mx-auto px-6 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium mb-6">
                <RocketLaunchIcon className="w-4 h-4" />
                Next-Generation AI Platform
              </div>
              <h1 className="text-5xl lg:text-6xl font-bold text-white mb-6">
                The Future of
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
                  Knowledge Search
                </span>
              </h1>
              <p className="text-xl text-gray-300 mb-8 leading-relaxed">
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
                <button className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center gap-2 text-lg font-medium">
                  Start Free Trial
                  <ArrowRightIcon className="w-5 h-5" />
                </button>
                <button 
                  onClick={() => setIsVideoPlaying(!isVideoPlaying)}
                  className="px-8 py-4 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all duration-300 flex items-center gap-2 text-lg font-medium"
                >
                  <PlayIcon className="w-5 h-5" />
                  Watch Demo
                </button>
              </div>

              {/* Trust Indicators */}
              <div className="mt-8 flex items-center gap-6 text-gray-400 text-sm">
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

            {/* Hero Visual */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-3xl p-8">
                <div className="aspect-video bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-2xl flex items-center justify-center mb-6">
                  {isVideoPlaying ? (
                    <div className="text-center">
                      <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                        <PlayIcon className="w-8 h-8 text-white ml-1" />
                      </div>
                      <p className="text-white text-sm">Demo Video Playing</p>
                    </div>
                  ) : (
                    <div className="text-center">
                      <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <SparklesIcon className="w-10 h-10 text-white" />
                      </div>
                      <p className="text-white text-lg font-medium">AI Search in Action</p>
                    </div>
                  )}
                </div>
                
                {/* Live Stats */}
                <div className="grid grid-cols-2 gap-4">
                  {stats.map((stat, index) => (
                    <div key={stat.label} className="text-center p-4 bg-white/5 rounded-lg">
                      <stat.icon className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                      <div className="text-2xl font-bold text-white">{stat.value}</div>
                      <div className="text-gray-400 text-sm">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-white mb-4">Powerful Features</h2>
            <p className="text-xl text-gray-300 max-w-2xl mx-auto">
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
                <div className="relative backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all duration-300">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-r ${feature.color} mb-4`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{feature.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-white mb-4">What Our Users Say</h2>
            <p className="text-xl text-gray-300">Trusted by researchers, developers, and organizations worldwide</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-2xl p-6"
              >
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <StarIcon key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                  ))}
                </div>
                <p className="text-gray-300 mb-6 leading-relaxed">"{testimonial.content}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-medium">
                    {testimonial.avatar}
                  </div>
                  <div>
                    <div className="text-white font-medium">{testimonial.name}</div>
                    <div className="text-gray-400 text-sm">{testimonial.role} at {testimonial.company}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-white mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-gray-300">Choose the plan that fits your needs</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className={`relative backdrop-blur-sm border rounded-2xl p-8 ${
                  plan.popular 
                    ? "bg-white/10 border-blue-500/50" 
                    : "bg-white/5 border-white/10"
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-white mb-2">{plan.name}</h3>
                  <div className="text-4xl font-bold text-white mb-2">
                    {plan.price}
                    {plan.period && <span className="text-lg text-gray-400">{plan.period}</span>}
                  </div>
                  <p className="text-gray-400">{plan.description}</p>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center gap-3">
                      <CheckIcon className="w-5 h-5 text-green-400 flex-shrink-0" />
                      <span className="text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button className={`w-full py-3 rounded-lg font-medium transition-all duration-300 ${
                  plan.popular
                    ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700"
                    : "bg-white/10 text-white hover:bg-white/20"
                }`}>
                  {plan.cta}
                </button>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="backdrop-blur-sm bg-white/5 border border-white/10 rounded-3xl p-12"
          >
            <h2 className="text-4xl font-bold text-white mb-4">Ready to Transform Your Search?</h2>
            <p className="text-xl text-gray-300 mb-8">
              Join thousands of users who are already experiencing the future of AI-powered knowledge discovery
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 flex items-center gap-2 text-lg font-medium">
                Start Free Trial
                <ArrowRightIcon className="w-5 h-5" />
              </button>
              <button className="px-8 py-4 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all duration-300 flex items-center gap-2 text-lg font-medium">
                <ChatBubbleLeftRightIcon className="w-5 h-5" />
                Talk to Sales
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-white/10">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <SparklesIcon className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold text-white">SarvanOM</span>
              </div>
              <p className="text-gray-400 text-sm">
                The future of AI-powered knowledge discovery and search technology.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Documentation</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li><a href="#" className="hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Community</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-white/10 mt-8 pt-8 text-center text-gray-400 text-sm">
            <p>&copy; 2024 SarvanOM. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
