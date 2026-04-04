'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const AdminDashboardContent = loadDynamic(() => import('@/components/pages/admin/AdminDashboardContent'), { ssr: false });

export default function AdminDashboardPage() {
  return <AdminDashboardContent />;
}
