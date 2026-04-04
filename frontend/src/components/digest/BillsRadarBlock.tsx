'use client';

import { BillItem } from '@/types';

interface Props {
  items: BillItem[];
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-700',
  passed: 'bg-green-100 text-green-700',
  rejected: 'bg-red-100 text-red-700',
  reviewing: 'bg-blue-100 text-blue-700',
};

const statusLabels: Record<string, string> = {
  pending: '待審議',
  passed: '已通過',
  rejected: '已否決',
  reviewing: '審議中',
};

export default function BillsRadarBlock({ items }: Props) {
  const activeItems = items.filter((b) => b.is_active !== false);

  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-purple-500 inline-block"></span>
        法案雷達
      </h2>
      {activeItems.length === 0 ? (
        <p className="text-gray-400 text-sm">目前無追蹤中的法案</p>
      ) : (
        <div className="space-y-4">
          {activeItems.map((bill) => (
            <div key={bill.id} className="border border-gray-100 rounded-lg p-4">
              <div className="flex items-start justify-between gap-2 mb-2">
                <h3 className="font-medium text-gray-800 text-sm">{bill.title}</h3>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium shrink-0 ${statusColors[bill.status] || 'bg-gray-100 text-gray-600'}`}>
                  {statusLabels[bill.status] || bill.status}
                </span>
              </div>
              {bill.current_stage && (
                <p className="text-xs text-gray-500 mb-1">目前階段：{bill.current_stage}</p>
              )}
              {bill.expected_timeline && (
                <p className="text-xs text-gray-500 mb-1">預計時程：{bill.expected_timeline}</p>
              )}
              {bill.impact_summary && (
                <p className="text-sm text-gray-600 mb-2">{bill.impact_summary}</p>
              )}
              {bill.hr_preparation && (
                <p className="text-sm text-purple-700 bg-purple-50 rounded px-3 py-1.5">
                  <span className="font-semibold">HR 準備：</span>{bill.hr_preparation}
                </p>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
