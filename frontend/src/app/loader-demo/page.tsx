"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { SarvanomLoader, SarvanomLoaderFullScreen, SarvanomLoaderInline } from "@/components/SarvanomLoader";
import { Loader2, Play, Pause, RotateCcw } from "lucide-react";

export default function LoaderDemo() {
  const [isLoading, setIsLoading] = useState(false);
  const [showFullScreen, setShowFullScreen] = useState(false);
  const [demoType, setDemoType] = useState<'basic' | 'fullscreen' | 'inline'>('basic');

  const simulateLoading = () => {
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 3000);
  };

  const simulateFullScreenLoading = () => {
    setShowFullScreen(true);
    setTimeout(() => setShowFullScreen(false), 3000);
  };

  if (showFullScreen) {
    return <SarvanomLoaderFullScreen />;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            SarvanOM Loader Demo
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            A beautiful, animated loader component for the SarvanOM platform. 
            Features orbiting nodes around a globe design with smooth animations.
          </p>
        </div>

        {/* Demo Controls */}
        <div className="flex justify-center gap-4 mb-8">
          <Button
            onClick={() => setDemoType('basic')}
            variant={demoType === 'basic' ? 'default' : 'outline'}
          >
            Basic Demo
          </Button>
          <Button
            onClick={() => setDemoType('fullscreen')}
            variant={demoType === 'fullscreen' ? 'default' : 'outline'}
          >
            Full Screen Demo
          </Button>
          <Button
            onClick={() => setDemoType('inline')}
            variant={demoType === 'inline' ? 'default' : 'outline'}
          >
            Inline Demo
          </Button>
        </div>

        {/* Basic Demo */}
        {demoType === 'basic' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5" />
                  Small Loader
                </CardTitle>
                <CardDescription>
                  60px size - Perfect for buttons and small spaces
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <SarvanomLoader size={60} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5" />
                  Medium Loader
                </CardTitle>
                <CardDescription>
                  120px size - Default size for most use cases
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <SarvanomLoader size={120} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Loader2 className="h-5 w-5" />
                  Large Loader
                </CardTitle>
                <CardDescription>
                  200px size - For prominent loading states
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <SarvanomLoader size={200} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Play className="h-5 w-5" />
                  Interactive Demo
                </CardTitle>
                <CardDescription>
                  Click to simulate a loading state
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <Button 
                  onClick={simulateLoading}
                  disabled={isLoading}
                  className="mb-4"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Start Loading
                    </>
                  )}
                </Button>
                {isLoading && (
                  <div className="mt-4">
                    <SarvanomLoader size={80} />
                    <p className="text-sm text-gray-600 mt-2">Processing...</p>
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <RotateCcw className="h-5 w-5" />
                  Full Screen Demo
                </CardTitle>
                <CardDescription>
                  Experience the full screen loading experience
                </CardDescription>
              </CardHeader>
              <CardContent className="text-center">
                <Button 
                  onClick={simulateFullScreenLoading}
                  variant="outline"
                  className="mb-4"
                >
                  <Play className="h-4 w-4 mr-2" />
                  Show Full Screen
                </Button>
                <p className="text-sm text-gray-600">
                  Will show for 3 seconds
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Badge variant="secondary">Custom</Badge>
                  Custom Styling
                </CardTitle>
                <CardDescription>
                  Loader with custom background and styling
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-lg">
                  <SarvanomLoader size={100} />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Full Screen Demo */}
        {demoType === 'fullscreen' && (
          <Card>
            <CardHeader>
              <CardTitle>Full Screen Loader Demo</CardTitle>
              <CardDescription>
                The full screen loader provides a complete loading experience
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 bg-gray-50">
                <div className="text-center">
                  <SarvanomLoader size={120} />
                  <p className="mt-4 text-gray-600 text-lg font-medium">
                    Loading SarvanOM...
                  </p>
                  <p className="text-sm text-gray-500 mt-2">
                    This simulates the full screen loading experience
                  </p>
                </div>
              </div>
              <div className="mt-4 text-center">
                <Button onClick={simulateFullScreenLoading}>
                  <Play className="h-4 w-4 mr-2" />
                  Experience Full Screen
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Inline Demo */}
        {demoType === 'inline' && (
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Inline Loader Examples</CardTitle>
                <CardDescription>
                  Small loaders perfect for inline use in forms, buttons, and content areas
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-4 p-4 bg-white rounded border">
                  <span className="text-sm font-medium">Processing data...</span>
                  <SarvanomLoaderInline size={20} />
                </div>
                
                <div className="flex items-center gap-4 p-4 bg-white rounded border">
                  <span className="text-sm font-medium">Saving changes...</span>
                  <SarvanomLoaderInline size={24} />
                </div>
                
                <div className="flex items-center gap-4 p-4 bg-white rounded border">
                  <span className="text-sm font-medium">Loading results...</span>
                  <SarvanomLoaderInline size={32} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Button Integration</CardTitle>
                <CardDescription>
                  Loaders integrated into buttons for better UX
                </CardDescription>
              </CardHeader>
              <CardContent className="flex gap-4">
                <Button disabled={isLoading} onClick={simulateLoading}>
                  {isLoading ? (
                    <>
                      <SarvanomLoader size={16} />
                      <span className="ml-2">Loading...</span>
                    </>
                  ) : (
                    "Click to Load"
                  )}
                </Button>
                
                <Button variant="outline" disabled={isLoading} onClick={simulateLoading}>
                  {isLoading ? (
                    <>
                      <SarvanomLoader size={16} />
                      <span className="ml-2">Processing...</span>
                    </>
                  ) : (
                    "Secondary Action"
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Technical Details */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Technical Details</CardTitle>
            <CardDescription>
              Information about the SarvanOM loader implementation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <h4 className="font-semibold mb-2">Features</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Smooth orbital animations</li>
                  <li>• Pulsing center node</li>
                  <li>• Globe design with ellipses</li>
                  <li>• Customizable size</li>
                  <li>• TypeScript support</li>
                  <li>• Responsive design</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold mb-2">Usage</h4>
                <div className="text-sm text-gray-600 space-y-2">
                  <code className="bg-gray-100 px-2 py-1 rounded">
                    &lt;SarvanomLoader size={120} /&gt;
                  </code>
                  <br />
                  <code className="bg-gray-100 px-2 py-1 rounded">
                    &lt;SarvanomLoaderFullScreen /&gt;
                  </code>
                  <br />
                  <code className="bg-gray-100 px-2 py-1 rounded">
                    &lt;SarvanomLoaderInline size={40} /&gt;
                  </code>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
} 