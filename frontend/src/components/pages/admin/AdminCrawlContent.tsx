'use client';

import { useState } from 'react';
import { api } from '@/lib/api';

export default function AdminCrawlContent() {
  const [crawling, setCrawling] = useState(false);
  const [message, setMessage] = useState('');

  async function handleCrawl() {
    setCrawling(true);
    setMessage('');
    try {
      await api.post('/api/admin/crawl');
      setMessage('爬取任務已啟動，系統正在背景執行中，請稍後查看最新月報。');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '爬取失敗');
    } finally {
      setCrawling(false);
    }
  }

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">爬取新聞</h1>
      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-8 max-w-lg">
        <p className="text-gray-600 mb-2">
          點擊下方按鈕，系統將立即爬取最新勞動法規新聞並進行 AI 摘要分析。
        </p>
        <p className="text-sm text-gray-400 mb-6">
          此操作會在背景執行，通常需要 1-3 分鐘，完成後可在新聞審核頁面查看結果。
        </p>
        <button
          onClick={handleCrawl}
          disabled={crawling}
          className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition disabled:opacity-50 flex items-center gap-2"
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
      </div>
    </div>
  );
}
