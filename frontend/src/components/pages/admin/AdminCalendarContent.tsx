'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { CalendarItem } from '@/types';

const emptyForm = { month: 1, title: '', description: '' };

export default function AdminCalendarContent() {
  const [items, setItems] = useState<CalendarItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.get<CalendarItem[]>('/api/admin/calendar')
      .then(setItems)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleAdd() {
    setSaving(true);
    setMessage('');
    try {
      const created = await api.post<CalendarItem>('/api/admin/calendar', {
        month: form.month,
        title: form.title,
        description: form.description || undefined,
      });
      setItems((prev) => [...prev, created]);
      setForm(emptyForm);
      setMessage('行事曆項目已新增');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '新增失敗');
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('確定要刪除此項目？')) return;
    try {
      await api.delete(`/api/admin/calendar/${id}`);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : '刪除失敗');
    }
  }

  if (loading) {
    return <div className="p-4 sm:p-8 text-gray-400">載入中...</div>;
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-5 sm:mb-6">行事曆管理</h1>
      {error && <div className="mb-4 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg p-3">{error}</div>}

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 sm:p-6 mb-6">
        <h2 className="font-semibold text-gray-700 mb-4">新增項目</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">月份</label>
            <select
              value={form.month}
              onChange={(e) => setForm({ ...form, month: Number(e.target.value) })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
                <option key={m} value={m}>{m} 月</option>
              ))}
            </select>
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">標題 *</label>
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="md:col-span-3">
            <label className="block text-sm font-medium text-gray-700 mb-1">說明（選填）</label>
            <input
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <button
          onClick={handleAdd}
          disabled={saving || !form.title}
          className="mt-4 bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50"
        >
          {saving ? '新增中...' : '新增'}
        </button>
        {message && (
          <p className="mt-3 text-sm text-green-600 bg-green-50 rounded px-3 py-2">{message}</p>
        )}
      </div>

      <div className="space-y-3">
        {items.length === 0 ? (
          <div className="bg-gray-100 rounded-xl p-6 text-gray-500 text-sm">尚無行事曆項目</div>
        ) : (
          items.map((item) => (
            <div key={item.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-start sm:items-center justify-between gap-3 sm:gap-4">
              <div className="flex items-center gap-3 sm:gap-4 min-w-0 flex-1">
                <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-1 rounded min-w-[40px] text-center">
                  {item.month} 月
                </span>
                <div>
                  <p className="font-medium text-gray-800 text-sm">{item.title}</p>
                  {item.description && <p className="text-xs text-gray-400 mt-0.5">{item.description}</p>}
                </div>
              </div>
              <button
                onClick={() => handleDelete(item.id)}
                className="text-xs text-red-500 hover:underline shrink-0"
              >
                刪除
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
