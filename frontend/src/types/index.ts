export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  email_subscribed: boolean;
}

export interface LawChange {
  id: number;
  law_name: string;
  article_number: string;
  change_summary: string;
  action_items: string[];
}

export interface NewsItem {
  id: number;
  title: string;
  source: string;
  url: string;
  published_date: string;
  ai_summary: string;
  ai_action: string;
  sort_order: number;
  is_approved?: boolean;
}

export interface CalendarItem {
  id: number;
  month: number;
  quarter?: number;
  title: string;
  description?: string;
}

export interface BillItem {
  id: number;
  title: string;
  status: string;
  current_stage?: string;
  expected_timeline?: string;
  impact_summary?: string;
  hr_preparation?: string;
  is_active?: boolean;
}

export interface Digest {
  id: number;
  year: number;
  month: number;
  status: string;
  published_at: string | null;
  law_changes: LawChange[];
  news: NewsItem[];
  calendar: CalendarItem[];
  bills: BillItem[];
}

export interface DigestSummary {
  id: number;
  year: number;
  month: number;
  published_at: string | null;
}
