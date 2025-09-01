'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const STREAM = (process.env.NEXT_PUBLIC_ENABLE_STREAMING || 'true') === 'true';

export default function SearchPage() {
  const [q, setQ] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<Array<{title?: string; url: string; snippet?: string}>>([]);
  const [loading, setLoading] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  function closeStream() {
    esRef.current?.close();
    esRef.current = null;
  }

  async function searchREST(query: string) {
    const res = await fetch(`${API}/search`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ q: query })
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    setAnswer(data?.answer || data?.overview || '');
    setSources(data?.sources || []);
  }

  function searchSSE(query: string) {
    closeStream();
    setAnswer('');
    const es = new EventSource(`${API}/stream/search?query=${encodeURIComponent(query)}`);
    esRef.current = es;

    es.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);
        if (payload.type === 'content_chunk') {
          setAnswer(a => a + (payload.delta || ''));
        } else if (payload.type === 'complete') {
          setSources(payload.sources || []);
          closeStream();
          setLoading(false);
        }
      } catch {
        setAnswer(a => a + e.data);
      }
    };
    es.onerror = () => { closeStream(); setLoading(false); };
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const query = q.trim();
    if (!query) return;
    setLoading(true);
    setSources([]); setAnswer('');
    try {
      STREAM ? searchSSE(query) : await searchREST(query);
    } catch (err: any) {
      setAnswer(`⚠️ ${err.message || 'Search failed.'}`);
    } finally {
      if (!STREAM) setLoading(false);
    }
  }

  useEffect(() => () => closeStream(), []);

  return (
    <main className="cosmic min-h-screen">
      <div className="container-std section-std">
        <header className="flex items-center justify-between">
          <h1 className="text-title">SarvanOM</h1>
          <nav className="text-sm opacity-90 flex gap-4">
            <Link className="link-std" href="/landing">Landing</Link>
            <Link className="link-std" href="/analytics">Analytics</Link>
            <Link className="link-std" href="/blog">Blog</Link>
            <Link className="link-std" href="/showcase">Showcase</Link>
          </nav>
        </header>

        <form onSubmit={onSubmit} className="mt-4 flex gap-2">
          <input
            aria-label="Search query"
            type="search"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Ask anything…"
            className="flex-1 rounded-md bg-[var(--card)]/90 px-4 py-3 outline-none focus:ring-2 focus:ring-[var(--accent)]"
          />
          <button
            className="rounded-md bg-[var(--accent)] px-4 py-3 text-black font-medium disabled:opacity-60"
            disabled={loading}
          >
            {loading ? 'Thinking…' : 'Search'}
          </button>
        </form>

        <section aria-label="AI Answer" className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <article className="lg:col-span-2 card-std p-4 text-body">
            {answer ? (
              <AnswerWithCitations text={answer} />
            ) : (
              <p className="opacity-80">{loading ? 'Streaming answer…' : 'Enter a question to begin.'}</p>
            )}
          </article>

          <aside className="card-std p-4" aria-label="Sources">
            <CitationsPanel items={sources} />
          </aside>
        </section>
      </div>
    </main>
  );
}

function AnswerWithCitations({ text }: { text: string }) {
  // Lightweight pass: convert [1] to anchors
  const withLinks = text.replace(/\[(\d+)]/g, (_m, n) => `<a class="link-std" href="#cite-${n}">[${n}]</a>`);
  return <div className="prose prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: withLinks }} />;
}

function CitationsPanel({ items }: { items: Array<{title?: string; url: string; snippet?: string}> }) {
  if (!items?.length) return <p className="text-sm opacity-75">No sources yet.</p>;
  return (
    <ol className="list-decimal list-inside text-sm space-y-2">
      {items.map((s, i) => (
        <li id={`cite-${i+1}`} key={s.url+i}>
          <a href={s.url} target="_blank" rel="noreferrer" className="link-std">
            [{i+1}] {s.title || new URL(s.url).hostname}
          </a>
          {s.snippet && <p className="opacity-80 mt-1">{s.snippet}</p>}
        </li>
      ))}
    </ol>
  );
}