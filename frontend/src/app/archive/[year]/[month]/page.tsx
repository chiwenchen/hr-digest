'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const ArchiveDetailContent = loadDynamic(() => import('@/components/pages/ArchiveDetailContent'), { ssr: false });

export default function ArchiveDetailPage() {
  return <ArchiveDetailContent />;
}
