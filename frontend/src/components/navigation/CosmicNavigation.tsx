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
  RocketLaunchIcon
} from '@heroicons/react/24/outline';
import { cn } from '@/lib/utils';

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
    name: 'Profile',
    href: '/profile',
    icon: UserIcon,
    description: 'User settings'
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
    <nav className="hidden md:flex items-center space-x-8">
      {navigation.map((item) => {
        const isActive = pathname === item.href;
        return (
          <Link
            key={item.name}
            href={item.href}
            className={cn(
              'group relative px-3 py-2 text-sm font-medium rounded-md transition-all duration-200',
              'hover:text-cosmos-accent hover:bg-cosmos-card/50',
              isActive 
                ? 'text-cosmos-accent bg-cosmos-card/30' 
                : 'text-cosmos-fg/80'
            )}
          >
            <div className="flex items-center space-x-2">
              <item.icon className="w-4 h-4" />
              <span>{item.name}</span>
            </div>
            {isActive && (
              <motion.div
                className="absolute inset-0 bg-cosmos-accent/20 rounded-md"
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
        className="p-2 rounded-md text-cosmos-fg hover:text-cosmos-accent hover:bg-cosmos-card/50 transition-colors"
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
            className="absolute top-full left-0 right-0 mt-2 bg-cosmos-card/95 backdrop-blur-sm border border-cosmos-accent/20 rounded-lg shadow-xl"
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
                      'flex items-center space-x-3 px-3 py-2 rounded-md text-sm font-medium transition-colors',
                      isActive
                        ? 'text-cosmos-accent bg-cosmos-accent/20'
                        : 'text-cosmos-fg hover:text-cosmos-accent hover:bg-cosmos-accent/10'
                    )}
                  >
                    <item.icon className="w-5 h-5" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );

  if (variant === 'header') {
    return (
      <header className={cn(
        'sticky top-0 z-50 bg-cosmos-bg/80 backdrop-blur-md border-b border-cosmos-accent/20',
        className
      )}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center space-x-2">
              <RocketLaunchIcon className="w-8 h-8 text-cosmos-accent" />
              <span className="text-xl font-bold text-cosmos-fg">SarvanOM</span>
            </Link>

            {/* Desktop Navigation */}
            <HeaderNav />

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
