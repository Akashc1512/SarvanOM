"use client";

import { useState } from "react";
import { Button } from "@/ui/ui/button";
import { Badge } from "@/ui/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/ui/ui/dialog";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/ui/ui/card";
import { ScrollArea } from "@/ui/ui/ScrollArea";
import { Separator } from "@/ui/ui/separator";
import { Progress } from "@/ui/ui/progress";
import {
  Shield,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock,
  User,
  Star,
  Brain,
  Loader2,
} from "lucide-react";
import { useToast } from "@/hooks/useToast";

interface ValidationResult {
  status: "supported" | "contradicted" | "unclear" | "pending";
  confidence: number;
  consensus_score: number;
  total_experts: number;
  agreeing_experts: number;
  expert_network: string;
  validation_time: string;
  details?: {
    academic_validation?: {
      status: string;
      confidence: number;
      notes: string;
    };
    industry_validation?: {
      status: string;
      confidence: number;
      notes: string;
    };
    ai_model_validation?: {
      status: string;
      confidence: number;
      notes: string;
    };
  };
  sources_checked: string[];
  reasoning: string;
}

interface ExpertValidationButtonProps {
  claim: string;
  queryId?: string;
  variant?: "default" | "outline" | "ghost";
  size?: "default" | "sm" | "lg";
  showBadge?: boolean;
  onValidationComplete?: (status: string, confidence: number) => void;
}

export function ExpertValidationButton({
  claim,
  queryId,
  variant = "outline",
  size = "sm",
  showBadge = true,
  onValidationComplete,
}: ExpertValidationButtonProps) {
  const { toast } = useToast();
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  const handleValidation = async () => {
    if (!claim.trim()) {
      toast({
        title: "No claim to validate",
        description: "Please provide a claim to validate",
        variant: "destructive",
      });
      return;
    }

    setIsValidating(true);
    try {
      const response = await fetch("/fact-check", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          content: claim.trim(),
          user_id: queryId,
          context: `Query ID: ${queryId}`,
        }),
      });

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`);
      }

      const result: ValidationResult = await response.json();
      setValidationResult(result);
      
      // Call the callback to update parent component
      if (onValidationComplete) {
        onValidationComplete(result.status, result.confidence);
      }
      
      toast({
        title: "Validation Complete",
        description: `Claim ${result.status} with ${(result.confidence * 100).toFixed(0)}% confidence`,
      });
    } catch (error) {
      console.error("Validation error:", error);
      toast({
        title: "Validation Failed",
        description: error instanceof Error ? error.message : "Failed to validate claim",
        variant: "destructive",
      });
    } finally {
      setIsValidating(false);
    }
  };

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

  const getStatusText = (status: string) => {
    switch (status) {
      case "supported":
        return "Expert Verified ✅";
      case "contradicted":
        return "Failed ❌";
      case "unclear":
        return "Validation Pending ⏳";
      case "pending":
        return "Validation Pending ⏳";
      default:
        return "Validation Pending ⏳";
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

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-green-600";
    if (confidence >= 0.6) return "text-yellow-600";
    if (confidence >= 0.4) return "text-orange-600";
    return "text-red-600";
  };

  return (
    <>
      <div className="flex items-center gap-2">
        <Button
          variant={variant}
          size={size}
          onClick={handleValidation}
          disabled={isValidating || (validationResult && validationResult.status === "supported")}
          className="flex items-center gap-2"
        >
          {isValidating ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Shield className="h-4 w-4" />
          )}
          {isValidating ? "Validating..." : "Request Expert Validation"}
        </Button>

        {showBadge && validationResult && (
          <Badge 
            variant="outline" 
            className={`${getStatusColor(validationResult.status)} cursor-pointer`}
            onClick={() => setShowDetails(true)}
          >
            {getStatusIcon(validationResult.status)}
            <span className="ml-1">{getStatusText(validationResult.status)}</span>
            <span className={`ml-1 font-medium ${getConfidenceColor(validationResult.confidence)}`}>
              {(validationResult.confidence * 100).toFixed(0)}%
            </span>
          </Badge>
        )}
      </div>

      {/* Validation Details Dialog */}
      <Dialog open={showDetails} onOpenChange={setShowDetails}>
        <DialogContent className="max-w-2xl max-h-[80vh]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Expert Validation Results
            </DialogTitle>
          </DialogHeader>

          {validationResult && (
            <ScrollArea className="max-h-[60vh]">
              <div className="space-y-6">
                {/* Claim */}
                <div>
                  <h3 className="font-semibold mb-2">Claim Validated</h3>
                  <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                    {claim}
                  </p>
                </div>

                <Separator />

                {/* Overall Result */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h3 className="font-semibold">Overall Result</h3>
                    <Badge className={getStatusColor(validationResult.status)}>
                      {getStatusIcon(validationResult.status)}
                      <span className="ml-1 capitalize">{validationResult.status}</span>
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Confidence</p>
                      <p className={`font-semibold ${getConfidenceColor(validationResult.confidence)}`}>
                        {(validationResult.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Consensus Score</p>
                      <p className="font-semibold">
                        {(validationResult.consensus_score * 100).toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Experts Consulted</p>
                      <p className="font-semibold">{validationResult.total_experts}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Agreeing Experts</p>
                      <p className="font-semibold">{validationResult.agreeing_experts}</p>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Expert Network Results */}
                {validationResult.details && (
                  <div>
                    <h3 className="font-semibold mb-3">Expert Network Results</h3>
                    <div className="space-y-4">
                      {validationResult.details.academic_validation && (
                        <Card>
                          <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2 text-sm">
                              <User className="h-4 w-4" />
                              Academic Network
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="outline" className="capitalize">
                                {validationResult.details.academic_validation.status}
                              </Badge>
                              <span className={`text-sm font-medium ${getConfidenceColor(validationResult.details.academic_validation.confidence)}`}>
                                {(validationResult.details.academic_validation.confidence * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                            <p className="text-sm text-gray-600">
                              {validationResult.details.academic_validation.notes}
                            </p>
                          </CardContent>
                        </Card>
                      )}

                      {validationResult.details.industry_validation && (
                        <Card>
                          <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2 text-sm">
                              <Star className="h-4 w-4" />
                              Industry Network
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="outline" className="capitalize">
                                {validationResult.details.industry_validation.status}
                              </Badge>
                              <span className={`text-sm font-medium ${getConfidenceColor(validationResult.details.industry_validation.confidence)}`}>
                                {(validationResult.details.industry_validation.confidence * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                            <p className="text-sm text-gray-600">
                              {validationResult.details.industry_validation.notes}
                            </p>
                          </CardContent>
                        </Card>
                      )}

                      {validationResult.details.ai_model_validation && (
                        <Card>
                          <CardHeader className="pb-2">
                            <CardTitle className="flex items-center gap-2 text-sm">
                              <Brain className="h-4 w-4" />
                              AI Model Validation
                            </CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="flex items-center justify-between mb-2">
                              <Badge variant="outline" className="capitalize">
                                {validationResult.details.ai_model_validation.status}
                              </Badge>
                              <span className={`text-sm font-medium ${getConfidenceColor(validationResult.details.ai_model_validation.confidence)}`}>
                                {(validationResult.details.ai_model_validation.confidence * 100).toFixed(0)}% confidence
                              </span>
                            </div>
                            <p className="text-sm text-gray-600">
                              {validationResult.details.ai_model_validation.notes}
                            </p>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  </div>
                )}

                <Separator />

                {/* Reasoning */}
                {validationResult.reasoning && (
                  <div>
                    <h3 className="font-semibold mb-2">Validation Reasoning</h3>
                    <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">
                      {validationResult.reasoning}
                    </p>
                  </div>
                )}

                {/* Sources Checked */}
                {validationResult.sources_checked && validationResult.sources_checked.length > 0 && (
                  <>
                    <Separator />
                    <div>
                      <h3 className="font-semibold mb-2">Sources Checked</h3>
                      <div className="space-y-1">
                        {validationResult.sources_checked.map((source, index) => (
                          <p key={index} className="text-sm text-gray-600">
                            • {source}
                          </p>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {/* Validation Time */}
                <Separator />
                <div className="text-xs text-gray-500">
                  Validated on {new Date(validationResult.validation_time).toLocaleString()}
                </div>
              </div>
            </ScrollArea>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
} 