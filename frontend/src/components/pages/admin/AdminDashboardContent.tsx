'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

interface DashboardData {
  latest_digest_id: number | null;
  latest_digest_status: string | null;
  latest_digest_year: number | null;
  latest_digest_month: number | null;
  pending_news_count: number;
}

export default function AdminDashboardContent() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get<DashboardData>('/api/admin/dashboard')
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-4 sm:p-8 flex items-center justify-center">
        <p className="text-gray-400">載入中...</p>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-5 sm:mb-6">後台總覽</h1>
      {error ? (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">{error}</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 sm:p-6">
            <h2 className="font-semibold text-gray-700 mb-3">最新月報</h2>
            {data?.latest_digest_id ? (
              <div>
                <p className="text-gray-800 font-medium">
                  {data.latest_digest_year} 年 {data.latest_digest_month} 月
                </p>
                <span className={`inline-block mt-1 text-xs px-2 py-0.5 rounded-full ${
                  data.latest_digest_status === 'published'
                    ? 'bg-green-100 text-green-700'
                    : 'bg-yellow-100 text-yellow-700'
                }`}>
                  {data.latest_digest_status === 'published' ? '已發布' : '草稿'}
                </span>
                <div className="mt-3">
                  <Link
                    href={`/admin/digest/${data.latest_digest_id}`}
                    className="text-sm text-blue-600 hover:underline"
                  >
                    前往審核 →
                  </Link>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">尚無月報</p>
            )}
          </div>
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 sm:p-6">
            <h2 className="font-semibold text-gray-700 mb-3">待審新聞</h2>
            <p className="text-3xl font-bold text-orange-600">{data?.pending_news_count ?? 0}</p>
            <p className="text-sm text-gray-400 mt-1">則待審核新聞</p>
            {data?.latest_digest_id && (
              <div className="mt-3">
                <Link
                  href={`/admin/digest/${data.latest_digest_id}`}
                  className="text-sm text-blue-600 hover:underline"
                >
                  前往審核 →
                </Link>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
