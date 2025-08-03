"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Textarea } from "@/ui/ui/textarea";
import { Label } from "@/ui/ui/label";
import { ExpertValidationButton } from "@/ui/ExpertValidationButton";
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Clock,
  ArrowLeft,
  BookOpen,
  Users,
  Brain,
  Star,
  Info,
  History
} from "lucide-react";
import Link from "next/link";

interface ValidationHistory {
  id: string;
  claim: string;
  status: "supported" | "contradicted" | "unclear" | "pending";
  confidence: number;
  timestamp: string;
}

export default function ExpertReviewPage() {
  const [claim, setClaim] = useState("");
  const [validationHistory, setValidationHistory] = useState<ValidationHistory[]>([
    {
      id: "1",
      claim: "Artificial intelligence will replace most jobs by 2030",
      status: "unclear",
      confidence: 0.65,
      timestamp: "2024-01-15T10:30:00Z"
    },
    {
      id: "2", 
      claim: "The Earth is approximately 4.54 billion years old",
      status: "supported",
      confidence: 0.95,
      timestamp: "2024-01-14T15:45:00Z"
    },
    {
      id: "3",
      claim: "Quantum computers can solve all problems instantly",
      status: "contradicted", 
      confidence: 0.88,
      timestamp: "2024-01-13T09:20:00Z"
    }
  ]);

  const exampleClaims = [
    {
      title: "Scientific Claims",
      description: "Validate scientific facts and research findings",
      examples: [
        "Climate change is primarily caused by human activities",
        "Vaccines are safe and effective for preventing diseases",
        "The universe is expanding at an accelerating rate"
      ]
    },
    {
      title: "Historical Facts", 
      description: "Check historical events and timelines",
      examples: [
        "World War II ended in 1945",
        "The United States declared independence in 1776",
        "The Berlin Wall fell in 1989"
      ]
    },
    {
      title: "Technology Claims",
      description: "Verify technology trends and capabilities",
      examples: [
        "5G networks are faster than 4G",
        "Electric vehicles produce fewer emissions than gas cars",
        "Machine learning requires large amounts of data"
      ]
    },
    {
      title: "Economic Statements",
      description: "Validate economic data and market trends",
      examples: [
        "Inflation rates affect purchasing power",
        "Stock markets are volatile in uncertain times",
        "Cryptocurrency prices are highly volatile"
      ]
    }
  ];

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "supported":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "contradicted":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "unclear":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "pending":
        return <Clock className="h-4 w-4 text-blue-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "supported":
        return "bg-green-100 text-green-800 border-green-200";
      case "contradicted":
        return "bg-red-100 text-red-800 border-red-200";
      case "unclear":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "pending":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              <ArrowLeft className="h-4 w-4" />
            </Link>
            <h1 className="text-3xl font-bold text-gray-900">Expert Validation</h1>
          </div>
          <p className="text-gray-600">
            Fact-check claims using multiple expert networks including academic, industry, and AI validation
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className="flex items-center gap-1">
            <Shield className="h-3 w-3" />
            Multi-Source
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Validation Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Validation Form */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Validate a Claim
              </CardTitle>
              <CardDescription>
                Enter a claim to validate using our expert networks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="claim">Claim to Validate</Label>
                <Textarea
                  id="claim"
                  placeholder="Enter the claim you want to validate..."
                  value={claim}
                  onChange={(e) => setClaim(e.target.value)}
                  className="mt-1 min-h-[100px]"
                />
              </div>
              
              <div className="flex items-center gap-2">
                <ExpertValidationButton
                  claim={claim}
                  variant="default"
                  size="lg"
                  showBadge={true}
                />
              </div>
            </CardContent>
          </Card>

          {/* Expert Networks Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Expert Networks
              </CardTitle>
              <CardDescription>
                Our validation uses multiple expert networks for comprehensive fact-checking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <BookOpen className="h-5 w-5 text-blue-600" />
                    <h4 className="font-medium">Academic Network</h4>
                  </div>
                  <p className="text-sm text-gray-600">
                    Validates against peer-reviewed research, academic papers, and scholarly sources
                  </p>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Star className="h-5 w-5 text-green-600" />
                    <h4 className="font-medium">Industry Network</h4>
                  </div>
                  <p className="text-sm text-gray-600">
                    Checks against industry reports, expert opinions, and professional insights
                  </p>
                </div>
                
                <div className="border rounded-lg p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <Brain className="h-5 w-5 text-purple-600" />
                    <h4 className="font-medium">AI Model Validation</h4>
                  </div>
                  <p className="text-sm text-gray-600">
                    Uses advanced AI models to analyze claim consistency and factual accuracy
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Example Claims */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="h-5 w-5" />
                Example Claims
              </CardTitle>
              <CardDescription>
                Try validating these example claims
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {exampleClaims.map((category, index) => (
                  <div key={index}>
                    <h4 className="font-medium text-sm mb-2">{category.title}</h4>
                    <p className="text-xs text-gray-600 mb-2">{category.description}</p>
                    <div className="space-y-1">
                      {category.examples.map((example, exampleIndex) => (
                        <Button
                          key={exampleIndex}
                          variant="outline"
                          size="sm"
                          className="w-full justify-start text-xs h-auto p-2"
                          onClick={() => setClaim(example)}
                        >
                          {example}
                        </Button>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Validation History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <History className="h-5 w-5" />
                Recent Validations
              </CardTitle>
              <CardDescription>
                Your recent validation history
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {validationHistory.map((item) => (
                  <div key={item.id} className="border rounded-lg p-3">
                    <div className="flex items-start justify-between mb-2">
                      <Badge className={`text-xs ${getStatusColor(item.status)}`}>
                        {getStatusIcon(item.status)}
                        <span className="ml-1 capitalize">{item.status}</span>
                      </Badge>
                      <span className="text-xs text-gray-500">
                        {new Date(item.timestamp).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm text-gray-700 line-clamp-2 mb-2">
                      {item.claim}
                    </p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-gray-500">Confidence:</span>
                      <span className="font-medium">{(item.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
} 