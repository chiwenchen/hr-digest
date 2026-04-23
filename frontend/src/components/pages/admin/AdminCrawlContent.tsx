'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';

interface DashboardData {
  latest_digest_id: number | null;
  pending_news_count: number;
}

export default function AdminCrawlContent() {
  const [crawling, setCrawling] = useState(false);
  const [message, setMessage] = useState('');
  const [latestId, setLatestId] = useState<number | null>(null);
  const [pendingCount, setPendingCount] = useState<number>(0);

  async function refreshLatest() {
    try {
      const data = await api.get<DashboardData>('/api/admin/dashboard');
      setLatestId(data.latest_digest_id);
      setPendingCount(data.pending_news_count);
    } catch {}
  }

  useEffect(() => {
    refreshLatest();
  }, []);

  async function handleCrawl() {
    setCrawling(true);
    setMessage('');
    try {
      await api.post('/api/admin/crawl');
      setMessage('爬取任務已啟動，系統正在背景執行中，約 1-3 分鐘後完成。');
      // Poll for latest digest until pending_news_count changes
      const deadline = Date.now() + 4 * 60 * 1000;
      const interval = setInterval(async () => {
        await refreshLatest();
        if (Date.now() > deadline) clearInterval(interval);
      }, 5000);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '爬取失敗');
    } finally {
      setCrawling(false);
    }
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-5 sm:mb-6">爬取新聞</h1>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 sm:p-6 lg:p-8 max-w-lg">
        <p className="text-gray-600 mb-2">
          點擊下方按鈕，系統將立即爬取最新勞動法規新聞並進行 AI 摘要分析。
        </p>
        <p className="text-sm text-gray-400 mb-6">
          此操作會在背景執行，通常需要 1-3 分鐘，完成後可在新聞審核頁面查看結果。
        </p>
        <button
          onClick={handleCrawl}
          disabled={crawling}
          className="bg-blue-600 text-white px-6 h-11 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
        >
          {crawling ? (
            <>
              <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              爬取中...
            </>
          ) : (
            '立即爬取新聞'
          )}
        </button>
        {message && (
          <div className={`mt-4 text-sm rounded-lg px-4 py-3 ${
            message.includes('已啟動') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
          }`}>
            {message}
          </div>
        )}

        {latestId && (
          <div className="mt-6 pt-6 border-t border-gray-100">
            <p className="text-sm text-gray-500 mb-2">最新月報（待審 {pendingCount} 則）</p>
            <Link
              href={`/admin/digest/${latestId}`}
              className="inline-flex items-center justify-center bg-green-600 text-white px-5 h-11 rounded-lg font-medium hover:bg-green-700 transition"
            >
              前往新聞審核 →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
