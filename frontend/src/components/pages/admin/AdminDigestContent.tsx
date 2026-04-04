'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import { api } from '@/lib/api';
import { Digest, NewsItem } from '@/types';

export default function AdminDigestContent() {
  const params = useParams();
  const digestId = params.id;
  const [digest, setDigest] = useState<Digest | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [publishing, setPublishing] = useState(false);
  const [publishMessage, setPublishMessage] = useState('');

  useEffect(() => {
    api.get<Digest>(`/api/digest/${digestId}`)
      .then(setDigest)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [digestId]);

  async function handleApprove(newsId: number) {
    await api.patch(`/api/admin/news/${newsId}/approve`);
    setDigest((prev) => prev ? {
      ...prev,
      news: prev.news.map((n) => n.id === newsId ? { ...n, is_approved: true } : n),
    } : prev);
  }

  async function handleReject(newsId: number) {
    await api.patch(`/api/admin/news/${newsId}/reject`);
    setDigest((prev) => prev ? {
      ...prev,
      news: prev.news.filter((n) => n.id !== newsId),
    } : prev);
  }

  async function handleUpdateOrder(newsId: number, order: number) {
    await api.patch(`/api/admin/news/${newsId}/order`, { sort_order: order });
    setDigest((prev) => prev ? {
      ...prev,
      news: prev.news.map((n) => n.id === newsId ? { ...n, sort_order: order } : n),
    } : prev);
  }

  async function handlePublish() {
    setPublishing(true);
    setPublishMessage('');
    try {
      await api.post(`/api/admin/digest/${digestId}/publish`);
      setPublishMessage('月報已成功發布！');
      setDigest((prev) => prev ? { ...prev, status: 'published' } : prev);
    } catch (err) {
      setPublishMessage(err instanceof Error ? err.message : '發布失敗');
    } finally {
      setPublishing(false);
    }
  }

  if (loading) {
    return (
      <div className="p-8 flex items-center justify-center">
        <p className="text-gray-400">載入中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-600 text-sm">{error}</div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-800">
            {digest?.year} 年 {digest?.month} 月 — 新聞審核
          </h1>
          <span className={`inline-block mt-1 text-xs px-2 py-0.5 rounded-full ${
            digest?.status === 'published' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'
          }`}>
            {digest?.status === 'published' ? '已發布' : '草稿'}
          </span>
        </div>
        {digest?.status !== 'published' && (
          <button
            onClick={handlePublish}
            disabled={publishing}
            className="bg-green-600 text-white px-5 py-2 rounded-lg font-medium hover:bg-green-700 transition disabled:opacity-50"
          >
            {publishing ? '發布中...' : '發布月報'}
          </button>
        )}
      </div>

      {publishMessage && (
        <div className={`mb-4 text-sm rounded-lg px-4 py-3 ${
          publishMessage.includes('成功') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-600'
        }`}>
          {publishMessage}
        </div>
      )}

      <div className="space-y-4">
        {digest?.news.length === 0 ? (
          <div className="bg-gray-100 rounded-xl p-6 text-gray-500 text-sm">尚無新聞</div>
        ) : (
          digest?.news.map((item: NewsItem) => (
            <div
              key={item.id}
              className={`bg-white rounded-xl border shadow-sm p-5 ${
                item.is_approved === false ? 'border-red-200 opacity-60' : 'border-gray-100'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <a
                    href={item.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-gray-800 hover:text-blue-600 text-sm"
                  >
                    {item.title}
                  </a>
                  <div className="flex items-center gap-2 mt-1 mb-2">
                    <span className="text-xs text-gray-400">{item.source}</span>
                    <span className="text-xs text-gray-300">·</span>
                    <span className="text-xs text-gray-400">{item.published_date}</span>
                    {item.is_approved && (
                      <span className="text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">已核准</span>
                    )}
                  </div>
                  {item.ai_summary && <p className="text-xs text-gray-600">{item.ai_summary}</p>}
                </div>
                <div className="flex flex-col gap-2 shrink-0">
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleApprove(item.id)}
                      className="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full hover:bg-green-200 transition"
                    >
                      核准
                    </button>
                    <button
                      onClick={() => handleReject(item.id)}
                      className="text-xs bg-red-100 text-red-700 px-3 py-1 rounded-full hover:bg-red-200 transition"
                    >
                      拒絕
                    </button>
                  </div>
                  <div className="flex items-center gap-1">
                    <span className="text-xs text-gray-400">順序</span>
                    <input
                      type="number"
                      defaultValue={item.sort_order}
                      className="w-14 text-xs border border-gray-200 rounded px-2 py-1"
                      onBlur={(e) => handleUpdateOrder(item.id, Number(e.target.value))}
                    />
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
