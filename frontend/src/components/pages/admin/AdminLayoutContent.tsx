'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/auth';

const navLinks = [
  { href: '/admin', label: '後台首頁', exact: true },
  { href: '/admin/crawl', label: '爬取新聞' },
  { href: '/admin/bills', label: '法案管理' },
  { href: '/admin/calendar', label: '行事曆管理' },
  { href: '/admin/subscribers', label: '使用者管理' },
];

export default function AdminLayoutContent({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (!loading && (!user || user.role !== 'admin')) {
      router.push('/');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-400">載入中...</p>
      </div>
    );
  }

  if (!user || user.role !== 'admin') return null;

  return (
    <div className="min-h-screen flex bg-gray-50">
      <aside className="w-56 bg-white border-r border-gray-200 flex flex-col">
        <div className="px-6 py-5 border-b border-gray-100">
          <h2 className="font-bold text-gray-800">管理後台</h2>
          <p className="text-xs text-gray-400 mt-0.5">HR Digest</p>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navLinks.map((link) => {
            const active = link.exact ? pathname === link.href : pathname.startsWith(link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`block px-3 py-2 rounded-lg text-sm font-medium transition ${
                  active
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-800'
                }`}
              >
                {link.label}
              </Link>
            );
          })}
        </nav>
        <div className="px-6 py-4 border-t border-gray-100">
          <Link href="/" className="text-xs text-gray-400 hover:text-gray-600">← 返回前台</Link>
        </div>
      </aside>
      <div className="flex-1 overflow-auto">
        {children}
      </div>
    </div>
  );
}
