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
    <nav className="flex gap-2 md:gap-4 py-2 items-center">
      {navItems.map(({ title, href, Icon }) => {
        const active = pathname === href;
        return (
          <Link
            key={href}
            href={href}
            className={`flex items-center gap-2 px-3 py-2 rounded-md font-medium transition-colors ${
              active
                ? "bg-blue-600 text-white"
                : "text-blue-700 hover:bg-blue-50"
            }`}
            aria-current={active ? "page" : undefined}
            title={title}
          >
            <Icon className="h-5 w-5" aria-hidden="true" />
            <span className="hidden md:inline">{title}</span>
          </Link>
        );
      })}
    </nav>
  );
}
