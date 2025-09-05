import dynamic from 'next/dynamic';

// Fallback component for when EruditeBlog is not available
const FallbackBlog = () => (
  <section className="cosmic-section">
    <h1 className="text-4xl font-bold cosmic-text-primary">Blog</h1>
    <p className="text-lg cosmic-text-secondary">Posts will appear here.</p>
  </section>
);

const EruditeBlog = dynamic(
  () => import('@/components/blog/EruditeBlog').then(mod => ({ default: mod.EruditeBlog })),
  { 
    ssr: true,
    loading: () => <FallbackBlog />
  }
);

export const metadata = { title: 'SarvanOM — Blog' };

export default function BlogPage() {
  return (
    <main className="cosmic-bg-primary min-h-screen">
      <div className="cosmic-container">
        <EruditeBlog />
      </div>
    </main>
  );
}
