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
import { Eye, EyeOff, AlertCircle, User, Lock, Sparkles } from "lucide-react";
import { motion } from "framer-motion";

export default function LoginPage() {
  const [formData, setFormData] = useState({
    username: "",
    password: "",
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { login, isAuthenticated, isLoading, error } = useAuth();
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
    }

    if (!formData.password) {
      newErrors["password"] = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors["password"] = "Password must be at least 6 characters";
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
      await login({
        username: formData.username.trim(),
        password: formData.password,
        remember_me: formData.rememberMe,
      });

      // Redirect will be handled by useEffect
    } catch (error) {
      console.error("Login failed:", error);
      setErrors({
        general: error instanceof Error ? error.message : "Login failed. Please try again.",
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
      <div className="min-h-screen bg-[#0b1020] flex items-center justify-center">
        <motion.div 
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          className="text-center space-y-6"
        >
          <LoadingSpinner size="lg" />
          <p className="text-lg text-[#e2e8f0]/70">Initializing SarvanOM...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0b1020] relative overflow-hidden">
      {/* Starfield Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div 
          className="absolute inset-0 opacity-30 animate-starfield"
          style={{
            background: `
              radial-gradient(1px 1px at 20% 30%, rgba(255,255,255,0.8) 0, transparent 40%),
              radial-gradient(1px 1px at 80% 20%, rgba(255,255,255,0.5) 0, transparent 40%),
              radial-gradient(1px 1px at 40% 70%, rgba(255,255,255,0.3) 0, transparent 40%),
              radial-gradient(1px 1px at 90% 90%, rgba(255,255,255,0.4) 0, transparent 40%)
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
                Welcome Back
              </motion.h1>
              
              <motion.p
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="text-lg text-[#e2e8f0]/70"
              >
                Sign in to your SarvanOM account
              </motion.p>
            </div>

            {/* Login Form */}
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
                          placeholder="Enter your username"
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
                          placeholder="Enter your password"
                          value={formData.password}
                          onChange={(e) => handleInputChange("password", e.target.value)}
                          className={`pl-12 pr-12 py-4 bg-[#1a2332]/30 border-[#3b82f6]/20 text-[#e2e8f0] placeholder:text-[#e2e8f0]/50 focus:border-[#3b82f6] focus:ring-[#3b82f6]/20 rounded-xl transition-all duration-300 ${
                            errors["password"] ? "border-red-400 focus:border-red-400" : ""
                          }`}
                          disabled={isSubmitting}
                          autoComplete="current-password"
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

                    {/* Remember Me */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <input
                          id="rememberMe"
                          type="checkbox"
                          checked={formData.rememberMe}
                          onChange={(e) => handleInputChange("rememberMe", e.target.checked)}
                          disabled={isSubmitting}
                          className="w-5 h-5 rounded border-[#3b82f6]/30 text-[#3b82f6] focus:ring-[#3b82f6]/20 bg-[#1a2332]/30"
                        />
                        <Label htmlFor="rememberMe" className="text-[#e2e8f0]/80 text-sm">
                          Remember me
                        </Label>
                      </div>
                      
                      <button
                        type="button"
                        className="text-sm text-[#3b82f6] hover:text-[#3b82f6]/80 transition-colors duration-200"
                        disabled={isSubmitting}
                      >
                        Forgot password?
                      </button>
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
                          <span>Signing in...</span>
                        </div>
                      ) : (
                        "Sign In"
                      )}
                    </Button>

                    {/* Links */}
                    <div className="text-center space-y-4 pt-4">
                      <p className="text-sm text-[#e2e8f0]/70">
                        Don't have an account?{" "}
                        <button
                          type="button"
                          onClick={() => router.push("/register")}
                          className="text-[#3b82f6] hover:text-[#3b82f6]/80 font-medium transition-colors duration-200"
                          disabled={isSubmitting}
                        >
                          Sign up
                        </button>
                      </p>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </motion.div>

            {/* Footer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="mt-8 text-center"
            >
              <p className="text-xs text-[#e2e8f0]/50">
                By signing in, you agree to our{" "}
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
              </p>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </div>
  );
} 