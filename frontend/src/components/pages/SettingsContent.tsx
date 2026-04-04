'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { api } from '@/lib/api';
import Header from '@/components/layout/Header';

export default function SettingsContent() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [subscribed, setSubscribed] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!loading && !user) router.push('/login');
  }, [user, loading, router]);

  useEffect(() => {
    if (user) setSubscribed(user.email_subscribed);
  }, [user]);

  async function handleToggle() {
    const newValue = !subscribed;
    setSaving(true);
    setMessage('');
    try {
      await api.patch('/api/auth/settings', { email_subscribed: newValue });
      setSubscribed(newValue);
      setMessage(newValue ? '已開啟電子報訂閱' : '已關閉電子報訂閱');
    } catch (err) {
      setMessage(err instanceof Error ? err.message : '儲存失敗');
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-400">載入中...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="max-w-xl mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold text-gray-800 mb-6">訂閱設定</h1>
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-800">月報電子報</p>
              <p className="text-sm text-gray-500 mt-0.5">每月月報發布時，寄送到 {user?.email}</p>
            </div>
            <button
              onClick={handleToggle}
              disabled={saving}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none ${
                subscribed ? 'bg-blue-600' : 'bg-gray-300'
              } disabled:opacity-50`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  subscribed ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
          {message && (
            <p className="mt-4 text-sm text-green-600 bg-green-50 rounded px-3 py-2">{message}</p>
          )}
        </div>
      </main>
    </div>
  );
}
