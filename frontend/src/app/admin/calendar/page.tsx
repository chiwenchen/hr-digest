'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const AdminCalendarContent = loadDynamic(() => import('@/components/pages/admin/AdminCalendarContent'), { ssr: false });

export default function AdminCalendarPage() {
  return <AdminCalendarContent />;
}
