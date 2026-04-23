'use client';

import { CalendarItem } from '@/types';

interface Props {
  items: CalendarItem[];
}

const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];

export default function CalendarBlock({ items }: Props) {
  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-green-500 inline-block"></span>
        重要日曆
      </h2>
      {items.length === 0 ? (
        <p className="text-gray-400 text-sm">本月無重要事項</p>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="flex gap-4 items-start">
              <span className="text-xs font-bold text-green-600 bg-green-50 px-2 py-1 rounded min-w-[40px] text-center">
                {monthNames[(item.month - 1) % 12]}
              </span>
              <div>
                <p className="text-sm font-medium text-gray-800">{item.title}</p>
                {item.description && (
                  <p className="text-xs text-gray-500 mt-0.5">{item.description}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
