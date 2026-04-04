'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const AdminBillsContent = loadDynamic(() => import('@/components/pages/admin/AdminBillsContent'), { ssr: false });

export default function AdminBillsPage() {
  return <AdminBillsContent />;
}
