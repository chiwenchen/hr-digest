'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const AdminLayoutContent = loadDynamic(() => import('@/components/pages/admin/AdminLayoutContent'), { ssr: false });

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <AdminLayoutContent>{children}</AdminLayoutContent>;
}
