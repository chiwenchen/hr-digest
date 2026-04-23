'use client';

export const dynamic = 'force-dynamic';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/lib/api';

export default function AdminReviewRedirect() {
  const router = useRouter();

  useEffect(() => {
    api.get<{ latest_digest_id: number | null }>('/api/admin/dashboard')
      .then((d) => {
        if (d.latest_digest_id) {
          router.replace(`/admin/digest/${d.latest_digest_id}`);
        } else {
          router.replace('/admin/crawl');
        }
      })
      .catch(() => router.replace('/admin'));
  }, [router]);

  return (
    <div className="p-8 text-gray-400">載入中...</div>
  );
}
