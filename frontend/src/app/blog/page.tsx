import dynamic from 'next/dynamic';

// Fallback component for when EruditeBlog is not available
const FallbackBlog = () => (
  <section className="section-std">
    <h1 className="text-title">Blog</h1>
    <p className="text-body opacity-90">Posts will appear here.</p>
  </section>
);

const MaybeBlog = dynamic(
  () => import('@/components/blog/EruditeBlog'),
  { 
    ssr: true,
    loading: () => <FallbackBlog />
  }
);

export const metadata = { title: 'SarvanOM — Blog' };

export default function BlogPage() {
  return (
    <main className="cosmic min-h-screen">
      <div className="container-std">
        <MaybeBlog />
      </div>
    </main>
  );
}
