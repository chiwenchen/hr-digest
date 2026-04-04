'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const AdminDigestContent = loadDynamic(() => import('@/components/pages/admin/AdminDigestContent'), { ssr: false });

export default function AdminDigestPage() {
  return <AdminDigestContent />;
}
