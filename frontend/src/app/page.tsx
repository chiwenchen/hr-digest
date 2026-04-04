'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const HomeContent = loadDynamic(() => import('@/components/pages/HomeContent'), { ssr: false });

export default function HomePage() {
  return <HomeContent />;
}
