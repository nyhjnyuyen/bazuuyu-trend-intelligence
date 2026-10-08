export const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export interface KeyEntities {
  companies?: string[];
  products?: string[];
  people?: string[];
}

export interface Trend {
  rank: number;
  title: string;
  description: string;
  key_entities?: KeyEntities;
  sentiment?: "positive" | "negative" | "mixed" | string;
  importance?: string;
  references?: string[];
}

export interface WeekResult {
  week_number: number;
  week_label: string;
  post_count: number;
  clusters_found: number;
  noise_posts: number;
  trends: Trend[];
}

export interface TrendResponse {
  niche: string;
  week: number | null;
  results: WeekResult[];
}

export interface NicheSummary {
  niche: string;
  total_posts: number;
  weeks_available: number[];
  total_trends: number;
}

export interface NichesResponse {
  generated_at?: string;
  model?: string;
  niches: NicheSummary[];
}

export interface FutureOpportunity {
  ip: string;
  title: string;
  release_date: string | null;

  momentum_score: number | null;
  momentum_class: string | null;
  signal_profile: string | null;

  timing_score: number | null;
  action_timing: string | null;
  days_to_release: number | null;
  days_since_toy_activity: number | null;

  opportunity_score: number | null;
  opportunity_class: string | null;

  fit_score: number;
  fit_level: string;
  fit_signals: string[];
  character_count: number;
  animal_matches: string[];

  final_score: number | null;
  final_priority: string;

  recommended_action: string | null;
  recommendation_summary: string | null;
}

export interface FutureOpportunitiesResponse {
  generated_at: string;
  source_snapshot: string;
  candidate_count: number;
  results: FutureOpportunity[];
}

export const nicheMeta: Record<string, { emoji: string; label: string }> = {
  technology: { emoji: "🖥", label: "Technology" },
  science: { emoji: "🔬", label: "Science" },
  worldnews: { emoji: "🌍", label: "World News" },
  gaming: { emoji: "🎮", label: "Gaming" },
  smartphones: { emoji: "📱", label: "Smartphones" },
  movies: { emoji: "🎬", label: "Movies" },
};

export function getNicheLabel(niche: string) {
  return nicheMeta[niche]?.label ?? niche.replace(/-/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export async function fetchNiches(signal?: AbortSignal) {
  const response = await fetch(`${API_BASE}/api/v1/niches`, {
    signal,
    headers: { accept: "application/json" },
  });
  if (!response.ok) throw new Error(`Could not load niches (${response.status})`);
  return (await response.json()) as NichesResponse;
}

export async function fetchTrends(niche: string, week?: string | number, signal?: AbortSignal) {
  const weekQuery = week === undefined ? "" : `?week=${week}`;
  const response = await fetch(`${API_BASE}/api/v1/trends/${encodeURIComponent(niche)}${weekQuery}`, {
    signal,
    headers: { accept: "application/json" },
  });
  if (!response.ok) throw new Error(`Could not load trends (${response.status})`);
  return (await response.json()) as TrendResponse;
}

export async function fetchFutureOpportunities(
  signal?: AbortSignal,
) {
  const response = await fetch(
    `${API_BASE}/api/v1/future-opportunities`,
    {
      signal,
      headers: {
        accept: "application/json",
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Could not load future opportunities (${response.status})`,
    );
  }

  return (
    await response.json()
  ) as FutureOpportunitiesResponse;
}
