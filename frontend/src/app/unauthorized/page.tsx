"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/ui/ui/button";
import { Shield, Home, ArrowLeft, User } from "lucide-react";

export default function Unauthorized() {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const handleGoBack = () => {
    if (isClient && typeof window !== "undefined") {
      window.history.back();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          <div className="text-center">
            {/* Unauthorized Icon */}
            <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-yellow-100 mb-4">
              <Shield className="h-6 w-6 text-yellow-600" />
            </div>

            {/* Error Message */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              Access Denied
            </h1>
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Unauthorized Access
            </h2>
            <p className="text-gray-600 mb-8">
              You don&apos;t have permission to access this page. Please contact
              your administrator if you believe this is an error.
            </p>

            {/* Action Buttons */}
            <div className="space-y-4">
              <Button asChild className="w-full">
                <Link href="/">
                  <Home className="w-4 h-4 mr-2" />
                  Go to Homepage
                </Link>
              </Button>

              <Button variant="outline" asChild className="w-full">
                <Link href="/account">
                  <User className="w-4 h-4 mr-2" />
                  View Account
                </Link>
              </Button>

              <Button
                variant="ghost"
                onClick={handleGoBack}
                className="w-full"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Go Back
              </Button>
            </div>

            {/* Help Information */}
            <div className="mt-8 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-900 mb-3">
                Need Help?
              </h3>
              <div className="text-sm text-gray-600 space-y-2">
                <p>• Check your account permissions</p>
                <p>• Contact your system administrator</p>
                <p>• Request access to this feature</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
