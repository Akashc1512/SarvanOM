'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { 
  HomeIcon, 
  MagnifyingGlassIcon, 
  ChartBarIcon, 
  UserIcon,
  Bars3Icon,
  XMarkIcon,
  RocketLaunchIcon,
  DocumentTextIcon,
  CodeBracketIcon,
  LinkIcon,
  ChevronLeftIcon,
  ChevronRightIcon
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/ui/ThemeToggle';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
  badge?: string;
}

const navigation: NavItem[] = [
  {
    name: 'Home',
    href: '/',
    icon: HomeIcon,
    description: 'Main dashboard'
  },
  {
    name: 'Search',
    href: '/search',
    icon: MagnifyingGlassIcon,
    description: 'Knowledge search'
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: ChartBarIcon,
    description: 'Platform analytics',
    badge: 'New'
  },
  {
    name: 'Blog',
    href: '/blog',
    icon: DocumentTextIcon,
    description: 'Content blog'
  },
  {
    name: 'Showcase',
    href: '/showcase',
    icon: CodeBracketIcon,
    description: 'Portfolio showcase'
  },
  {
    name: 'Hub',
    href: '/hub',
    icon: LinkIcon,
    description: 'Personal hub'
  }
];

interface CosmicAppShellProps {
  children: React.ReactNode;
  className?: string;
  showStarfield?: boolean;
}

export const CosmicAppShell: React.FC<CosmicAppShellProps> = ({
  children,
  className,
  showStarfield = true
}) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const pathname = usePathname();

  // Close sidebar on mobile when route changes
  useEffect(() => {
    setSidebarOpen(false);
  }, [pathname]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey || e.ctrlKey) {
        if (e.key === 'b') {
          e.preventDefault();
          setSidebarCollapsed(!sidebarCollapsed);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [sidebarCollapsed]);

  const SidebarContent = () => (
    <div className="flex flex-col h-full">
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-4 border-b border-cosmic-border-primary">
        <AnimatePresence mode="wait">
          {!sidebarCollapsed && (
            <motion.div
              key="expanded-logo"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-3"
            >
              <div className="relative">
                <RocketLaunchIcon className="w-8 h-8 text-cosmic-primary-500 cosmic-glow-primary" />
                <motion.div
                  className="absolute inset-0 bg-cosmic-primary-500/20 rounded-full"
                  animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </div>
              <span className="text-xl font-bold cosmic-text-primary">SarvanOM</span>
            </motion.div>
          )}
        </AnimatePresence>
        
        {sidebarCollapsed && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center justify-center w-8 h-8"
          >
            <RocketLaunchIcon className="w-6 h-6 text-cosmic-primary-500 cosmic-glow-primary" />
          </motion.div>
        )}

        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="cosmic-btn-ghost p-1.5 rounded-lg hover:bg-cosmic-bg-secondary transition-colors"
          title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {sidebarCollapsed ? (
            <ChevronRightIcon className="w-4 h-4" />
          ) : (
            <ChevronLeftIcon className="w-4 h-4" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'cosmic-nav-item group relative flex items-center rounded-lg transition-all duration-200',
                isActive && 'cosmic-nav-item-active bg-cosmic-primary-500/10',
                sidebarCollapsed ? 'justify-center px-3' : 'px-3 py-2'
              )}
              title={sidebarCollapsed ? item.name : undefined}
            >
              <div className="flex items-center space-x-3 w-full">
                <item.icon className="w-5 h-5 flex-shrink-0" />
                <AnimatePresence>
                  {!sidebarCollapsed && (
                    <motion.div
                      key="nav-text"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -10 }}
                      transition={{ duration: 0.2 }}
                      className="flex-1 flex items-center justify-between"
                    >
                      <span className="text-sm font-medium">{item.name}</span>
                      {item.badge && (
                        <span className="px-2 py-0.5 text-xs bg-cosmic-primary-500 text-white rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
              
              {isActive && (
                <motion.div
                  className="absolute left-0 top-0 bottom-0 w-1 bg-cosmic-primary-500 rounded-r-full"
                  layoutId="activeIndicator"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-cosmic-border-primary">
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              key="footer-content"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.2 }}
              className="space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm cosmic-text-secondary">Theme</span>
                <ThemeToggle size="sm" variant="ghost" />
              </div>
              <div className="text-xs cosmic-text-tertiary">
                Press <kbd className="px-1 py-0.5 bg-cosmic-bg-secondary rounded text-xs">⌘B</kbd> to toggle
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        
        {sidebarCollapsed && (
          <div className="flex justify-center">
            <ThemeToggle size="sm" variant="ghost" />
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className={cn('min-h-screen cosmic-bg-primary', className)}>
      {/* Cosmic Pro Starfield Background */}
      {showStarfield && (
        <div className="fixed inset-0 pointer-events-none">
          <div className="absolute inset-0 cosmic-starfield opacity-20" />
          <motion.div
            className="absolute inset-0"
            animate={{
              backgroundPosition: ['0% 0%', '100% 100%'],
            }}
            transition={{
              duration: 30,
              repeat: Infinity,
              repeatType: 'reverse',
            }}
            style={{
              background: `
                radial-gradient(1px 1px at 20% 30%, rgba(59, 130, 246, 0.4) 0, transparent 40%),
                radial-gradient(1px 1px at 80% 20%, rgba(168, 85, 247, 0.3) 0, transparent 40%),
                radial-gradient(1px 1px at 40% 70%, rgba(59, 130, 246, 0.2) 0, transparent 40%),
                radial-gradient(1px 1px at 90% 90%, rgba(168, 85, 247, 0.3) 0, transparent 40%)
              `,
              backgroundSize: '300px 300px, 400px 400px, 200px 200px, 350px 350px',
            }}
          />
        </div>
      )}

      <div className="flex h-screen relative z-10">
        {/* Desktop Sidebar */}
        <motion.aside
          initial={false}
          animate={{
            width: sidebarCollapsed ? 64 : 280,
          }}
          transition={{ duration: 0.3, ease: 'easeInOut' }}
          className="hidden lg:flex flex-col cosmic-card-glass border-r border-cosmic-border-primary"
        >
          <SidebarContent />
        </motion.aside>

        {/* Mobile Sidebar Overlay */}
        <AnimatePresence>
          {sidebarOpen && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 lg:hidden"
                onClick={() => setSidebarOpen(false)}
              />
              <motion.aside
                initial={{ x: -280 }}
                animate={{ x: 0 }}
                exit={{ x: -280 }}
                transition={{ type: 'spring', damping: 25, stiffness: 200 }}
                className="fixed left-0 top-0 h-full w-80 cosmic-card-glass border-r border-cosmic-border-primary z-50 lg:hidden"
              >
                <SidebarContent />
              </motion.aside>
            </>
          )}
        </AnimatePresence>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Compact Topbar */}
          <header className="cosmic-topbar border-b border-cosmic-border-primary">
            <div className="flex items-center justify-between h-14 px-4">
              <div className="flex items-center space-x-4">
                {/* Mobile Menu Button */}
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="cosmic-btn-ghost p-2 lg:hidden"
                >
                  <Bars3Icon className="w-5 h-5" />
                </button>

                {/* Breadcrumb */}
                <nav className="hidden md:flex items-center space-x-2 text-sm">
                  <Link href="/" className="cosmic-text-tertiary hover:cosmic-text-primary transition-colors">
                    Home
                  </Link>
                  <span className="cosmic-text-tertiary">/</span>
                  <span className="cosmic-text-primary font-medium">
                    {navigation.find(item => item.href === pathname)?.name || 'Page'}
                  </span>
                </nav>
              </div>

              {/* Topbar Actions */}
              <div className="flex items-center space-x-3">
                <ThemeToggle size="sm" variant="ghost" />
                <div className="w-8 h-8 bg-cosmic-primary-500 rounded-full flex items-center justify-center">
                  <UserIcon className="w-4 h-4 text-white" />
                </div>
              </div>
            </div>
          </header>

          {/* Main Content */}
          <main className="flex-1 overflow-auto">
            <div className="cosmic-container cosmic-section">
              {children}
            </div>
          </main>
        </div>
      </div>

      {/* Cosmic Pro Accent Elements */}
      <motion.div
        className="absolute top-20 left-20 w-2 h-2 bg-cosmic-primary-500 rounded-full cosmic-glow-primary"
        animate={{
          opacity: [0.3, 1, 0.3],
          scale: [1, 1.5, 1],
        }}
        transition={{
          duration: 4,
          repeat: Infinity,
        }}
      />
      <motion.div
        className="absolute bottom-20 right-20 w-3 h-3 bg-cosmic-secondary-500 rounded-full cosmic-glow-secondary"
        animate={{
          opacity: [0.5, 1, 0.5],
          scale: [1, 2, 1],
        }}
        transition={{
          duration: 5,
          repeat: Infinity,
          delay: 1,
        }}
      />
    </div>
  );
};

export default CosmicAppShell;
