'use client';

import { LawChange } from '@/types';

interface Props {
  items: LawChange[];
}

export default function LawChangesBlock({ items }: Props) {
  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-blue-500 inline-block"></span>
        法條異動
      </h2>
      {items.length === 0 ? (
        <p className="text-gray-400 text-sm">本月無法條異動</p>
      ) : (
        <div className="space-y-5">
          {items.map((item) => (
            <div key={item.id} className="border-l-4 border-blue-200 pl-4">
              <div className="flex items-baseline gap-2 mb-1">
                <span className="font-medium text-gray-800">{item.law_name}</span>
                <span className="text-xs text-gray-500 bg-gray-100 px-2 py-0.5 rounded">{item.article_number}</span>
              </div>
              <p className="text-sm text-gray-600 mb-2">{item.change_summary}</p>
              {item.action_items && item.action_items.length > 0 && (
                <div>
                  <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">行動項目</p>
                  <ul className="space-y-1">
                    {item.action_items.map((action, i) => (
                      <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                        <span className="text-blue-400 mt-0.5">•</span>
                        <span>{action}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
