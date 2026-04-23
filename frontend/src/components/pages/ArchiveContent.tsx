'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { DigestSummary } from '@/types';
import Header from '@/components/layout/Header';

export default function ArchiveContent() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [archives, setArchives] = useState<DigestSummary[]>([]);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!loading && !user) router.push('/login');
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    api.get<DigestSummary[]>('/api/digest/archive')
      .then(setArchives)
      .catch((err) => setError(err.message))
      .finally(() => setFetching(false));
  }, [user]);

  if (loading || fetching) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-400">載入中...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-5 sm:mb-6">歷史月報彙整</h1>
        {error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 sm:p-6 text-red-600 text-sm sm:text-base">{error}</div>
        ) : archives.length === 0 ? (
          <div className="bg-gray-100 rounded-xl p-4 sm:p-6 text-gray-500 text-sm sm:text-base">尚無歷史月報</div>
        ) : (
          <div className="space-y-3">
            {archives.map((item) => (
              <Link
                key={item.id}
                href={`/archive/${item.year}/${item.month}`}
                className="block bg-white rounded-xl border border-gray-100 shadow-sm px-4 sm:px-6 py-4 hover:shadow-md transition"
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="font-medium text-gray-800 text-sm sm:text-base">
                    {item.year} 年 {item.month} 月
                  </span>
                  {item.published_at && (
                    <span className="text-xs sm:text-sm text-gray-400 shrink-0">
                      {new Date(item.published_at).toLocaleDateString('zh-TW')}
                    </span>
                  )}
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
