'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { BillItem } from '@/types';

const STATUS_OPTIONS = [
  { value: 'pending', label: '待審議' },
  { value: 'reviewing', label: '審議中' },
  { value: 'passed', label: '已通過' },
  { value: 'rejected', label: '已否決' },
];

const emptyForm = {
  title: '',
  status: 'pending',
  current_stage: '',
  expected_timeline: '',
  impact_summary: '',
  hr_preparation: '',
};

export default function AdminBillsContent() {
  const [bills, setBills] = useState<BillItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [form, setForm] = useState(emptyForm);
  const [editing, setEditing] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.get<BillItem[]>('/api/admin/bills')
      .then(setBills)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function handleSave() {
    setSaving(true);
    setMessage('');
    try {
      if (editing !== null) {
        const updated = await api.patch<BillItem>(`/api/admin/bills/${editing}`, form);
        setBills((prev) => prev.map((b) => b.id === editing ? updated : b));
        setMessage('法案已更新');
      } else {
        const created = await api.post<BillItem>('/api/admin/bills', form);
        setBills((prev) => [...prev, created]);
        setMessage('法案已新增');
      }
      setForm(emptyForm);
      setEditing(null);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '儲存失敗');
    } finally {
      setSaving(false);
    }
  }

  function handleEdit(bill: BillItem) {
    setEditing(bill.id);
    setForm({
      title: bill.title,
      status: bill.status,
      current_stage: bill.current_stage || '',
      expected_timeline: bill.expected_timeline || '',
      impact_summary: bill.impact_summary || '',
      hr_preparation: bill.hr_preparation || '',
    });
  }

  if (loading) {
    return <div className="p-4 sm:p-8 text-gray-400">載入中...</div>;
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8">
      <h1 className="text-xl sm:text-2xl font-bold text-gray-800 mb-5 sm:mb-6">法案管理</h1>
      {error && <div className="mb-4 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg p-3">{error}</div>}

      <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 sm:p-6 mb-6">
        <h2 className="font-semibold text-gray-700 mb-4">{editing !== null ? '編輯法案' : '新增法案'}</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">法案名稱 *</label>
            <input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">狀態</label>
            <select
              value={form.status}
              onChange={(e) => setForm({ ...form, status: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {STATUS_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>{opt.label}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">目前階段</label>
            <input
              value={form.current_stage}
              onChange={(e) => setForm({ ...form, current_stage: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">預計時程</label>
            <input
              value={form.expected_timeline}
              onChange={(e) => setForm({ ...form, expected_timeline: e.target.value })}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">影響摘要</label>
            <textarea
              value={form.impact_summary}
              onChange={(e) => setForm({ ...form, impact_summary: e.target.value })}
              rows={2}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-1">HR 準備建議</label>
            <textarea
              value={form.hr_preparation}
              onChange={(e) => setForm({ ...form, hr_preparation: e.target.value })}
              rows={2}
              className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
        <div className="flex gap-3 mt-4">
          <button
            onClick={handleSave}
            disabled={saving || !form.title}
            className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50"
          >
            {saving ? '儲存中...' : editing !== null ? '更新' : '新增'}
          </button>
          {editing !== null && (
            <button
              onClick={() => { setEditing(null); setForm(emptyForm); }}
              className="text-gray-500 px-5 py-2 rounded-lg text-sm border border-gray-200 hover:bg-gray-50"
            >
              取消
            </button>
          )}
        </div>
        {message && (
          <p className="mt-3 text-sm text-green-600 bg-green-50 rounded px-3 py-2">{message}</p>
        )}
      </div>

      <div className="space-y-3">
        {bills.map((bill) => (
          <div key={bill.id} className="bg-white rounded-xl border border-gray-100 shadow-sm p-4 flex items-start justify-between gap-3 sm:gap-4">
            <div className="min-w-0 flex-1">
              <p className="font-medium text-gray-800 text-sm">{bill.title}</p>
              <p className="text-xs text-gray-400 mt-0.5">{bill.status}</p>
            </div>
            <button
              onClick={() => handleEdit(bill)}
              className="text-xs text-blue-600 hover:underline shrink-0"
            >
              編輯
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
