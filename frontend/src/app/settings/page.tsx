'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const SettingsContent = loadDynamic(() => import('@/components/pages/SettingsContent'), { ssr: false });

export default function SettingsPage() {
  return <SettingsContent />;
}
