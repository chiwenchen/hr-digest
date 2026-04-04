'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const AdminCrawlContent = loadDynamic(() => import('@/components/pages/admin/AdminCrawlContent'), { ssr: false });

export default function AdminCrawlPage() {
  return <AdminCrawlContent />;
}
