'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';

export default function Header() {
  const { user, logout } = useAuth();
  const [mounted, setMounted] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

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
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between gap-3">
        <Link href="/" className="text-lg font-bold text-blue-700 shrink-0">HR Digest</Link>

        {/* Desktop nav */}
        <nav className="hidden md:flex flex-1 gap-4 text-sm text-gray-600 ml-4">
          <Link href="/" className="hover:text-blue-600 font-medium">本月摘要</Link>
          <Link href="/archive" className="hover:text-blue-600">歷史彙整</Link>
          <Link href="/settings" className="hover:text-blue-600">訂閱設定</Link>
          {user?.role === 'admin' && (
            <Link href="/admin" className="hover:text-red-600 font-medium text-red-500">管理後台</Link>
          )}
        </nav>

        <div className="hidden md:flex items-center gap-4 text-sm shrink-0">
          <span className="text-gray-600 truncate max-w-[140px]">{user?.name}</span>
          <button
            onClick={logout}
            className="text-gray-400 hover:text-gray-600 transition"
          >
            登出
          </button>
        </div>

        {/* Mobile hamburger */}
        <button
          type="button"
          aria-label="開啟選單"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen((v) => !v)}
          className="md:hidden inline-flex items-center justify-center w-10 h-10 rounded-lg text-gray-600 hover:bg-gray-100"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            {menuOpen ? (
              <>
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </>
            ) : (
              <>
                <line x1="3" y1="6" x2="21" y2="6" />
                <line x1="3" y1="12" x2="21" y2="12" />
                <line x1="3" y1="18" x2="21" y2="18" />
              </>
            )}
          </svg>
        </button>
      </div>

      {/* Mobile dropdown */}
      {menuOpen && (
        <div className="md:hidden border-t border-gray-100 bg-white">
          <nav className="px-4 py-2 flex flex-col text-sm">
            <Link href="/" onClick={() => setMenuOpen(false)} className="py-3 border-b border-gray-50 text-gray-700 font-medium">本月摘要</Link>
            <Link href="/archive" onClick={() => setMenuOpen(false)} className="py-3 border-b border-gray-50 text-gray-700">歷史彙整</Link>
            <Link href="/settings" onClick={() => setMenuOpen(false)} className="py-3 border-b border-gray-50 text-gray-700">訂閱設定</Link>
            {user?.role === 'admin' && (
              <Link href="/admin" onClick={() => setMenuOpen(false)} className="py-3 border-b border-gray-50 text-red-500 font-medium">管理後台</Link>
            )}
            <div className="flex items-center justify-between py-3">
              <span className="text-gray-500 truncate">{user?.name}</span>
              <button
                onClick={() => { setMenuOpen(false); logout(); }}
                className="text-gray-500 hover:text-gray-700 px-3 py-1 rounded border border-gray-200"
              >
                登出
              </button>
            </div>
          </nav>
        </div>
      )}
    </header>
  );
}
