'use client';

export const dynamic = 'force-dynamic';

import loadDynamic from "next/dynamic";;

const LoginContent = loadDynamic(() => import('@/components/pages/LoginContent'), { ssr: false });

export default function LoginPage() {
  return <LoginContent />;
}
