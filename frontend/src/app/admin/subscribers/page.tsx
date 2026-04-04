'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const AdminSubscribersContent = loadDynamic(() => import('@/components/pages/admin/AdminSubscribersContent'), { ssr: false });

export default function AdminSubscribersPage() {
  return <AdminSubscribersContent />;
}
