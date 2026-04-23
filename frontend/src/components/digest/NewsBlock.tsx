'use client';

import { NewsItem } from '@/types';

interface Props {
  items: NewsItem[];
}

export default function NewsBlock({ items }: Props) {
  return (
    <section className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6">
      <h2 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-orange-500 inline-block"></span>
        人資新聞
      </h2>
      {items.length === 0 ? (
        <p className="text-gray-400 text-sm">本月無相關新聞</p>
      ) : (
        <div className="space-y-5">
          {items.map((item, index) => (
            <div key={item.id} className="flex gap-3 sm:gap-4 items-start">
              <span className="text-xl sm:text-2xl font-bold text-orange-200 w-6 sm:w-8 shrink-0 leading-tight">
                {index + 1}
              </span>
              <div className="flex-1">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-medium text-gray-800 hover:text-blue-600 transition text-sm leading-snug"
                >
                  {item.title}
                </a>
                <div className="flex items-center gap-2 mt-1 mb-2">
                  <span className="text-xs text-gray-400">{item.source}</span>
                  <span className="text-xs text-gray-300">·</span>
                  <span className="text-xs text-gray-400">{item.published_date}</span>
                </div>
                {item.ai_summary && (
                  <p className="text-sm text-gray-600 mb-1">{item.ai_summary}</p>
                )}
                {item.ai_action && (
                  <p className="text-sm text-blue-700 bg-blue-50 rounded px-3 py-1.5">
                    <span className="font-semibold">建議行動：</span>{item.ai_action}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
