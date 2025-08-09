"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Home,
  Search,
  BarChart2,
  Sparkles,
  FileText,
  Users,
  Cog,
  HelpCircle,
  Shield,
  Settings,
  MessageSquare,
  BookOpen,
  TrendingUp,
  LucideIcon
} from "lucide-react";
import { ThemeToggle } from "@/ui/ThemeToggle";

// Use LucideIcon as the type for icons
interface NavItem {
  title: string;
  href: string;
  Icon: LucideIcon;
}

const navItems: NavItem[] = [
  {
    title: "Home",
    href: "/",
    Icon: Home,
  },
  {
    title: "Search",
    href: "/search",
    Icon: Search,
  },
  {
    title: "Queries",
    href: "/queries",
    Icon: Search,
  },
  {
    title: "Dashboard",
    href: "/dashboard",
    Icon: BarChart2,
  },
  {
    title: "Insights",
    href: "/analytics",
    Icon: TrendingUp,
  },
  {
    title: "Expert Review",
    href: "/expert-review",
    Icon: Shield,
  },
  {
    title: "Research",
    href: "/research",
    Icon: Sparkles,
  },
  {
    title: "Docs",
    href: "/docs",
    Icon: FileText,
  },
  {
    title: "Team",
    href: "/team",
    Icon: Users,
  },
               {
               title: "Collaboration",
               href: "/collaboration-demo",
               Icon: MessageSquare,
             },
             {
               title: "Testing",
               href: "/testing-demo",
               Icon: Sparkles,
             },
  {
    title: "Memory",
    href: "/memory",
    Icon: BookOpen,
  },
  {
    title: "Admin",
    href: "/admin/dashboard",
    Icon: Settings,
  },
  {
    title: "Settings",
    href: "/settings",
    Icon: Cog,
  },
  {
    title: "Help",
    href: "/help",
    Icon: HelpCircle,
  },
];

export function MainNav() {
  const pathname = usePathname();

  return (
    <nav className="bg-white/80 dark:bg-slate-800/80 backdrop-blur-sm border-b border-gray-200/50 dark:border-slate-700/50 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Brand */}
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2">
              <div className="relative">
                <Sparkles className="h-8 w-8 text-purple-600 dark:text-purple-400" />
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-purple-400 rounded-full animate-pulse" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                SarvanOM
              </span>
            </Link>
          </div>

          {/* Navigation Items */}
          <div className="hidden md:flex items-center space-x-1">
            {navItems.map(({ title, href, Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md font-medium transition-all duration-200 ${
                    active
                      ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg"
                      : "text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-slate-700/50 hover:text-purple-600 dark:hover:text-purple-400"
                  }`}
                  aria-current={active ? "page" : undefined}
                  title={title}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span className="text-sm">{title}</span>
                </Link>
              );
            })}
          </div>

          {/* Right side controls */}
          <div className="flex items-center space-x-3">
            <ThemeToggle size="sm" />
            
            {/* Mobile menu button */}
            <button className="md:hidden p-2 rounded-md text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-slate-700/50">
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden py-4 border-t border-gray-200 dark:border-slate-700">
          <div className="grid grid-cols-2 gap-2">
            {navItems.slice(0, 8).map(({ title, href, Icon }) => {
              const active = pathname === href;
              return (
                <Link
                  key={href}
                  href={href}
                  className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    active
                      ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white"
                      : "text-gray-700 dark:text-gray-300 hover:bg-purple-50 dark:hover:bg-slate-700/50"
                  }`}
                  aria-current={active ? "page" : undefined}
                >
                  <Icon className="h-4 w-4" aria-hidden="true" />
                  <span>{title}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    </nav>
  );
}
