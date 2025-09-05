'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
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
  LinkIcon
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';
import { ThemeToggle } from '@/ui/ThemeToggle';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

const navigation: NavItem[] = [
  {
    name: 'Home',
    href: '/',
    icon: HomeIcon,
    description: 'Main dashboard'
  },
  {
    name: 'Landing',
    href: '/landing',
    icon: RocketLaunchIcon,
    description: 'Marketing landing page'
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
    description: 'Platform analytics'
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

interface CosmicNavigationProps {
  className?: string;
  variant?: 'header' | 'sidebar' | 'mobile';
}

export const CosmicNavigation: React.FC<CosmicNavigationProps> = ({
  className,
  variant = 'header'
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const pathname = usePathname();

  const HeaderNav = () => (
    <nav className="hidden md:flex items-center space-x-2">
      {navigation.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'cosmic-nav-item group relative',
              isActive && 'cosmic-nav-item-active'
            )}
          >
            <div className="flex items-center space-x-2">
              <item.icon className="w-4 h-4" />
              <span>{item.name}</span>
            </div>
            {isActive && (
              <motion.div
                className="absolute inset-0 bg-cosmic-primary-500/10 rounded-lg cosmic-glow-soft"
                layoutId="activeTab"
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            )}
          </Link>
        );
      })}
    </nav>
  );

  const MobileNav = () => (
    <div className="md:hidden">
      <button
        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
        className="cosmic-btn-ghost p-2"
      >
        {isMobileMenuOpen ? (
          <XMarkIcon className="w-6 h-6" />
        ) : (
          <Bars3Icon className="w-6 h-6" />
        )}
      </button>

      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-full left-0 right-0 mt-2 cosmic-card-glass shadow-xl z-50"
          >
            <div className="px-4 py-2 space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setIsMobileMenuOpen(false)}
                    className={cn(
                      'cosmic-nav-item flex items-center space-x-3',
                      isActive && 'cosmic-nav-item-active'
                    )}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
              
              {/* Mobile Theme Toggle */}
              <div className="flex items-center justify-between px-3 py-2 border-t border-cosmic-border-primary mt-2">
                <span className="text-sm cosmic-text-secondary">Theme</span>
                <ThemeToggle size="sm" variant="ghost" />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );

  if (variant === 'header') {
    return (
      <header className={cn(
        'cosmic-topbar sticky top-0 z-50',
        className
      )}>
        <div className="cosmic-container">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-3 cosmic-hover-lift">
              <div className="relative">
                <RocketLaunchIcon className="w-8 h-8 text-cosmic-primary-500 cosmic-glow-primary" />
                <motion.div
                  className="absolute inset-0 bg-cosmic-primary-500/20 rounded-full"
                  animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </div>
              <span className="text-xl font-bold cosmic-text-primary">SarvanOM</span>
            </Link>

            {/* Desktop Navigation */}
            <HeaderNav />

            {/* Theme Toggle */}
            <div className="hidden md:flex items-center">
              <ThemeToggle size="sm" variant="ghost" />
            </div>

            {/* Mobile Navigation */}
            <MobileNav />
          </div>
        </div>
      </header>
    );
  }

  return null;
};

export default CosmicNavigation;
