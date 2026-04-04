'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import { Digest, DigestSummary } from '@/types';
import Header from '@/components/layout/Header';
import LawChangesBlock from '@/components/digest/LawChangesBlock';
import CalendarBlock from '@/components/digest/CalendarBlock';
import NewsBlock from '@/components/digest/NewsBlock';
import BillsRadarBlock from '@/components/digest/BillsRadarBlock';

export default function ArchiveDetailContent() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const [digest, setDigest] = useState<Digest | null>(null);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!loading && !user) router.push('/login');
  }, [user, loading, router]);

  useEffect(() => {
    if (!user) return;
    api.get<DigestSummary[]>('/api/digest/archive')
      .then((archives) => {
        const entry = archives.find(
          (a) => a.year === Number(params.year) && a.month === Number(params.month)
        );
        if (!entry) throw new Error('找不到該月報');
        return api.get<Digest>(`/api/digest/${entry.id}`);
      })
      .then(setDigest)
      .catch((err) => setError(err.message))
      .finally(() => setFetching(false));
  }, [user, params.year, params.month]);

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
      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-4">
          <Link href="/archive" className="text-sm text-blue-600 hover:underline">← 返回歷史彙整</Link>
        </div>
        {error ? (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-600">{error}</div>
        ) : !digest ? null : (
          <>
            <div className="mb-6">
              <h1 className="text-2xl font-bold text-gray-800">
                {digest.year} 年 {digest.month} 月 人資法規月報
              </h1>
              {digest.published_at && (
                <p className="text-sm text-gray-400 mt-1">
                  發布於 {new Date(digest.published_at).toLocaleDateString('zh-TW')}
                </p>
              )}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <LawChangesBlock items={digest.law_changes} />
              <CalendarBlock items={digest.calendar} />
              <NewsBlock items={digest.news} />
              <BillsRadarBlock items={digest.bills} />
            </div>
          </>
        )}
      </main>
    </div>
  );
}
