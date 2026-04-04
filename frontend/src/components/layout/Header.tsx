'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';

export default function Header() {
  const { user, logout } = useAuth();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <header className="bg-white border-b border-gray-200 shadow-sm h-14" />
    );
  }

  return (
    <header className="bg-white border-b border-gray-200 shadow-sm">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-6">
          <Link href="/" className="text-lg font-bold text-blue-700">HR Digest</Link>
          <nav className="flex gap-4 text-sm text-gray-600">
            <Link href="/" className="hover:text-blue-600 font-medium">本月摘要</Link>
            <Link href="/archive" className="hover:text-blue-600">歷史彙整</Link>
            <Link href="/settings" className="hover:text-blue-600">訂閱設定</Link>
            {user?.role === 'admin' && (
              <Link href="/admin" className="hover:text-red-600 font-medium text-red-500">管理後台</Link>
            )}
          </nav>
        </div>
        <div className="flex items-center gap-4 text-sm">
          <span className="text-gray-600">{user?.name}</span>
          <button
            onClick={logout}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            登出
          </button>
        </div>
      </div>
    </header>
  );
}
