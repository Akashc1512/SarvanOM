'use client';
import Link from 'next/link';

export default function Header() {
  return (
    <header className="w-full">
      <div className="container-std py-4 flex items-center justify-between">
        <Link href="/" className="text-title">SarvanOM</Link>
        <nav className="text-sm opacity-90 flex gap-4">
          <Link className="link-std" href="/landing">Landing</Link>
          <Link className="link-std" href="/analytics">Analytics</Link>
          <Link className="link-std" href="/blog">Blog</Link>
          <Link className="link-std" href="/showcase">Showcase</Link>
          <Link className="link-std" href="/hub">Hub</Link>
        </nav>
      </div>
    </header>
  );
}
