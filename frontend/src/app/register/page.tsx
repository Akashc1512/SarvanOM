"use client";

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/ui/ui/button";
import { Input } from "@/ui/ui/input";
import { Card, CardContent } from "@/ui/ui/card";
import { Label } from "@/ui/ui/label";
import { Alert, AlertDescription } from "@/ui/ui/alert";
import { LoadingSpinner } from "@/ui/atoms/loading-spinner";
import { Eye, EyeOff, AlertCircle, User, Lock, Mail, Sparkles, CheckCircle } from "lucide-react";
import { motion } from "framer-motion";

export default function RegisterPage() {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirmPassword: "",
    agreeToTerms: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { register, isAuthenticated, isLoading, error } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      const redirect = searchParams.get("redirect") || "/dashboard";
      router.push(redirect);
    }
  }, [isAuthenticated, isLoading, router, searchParams]);

  // Validate form
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.username.trim()) {
      newErrors["username"] = "Username is required";
    } else if (formData.username.length < 3) {
      newErrors["username"] = "Username must be at least 3 characters";
    }

    if (!formData.email.trim()) {
      newErrors["email"] = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors["email"] = "Please enter a valid email address";
    }

    if (!formData.password) {
      newErrors["password"] = "Password is required";
    } else if (formData.password.length < 8) {
      newErrors["password"] = "Password must be at least 8 characters";
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      newErrors["password"] = "Password must contain uppercase, lowercase, and number";
    }

    if (!formData.confirmPassword) {
      newErrors["confirmPassword"] = "Please confirm your password";
    } else if (formData.password !== formData.confirmPassword) {
      newErrors["confirmPassword"] = "Passwords do not match";
    }

    if (!formData.agreeToTerms) {
      newErrors["agreeToTerms"] = "You must agree to the terms and conditions";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    setErrors({});

    try {
      await register({
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password,
      });

      // Redirect will be handled by useEffect
    } catch (error) {
      console.error("Registration failed:", error);
      setErrors({
        general: error instanceof Error ? error.message : "Registration failed. Please try again.",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle input changes
  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: "" }));
    }
  };

  // Show loading state while auth is initializing
  if (isLoading) {
    return (
      <div className="min-h-screen cosmic-bg-primary flex items-center justify-center">
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-6"
        >
          <LoadingSpinner size="lg" />
          <p className="text-lg cosmic-text-secondary">Initializing SarvanOM...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen cosmic-bg-primary relative overflow-hidden">
      {/* Starfield Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div 
          className="absolute inset-0 opacity-30 animate-starfield cosmic-starfield"
          style={{
            background: `
              radial-gradient(1px 1px at 20% 30%, rgba(59, 130, 246, 0.4) 0, transparent 40%),
              radial-gradient(1px 1px at 80% 20%, rgba(168, 85, 247, 0.3) 0, transparent 40%),
              radial-gradient(1px 1px at 40% 70%, rgba(59, 130, 246, 0.2) 0, transparent 40%),
              radial-gradient(1px 1px at 90% 90%, rgba(168, 85, 247, 0.3) 0, transparent 40%)
            `,
            backgroundSize: '200px 200px, 300px 300px, 150px 150px, 250px 250px'
          }}
        />
      </div>

      <div className="relative z-10 flex items-center justify-center min-h-screen p-6 sm:p-8">
        <div className="w-full max-w-md">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {/* Header */}
            <div className="text-center mb-8">
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="flex items-center justify-center mb-6"
              >
                <div className="relative">
                  <Sparkles className="w-12 h-12 text-[#3b82f6]" />
                  <div className="absolute -top-2 -right-2 w-4 h-4 bg-[#3b82f6] rounded-full animate-pulse" />
                </div>
              </motion.div>
              
              <motion.h1
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="text-4xl font-bold text-[#e2e8f0] mb-3"
              >
                Join SarvanOM
              </motion.h1>
              
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-lg text-[#e2e8f0]/70"
              >
                Create your account and start exploring knowledge
              </motion.p>
            </div>

            {/* Register Form */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card className="bg-[#1a2332]/50 backdrop-blur-sm border border-[#3b82f6]/20 rounded-2xl shadow-xl">
                <CardContent className="p-8">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Error Alert */}
                    {(errors["general"] || error) && (
                      <motion.div
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                      >
                        <Alert variant="destructive" className="bg-red-500/10 border-red-500/20 text-red-400">
                          <AlertCircle className="h-5 w-5" />
                          <AlertDescription>
                            {errors["general"] || error}
                          </AlertDescription>
                        </Alert>
                      </motion.div>
                    )}

                    {/* Username Field */}
                    <div className="space-y-3">
                      <Label htmlFor="username" className="text-[#e2e8f0] font-medium">
                        Username
                      </Label>
                      <div className="relative">
                        <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#e2e8f0]/50" />
                        <Input
                          id="username"
                          type="text"
                          placeholder="Choose a username"
                          value={formData.username}
                          onChange={(e) => handleInputChange("username", e.target.value)}
                          className={`pl-12 pr-4 py-4 bg-[#1a2332]/30 border-[#3b82f6]/20 text-[#e2e8f0] placeholder:text-[#e2e8f0]/50 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20 rounded-xl transition-all duration-300 ${
                            errors["username"] ? "border-red-400 focus:border-red-400" : ""
                          }`}
                          disabled={isSubmitting}
                          autoComplete="username"
                        />
                      </div>
                      {errors["username"] && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-sm text-red-400"
                        >
                          {errors["username"]}
                        </motion.p>
                      )}
                    </div>

                    {/* Email Field */}
                    <div className="space-y-3">
                      <Label htmlFor="email" className="text-[#e2e8f0] font-medium">
                        Email Address
                      </Label>
                      <div className="relative">
                        <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#e2e8f0]/50" />
                        <Input
                          id="email"
                          type="email"
                          placeholder="Enter your email"
                          value={formData.email}
                          onChange={(e) => handleInputChange("email", e.target.value)}
                          className={`pl-12 pr-4 py-4 bg-[#1a2332]/30 border-[#3b82f6]/20 text-[#e2e8f0] placeholder:text-[#e2e8f0]/50 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20 rounded-xl transition-all duration-300 ${
                            errors["email"] ? "border-red-400 focus:border-red-400" : ""
                          }`}
                          disabled={isSubmitting}
                          autoComplete="email"
                        />
                      </div>
                      {errors["email"] && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-sm text-red-400"
                        >
                          {errors["email"]}
                        </motion.p>
                      )}
                    </div>

                    {/* Password Field */}
                    <div className="space-y-3">
                      <Label htmlFor="password" className="text-[#e2e8f0] font-medium">
                        Password
                      </Label>
                      <div className="relative">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#e2e8f0]/50" />
                        <Input
                          id="password"
                          type={showPassword ? "text" : "password"}
                          placeholder="Create a strong password"
                          value={formData.password}
                          onChange={(e) => handleInputChange("password", e.target.value)}
                          className={`pl-12 pr-12 py-4 bg-[#1a2332]/30 border-[#3b82f6]/20 text-[#e2e8f0] placeholder:text-[#e2e8f0]/50 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20 rounded-xl transition-all duration-300 ${
                            errors["password"] ? "border-red-400 focus:border-red-400" : ""
                          }`}
                          disabled={isSubmitting}
                          autoComplete="new-password"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-[#e2e8f0]/50 hover:text-[#e2e8f0] transition-colors duration-200"
                          disabled={isSubmitting}
                        >
                          {showPassword ? (
                            <EyeOff className="h-5 w-5" />
                          ) : (
                            <Eye className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                      {errors["password"] && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-sm text-red-400"
                        >
                          {errors["password"]}
                        </motion.p>
                      )}
                    </div>

                    {/* Confirm Password Field */}
                    <div className="space-y-3">
                      <Label htmlFor="confirmPassword" className="text-[#e2e8f0] font-medium">
                        Confirm Password
                      </Label>
                      <div className="relative">
                        <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#e2e8f0]/50" />
                        <Input
                          id="confirmPassword"
                          type={showConfirmPassword ? "text" : "password"}
                          placeholder="Confirm your password"
                          value={formData.confirmPassword}
                          onChange={(e) => handleInputChange("confirmPassword", e.target.value)}
                          className={`pl-12 pr-12 py-4 bg-[#1a2332]/30 border-[#3b82f6]/20 text-[#e2e8f0] placeholder:text-[#e2e8f0]/50 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20 rounded-xl transition-all duration-300 ${
                            errors["confirmPassword"] ? "border-red-400 focus:border-red-400" : ""
                          }`}
                          disabled={isSubmitting}
                          autoComplete="new-password"
                        />
                        <button
                          type="button"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                          className="absolute right-4 top-1/2 -translate-y-1/2 text-[#e2e8f0]/50 hover:text-[#e2e8f0] transition-colors duration-200"
                          disabled={isSubmitting}
                        >
                          {showConfirmPassword ? (
                            <EyeOff className="h-5 w-5" />
                          ) : (
                            <Eye className="h-5 w-5" />
                          )}
                        </button>
                      </div>
                      {errors["confirmPassword"] && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-sm text-red-400"
                        >
                          {errors["confirmPassword"]}
                        </motion.p>
                      )}
                    </div>

                    {/* Terms Agreement */}
                    <div className="space-y-3">
                      <div className="flex items-start space-x-3">
                        <input
                          id="agreeToTerms"
                          type="checkbox"
                          checked={formData.agreeToTerms}
                          onChange={(e) => handleInputChange("agreeToTerms", e.target.checked)}
                          disabled={isSubmitting}
                          className="w-5 h-5 mt-1 rounded border-[#3b82f6]/30 text-[#3b82f6] focus:ring-[#3b82f6]/20 bg-[#1a2332]/30"
                        />
                        <Label htmlFor="agreeToTerms" className="text-[#e2e8f0]/80 text-sm leading-relaxed">
                          I agree to the{" "}
                          <button
                            type="button"
                            className="text-[#3b82f6] hover:text-[#3b82f6]/80 transition-colors duration-200"
                          >
                            Terms of Service
                          </button>{" "}
                          and{" "}
                          <button
                            type="button"
                            className="text-[#3b82f6] hover:text-[#3b82f6]/80 transition-colors duration-200"
                          >
                            Privacy Policy
                          </button>
                        </Label>
                      </div>
                      {errors["agreeToTerms"] && (
                        <motion.p
                          initial={{ opacity: 0, y: -5 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-sm text-red-400"
                        >
                          {errors["agreeToTerms"]}
                        </motion.p>
                      )}
                    </div>

                    {/* Submit Button */}
                    <Button
                      type="submit"
                      className="w-full py-4 bg-[#3b82f6] hover:bg-[#3b82f6]/90 text-[#0b1020] font-semibold rounded-xl transition-all duration-300 shadow-lg hover:shadow-xl disabled:opacity-50"
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? (
                        <div className="flex items-center justify-center space-x-2">
                          <LoadingSpinner size="sm" />
                          <span>Creating account...</span>
                        </div>
                      ) : (
                        "Create Account"
                      )}
                    </Button>

                    {/* Links */}
                    <div className="text-center space-y-4 pt-4">
                      <p className="text-sm text-[#e2e8f0]/70">
                        Already have an account?{" "}
                        <button
                          type="button"
                          onClick={() => router.push("/login")}
                          className="text-[#3b82f6] hover:text-[#3b82f6]/80 font-medium transition-colors duration-200"
                          disabled={isSubmitting}
                        >
                          Sign in
                        </button>
                      </p>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </motion.div>

            {/* Benefits */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="mt-8 space-y-4"
            >
              <h3 className="text-lg font-semibold text-[#e2e8f0] text-center mb-4">
                Why join SarvanOM?
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {[
                  {
                    icon: CheckCircle,
                    title: "AI-Powered",
                    description: "Advanced AI for intelligent responses"
                  },
                  {
                    icon: CheckCircle,
                    title: "Multi-Source",
                    description: "Verified information from diverse sources"
                  },
                  {
                    icon: CheckCircle,
                    title: "Real-time",
                    description: "Instant access to current knowledge"
                  }
                ].map((benefit, index) => (
                  <div key={benefit.title} className="flex items-center space-x-3 p-3 bg-[#1a2332]/30 rounded-xl border border-[#3b82f6]/10">
                    <benefit.icon className="w-5 h-5 text-green-400 flex-shrink-0" />
                    <div>
                      <p className="text-sm font-medium text-[#e2e8f0]">{benefit.title}</p>
                      <p className="text-xs text-[#e2e8f0]/60">{benefit.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
