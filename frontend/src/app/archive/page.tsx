'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const ArchiveContent = loadDynamic(() => import('@/components/pages/ArchiveContent'), { ssr: false });

export default function ArchivePage() {
  return <ArchiveContent />;
}
