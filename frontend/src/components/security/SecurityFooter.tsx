"use client";

import React from 'react';
import { Shield, AlertTriangle, Info, ExternalLink } from 'lucide-react';

interface SecurityFooterProps {
  className?: string;
  variant?: 'default' | 'minimal' | 'detailed';
}

export function SecurityFooter({ 
  className = "", 
  variant = "default" 
}: SecurityFooterProps) {
  const [showDetails, setShowDetails] = React.useState(false);

  const securityInfo = {
    rateLimit: "60 requests per minute per IP",
    dataRetention: "Search data retained for 30 days",
    privacyPolicy: "https://sarvanom.com/privacy",
    termsOfService: "https://sarvanom.com/terms",
    securityReport: "https://sarvanom.com/security",
    contact: "security@sarvanom.com"
  };

  if (variant === "minimal") {
    return (
      <footer className={`text-xs text-muted-foreground/60 ${className}`}>
        <div className="flex items-center justify-center gap-2">
          <Shield className="h-3 w-3" />
          <span>Secure • Rate Limited • Privacy Protected</span>
        </div>
      </footer>
    );
  }

  if (variant === "detailed") {
    return (
      <footer className={`bg-muted/30 border-t border-border/50 ${className}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Security Status */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                <Shield className="h-4 w-4 text-green-500" />
                Security Status
              </h4>
              <div className="space-y-1 text-xs text-muted-foreground">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <span>All systems secure</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <span>Rate limiting active</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <span>Content sanitized</span>
                </div>
              </div>
            </div>

            {/* Usage Limits */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                Usage Limits
              </h4>
              <div className="space-y-1 text-xs text-muted-foreground">
                <div>• {securityInfo.rateLimit}</div>
                <div>• Burst limit: 10 requests/second</div>
                <div>• Max query length: 1000 characters</div>
                <div>• Data retention: 30 days</div>
              </div>
            </div>

            {/* Privacy & Legal */}
            <div className="space-y-2">
              <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                <Info className="h-4 w-4 text-blue-500" />
                Privacy & Legal
              </h4>
              <div className="space-y-1 text-xs text-muted-foreground">
                <a 
                  href={securityInfo.privacyPolicy}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 hover:text-foreground transition-colors"
                >
                  Privacy Policy <ExternalLink className="h-3 w-3" />
                </a>
                <a 
                  href={securityInfo.termsOfService}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 hover:text-foreground transition-colors"
                >
                  Terms of Service <ExternalLink className="h-3 w-3" />
                </a>
                <a 
                  href={securityInfo.securityReport}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 hover:text-foreground transition-colors"
                >
                  Security Report <ExternalLink className="h-3 w-3" />
                </a>
                <div className="flex items-center gap-1">
                  <span>Contact: </span>
                  <a 
                    href={`mailto:${securityInfo.contact}`}
                    className="hover:text-foreground transition-colors"
                  >
                    {securityInfo.contact}
                  </a>
                </div>
              </div>
            </div>
          </div>

          {/* Security Features */}
          <div className="mt-6 pt-4 border-t border-border/50">
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Shield className="h-3 w-3" />
                <span>HTTPS Encrypted</span>
              </div>
              <div className="flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" />
                <span>XSS Protected</span>
              </div>
              <div className="flex items-center gap-1">
                <Info className="h-3 w-3" />
                <span>CSRF Protected</span>
              </div>
              <div className="flex items-center gap-1">
                <Shield className="h-3 w-3" />
                <span>Clickjacking Protected</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    );
  }

  // Default variant
  return (
    <footer className={`bg-muted/20 border-t border-border/30 ${className}`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
          {/* Security Status */}
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Shield className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium text-foreground">Secure</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              <span className="text-sm text-muted-foreground">{securityInfo.rateLimit}</span>
            </div>
          </div>

          {/* Toggle Details */}
          <button
            onClick={() => setShowDetails(!showDetails)}
            className="text-xs text-muted-foreground hover:text-foreground transition-colors flex items-center gap-1"
          >
            <Info className="h-3 w-3" />
            {showDetails ? 'Hide' : 'Show'} Details
          </button>
        </div>

        {/* Expandable Details */}
        {showDetails && (
          <div className="mt-4 pt-4 border-t border-border/30">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-muted-foreground">
              <div className="space-y-1">
                <div className="font-medium text-foreground">Usage Limits</div>
                <div>• Burst limit: 10 requests/second</div>
                <div>• Max query length: 1000 characters</div>
                <div>• Data retention: 30 days</div>
              </div>
              <div className="space-y-1">
                <div className="font-medium text-foreground">Security Features</div>
                <div>• HTTPS encrypted</div>
                <div>• XSS & CSRF protected</div>
                <div>• Content sanitized</div>
              </div>
            </div>
            
            <div className="mt-3 pt-3 border-t border-border/20">
              <div className="flex flex-wrap items-center justify-center gap-4 text-xs">
                <a 
                  href={securityInfo.privacyPolicy}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 hover:text-foreground transition-colors"
                >
                  Privacy Policy <ExternalLink className="h-3 w-3" />
                </a>
                <a 
                  href={securityInfo.termsOfService}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 hover:text-foreground transition-colors"
                >
                  Terms of Service <ExternalLink className="h-3 w-3" />
                </a>
                <a 
                  href={`mailto:${securityInfo.contact}`}
                  className="hover:text-foreground transition-colors"
                >
                  {securityInfo.contact}
                </a>
              </div>
            </div>
          </div>
        )}
      </div>
    </footer>
  );
}

// Tooltip component for security information
export function SecurityTooltip({ children, content }: { 
  children: React.ReactNode; 
  content: string; 
}) {
  const [show, setShow] = React.useState(false);

  return (
    <div className="relative inline-block">
      <div
        onMouseEnter={() => setShow(true)}
        onMouseLeave={() => setShow(false)}
        className="cursor-help"
      >
        {children}
      </div>
      {show && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-popover text-popover-foreground text-xs rounded-md shadow-lg border border-border z-50 max-w-xs">
          <div className="whitespace-normal">{content}</div>
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-popover"></div>
        </div>
      )}
    </div>
  );
}

// Security status indicator
export function SecurityStatusIndicator() {
  const [status, setStatus] = React.useState<'secure' | 'warning' | 'error'>('secure');

  React.useEffect(() => {
    // In a real implementation, this would check actual security status
    // For now, we'll simulate a secure status
    setStatus('secure');
  }, []);

  const getStatusColor = () => {
    switch (status) {
      case 'secure': return 'text-green-500';
      case 'warning': return 'text-yellow-500';
      case 'error': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'secure': return 'All systems secure';
      case 'warning': return 'Security warning';
      case 'error': return 'Security issue detected';
      default: return 'Unknown status';
    }
  };

  return (
    <div className="flex items-center gap-2 text-xs">
      <Shield className={`h-3 w-3 ${getStatusColor()}`} />
      <span className={getStatusColor()}>{getStatusText()}</span>
    </div>
  );
}
