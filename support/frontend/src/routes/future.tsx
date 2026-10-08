import { Link, createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import {
  ArrowLeft,
  ChevronDown,
  RefreshCw,
} from "lucide-react";
import {
  fetchFutureOpportunities,
  type FutureOpportunity,
} from "@/lib/trend-api";

export const Route = createFileRoute("/future")({
  component: FuturePage,
  head: () => ({
    meta: [
      { title: "Bazuuyu — What's Next?" },
      {
        name: "description",
        content: "Explore future character and entertainment opportunities.",
      },
    ],
  }),
});

const filters = [
  ["ALL", "Everything"],
  ["TOP_PRIORITY", "Top priority"],
  ["HIGH_PRIORITY", "High priority"],
  ["WATCH", "Watch"],
  ["LOW_PRIORITY", "Low priority"],
  ["IGNORE_FOR_NOW", "Later"],
  ["WATCHLIST", "High-fit watchlist"],
  ["PENDING", "Pending history"],
] as const;

type Filter = (typeof filters)[number][0];

function label(value?: string | null) {
  return value
    ? value.replaceAll("_", " ").toLowerCase().replace(/\b\w/g, (c) => c.toUpperCase())
    : "Pending";
}

function score(value?: number | null) {
  return typeof value === "number" && Number.isFinite(value)
    ? value.toFixed(1)
    : "—";
}

function releaseDate(value: string | null) {
  if (!value) return "Not announced";
  const date = new Date(`${value.slice(0, 10)}T00:00:00`);
  if (Number.isNaN(date.getTime())) return "Not announced";
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function priorityStyle(priority: string) {
  switch (priority) {
    case "TOP_PRIORITY":
      return "bg-[#ffe0e5] text-[#a62f4d]";
    case "HIGH_PRIORITY":
      return "bg-[#ffedcb] text-[#86581a]";
    case "WATCH":
      return "bg-[#e4eddf] text-[#456740]";
    default:
      return "bg-[#eee9e3] text-[#71685f]";
  }
}

function FuturePage() {
  const [results, setResults] = useState<FutureOpportunity[]>([]);
  const [generatedAt, setGeneratedAt] = useState<string>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Filter>("ALL");
  const [query, setQuery] = useState("");
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const payload = await fetchFutureOpportunities(controller.signal);
        if (controller.signal.aborted) return;
        setResults(payload.results);
        setGeneratedAt(payload.generated_at);
      } catch (caught) {
        if (!controller.signal.aborted) {
          setError(
            caught instanceof Error
              ? caught.message
              : "The report could not be loaded.",
          );
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    void load();
    return () => controller.abort();
  }, [reloadKey]);

  const ranked = useMemo(
    () =>
      results
        .filter((item) => item.final_score != null)
        .sort((a, b) => (b.final_score ?? 0) - (a.final_score ?? 0)),
    [results],
  );

  const pending = results.filter((item) => item.final_score == null);
  const watchlist = pending.filter((item) => item.fit_score >= 75);
  const ordered = [...ranked, ...pending];

  const visible = ordered.filter((item) => {
    const matchesFilter =
      filter === "ALL" ||
      (filter === "PENDING" && item.final_score == null) ||
      (filter === "WATCHLIST" &&
        item.final_score == null &&
        item.fit_score >= 75) ||
      item.final_priority === filter;

    const text = `${item.ip} ${item.title}`.toLowerCase();
    return matchesFilter && text.includes(query.trim().toLowerCase());
  });

  const updated = generatedAt ? new Date(generatedAt) : null;

  return (
    <main
      className="min-h-screen bg-[#faf6ee] text-[#42362f]"
      style={{
        fontFamily: '"Avenir Next", "Nunito", "Trebuchet MS", sans-serif',
        colorScheme: "light",
      }}
    >
      <header className="border-b border-[#e8dfd3]">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-5 sm:px-8">
          <Link to="/" className="flex items-center gap-3">
            <span
              aria-hidden="true"
              className="flex h-10 w-10 rotate-[-8deg] items-center justify-center rounded-2xl bg-[#f7b9c5] text-xl"
            >
              ✿
            </span>
            <span className="text-xl font-black tracking-tight">bazuuyu</span>
          </Link>
          <Link
            to="/"
            className="flex items-center gap-2 text-sm font-semibold text-[#75665c] hover:text-[#a62f4d]"
          >
            <ArrowLeft size={15} />
            All trends
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-6xl px-5 pb-16 pt-10 sm:px-8">
        <div className="mb-8 flex flex-wrap items-end justify-between gap-6">
          <div>
            <p className="mb-3 text-xs font-bold uppercase tracking-[0.18em] text-[#976650]">
              The Bazuuyu lookout
            </p>
            <h1 className="text-4xl font-black tracking-tight sm:text-5xl">
              What&apos;s next?
              <span aria-hidden="true" className="ml-3 text-[#d65c78]">✳</span>
            </h1>
            <p className="mt-3 max-w-lg text-sm leading-6 text-[#75665c]">
              Meet the characters and stories worth watching.
              Find your next research idea here.
            </p>
          </div>

          <div className="flex items-center gap-3">
            {updated && !Number.isNaN(updated.getTime()) && (
              <p className="text-xs text-[#75665c]">
                Report · {updated.toLocaleDateString(undefined, {
                  month: "short",
                  day: "numeric",
                })}
              </p>
            )}
            <button
              type="button"
              disabled={loading}
              onClick={() => setReloadKey((value) => value + 1)}
              className="flex items-center gap-2 rounded-xl border border-[#dacfc2] bg-[#fffdf8] px-3 py-2 text-xs font-bold hover:bg-[#f3ebdf] disabled:opacity-50"
            >
              <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
              Refresh report
            </button>
          </div>
        </div>

        {!loading && !error && (
          <div className="mb-8 flex flex-wrap gap-x-7 gap-y-3 border-y border-[#e8dfd3] py-4 text-sm">
            <Count
              value={ranked.filter((item) => item.final_priority === "TOP_PRIORITY").length}
              text="top priority"
              color="#b83e5b"
            />
            <Count
              value={ranked.filter((item) => item.final_priority === "HIGH_PRIORITY").length}
              text="high priority"
              color="#86581a"
            />
            <Count
              value={ranked.filter((item) => item.final_priority === "WATCH").length}
              text="to watch"
              color="#456740"
            />
            <Count value={watchlist.length} text="high-fit, awaiting history" color="#75665c" />
          </div>
        )}

        <div className="mb-5 flex flex-col justify-between gap-4">
          <div className="flex flex-wrap gap-1">
            {filters.map(([value, text]) => (
              <button
                type="button"
                key={value}
                aria-pressed={filter === value}
                onClick={() => setFilter(value)}
                className={`rounded-lg px-3 py-2 text-xs font-bold transition ${
                  filter === value
                    ? "bg-[#42362f] text-[#fffdf8]"
                    : "text-[#75665c] hover:bg-[#eee6db]"
                }`}
              >
                {text}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-xs text-[#75665c]">
              {loading ? "Opening the lookout…" : `${visible.length} opportunities`}
            </p>
            <input
              type="search"
              aria-label="Search IPs and movie titles"
              placeholder="Find a character or story…"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              className="w-full rounded-xl border border-[#dacfc2] bg-[#fffdf8] px-4 py-2.5 text-sm outline-none placeholder:text-[#93867b] focus:border-[#c75370] focus:ring-2 focus:ring-[#f7d8df] sm:w-72"
            />
          </div>
        </div>

        <section className="overflow-hidden rounded-2xl border border-[#e4d9cb] bg-[#fffdf8]">
          {loading ? (
            <p role="status" className="p-10 text-center text-sm text-[#75665c]">
              Loading the latest saved report…
            </p>
          ) : error ? (
            <div role="alert" className="p-8">
              <p className="font-bold">We couldn&apos;t open the report.</p>
              <p className="mt-2 text-sm text-[#75665c]">{error}</p>
              <button
                type="button"
                onClick={() => setReloadKey((value) => value + 1)}
                className="mt-4 rounded-lg bg-[#42362f] px-4 py-2 text-sm font-bold text-white"
              >
                Try again
              </button>
            </div>
          ) : visible.length === 0 ? (
            <div className="p-12 text-center">
              <span aria-hidden="true" className="text-3xl text-[#d65c78]">✿</span>
              <p className="mt-3 font-bold">Nothing here just yet.</p>
              <p className="mt-2 text-sm text-[#75665c]">
                {results.length === 0
                  ? "No opportunities are available in this report."
                  : "Try another filter or search term."}
              </p>
            </div>
          ) : (
            <>
              <div className="hidden grid-cols-[minmax(0,2fr)_1fr_1fr_1fr_1.2fr_24px] gap-4 border-b border-[#e8dfd3] bg-[#f5efe5] px-6 py-3 text-[11px] font-bold uppercase tracking-wider text-[#75665c] md:grid">
                <span>Character / story</span>
                <span>Release</span>
                <span>Momentum</span>
                <span>Product fit</span>
                <span>Priority</span>
                <span />
              </div>
              {visible.map((item) => (
                <OpportunityRow
                  key={`${item.ip}:${item.title}`}
                  item={item}
                  rank={item.final_score == null ? null : ranked.indexOf(item) + 1}
                />
              ))}
            </>
          )}
        </section>

        <p className="mt-4 text-xs leading-5 text-[#75665c]">
          Open an opportunity to explore its recommendation.
          Refresh loads the latest saved report.
        </p>
      </div>
    </main>
  );
}

function Count({
  value,
  text,
  color,
}: {
  value: number;
  text: string;
  color: string;
}) {
  return (
    <span className="text-[#75665c]">
      <strong className="mr-1.5 text-lg" style={{ color }}>{value}</strong>
      {text}
    </span>
  );
}

function OpportunityRow({
  item,
  rank,
}: {
  item: FutureOpportunity;
  rank: number | null;
}) {
  return (
    <details className="group border-b border-[#eee5da] last:border-b-0">
      <summary className="grid cursor-pointer list-none grid-cols-[minmax(0,1fr)_24px] items-center gap-4 px-5 py-5 transition hover:bg-[#faf3e9] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#c75370] md:grid-cols-[minmax(0,2fr)_1fr_1fr_1fr_1.2fr_24px] md:px-6 [&::-webkit-details-marker]:hidden">
        <div className="min-w-0">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-[#9c8878]">
              {rank === null ? "✿" : String(rank).padStart(2, "0")}
            </span>
            <h2 className="text-base font-extrabold">{item.ip}</h2>
          </div>
          <p className="mt-1 truncate text-xs text-[#75665c]">{item.title}</p>
          <p className="mt-2 text-xs font-semibold text-[#a62f4d] md:hidden">
            {label(item.final_priority)} · Fit {score(item.fit_score)}/100
          </p>
        </div>
        <p className="hidden text-xs font-semibold md:block">
          {releaseDate(item.release_date)}
        </p>
        <div className="hidden md:block">
          <p className="text-sm font-bold">{label(item.momentum_class)}</p>
          <p className="mt-1 text-xs text-[#75665c]">{score(item.momentum_score)}</p>
        </div>
        <div className="hidden md:block">
          <p className="text-sm font-bold">{score(item.fit_score)}<span className="text-xs font-normal text-[#75665c]">/100</span></p>
          <p className="mt-1 text-xs text-[#75665c]">{label(item.fit_level)}</p>
        </div>
        <div className="hidden md:block">
          <span className={`inline-block rounded-md px-2 py-1 text-[11px] font-bold ${priorityStyle(item.final_priority)}`}>
            {label(item.final_priority)}
          </span>
        </div>
        <ChevronDown
          size={17}
          className="text-[#9c8878] transition-transform group-open:rotate-180"
        />
      </summary>

      <div className="border-t border-[#eee5da] bg-[#faf5ed] px-5 py-6 md:px-6">
        <div className="grid gap-6 md:grid-cols-[2fr_1fr]">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-wider text-[#976650]">
              Next step
            </p>
            <h3 className="mt-2 text-lg font-extrabold">
              {label(item.recommended_action)}
            </h3>
            <p className="mt-2 max-w-xl text-sm leading-6 text-[#75665c]">
              {item.recommendation_summary ||
                "More historical observations are needed to evaluate this opportunity."}
            </p>
            <ToyEvidenceDetails evidence={item.toy_evidence} />
            {(item.fit_signals ?? []).length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {item.fit_signals.map((signal) => (
                  <span key={signal} className="rounded-md border border-[#ded3c4] px-2 py-1 text-[11px] text-[#75665c]">
                    {label(signal)}
                  </span>
                ))}
              </div>
            )}
          </div>
          <dl className="grid grid-cols-2 gap-x-4 gap-y-3 text-xs">
            <dt className="text-[#75665c]">Final score</dt>
            <dd className="font-bold">{score(item.final_score)}</dd>
            <dt className="text-[#75665c]">Signal</dt>
            <dd className="font-bold">{label(item.signal_profile)}</dd>
            <dt className="text-[#75665c]">Timing</dt>
            <dd className={`font-bold ${item.action_timing === "ACT_NOW" ? "text-[#a62f4d]" : ""}`}>
              {label(item.action_timing)}
            </dd>
            <dt className="text-[#75665c]">Release</dt>
            <dd className="font-bold">{releaseDate(item.release_date)}</dd>
            <dt className="text-[#75665c]">Momentum</dt>
            <dd className="font-bold">{label(item.momentum_class)} · {score(item.momentum_score)}</dd>
            <dt className="text-[#75665c]">Product fit</dt>
            <dd className="font-bold">{score(item.fit_score)}/100</dd>
          </dl>
        </div>
      </div>
    </details>
  );
}
function ToyEvidenceDetails({
  evidence,
}: {
  evidence: FutureOpportunity["toy_evidence"];
}) {
  function count(value?: number | null) {
    return typeof value === "number" && Number.isFinite(value)
      ? value.toLocaleString()
      : "Not recorded";
  }

  const metrics = [
    ["IP-matched articles", evidence?.validated_article_count],
    ["Commercial product articles", evidence?.commercial_product_article_count],
    ["Movie-specific commercial articles", evidence?.movie_specific_commercial_article_count],
    ["Articles in the last 30 days", evidence?.recent_30d_count],
  ] as const;

  return (
    <section
      aria-label="Toy industry evidence"
      className="mt-5 border-t border-[#e4d9cb] pt-4"
    >
      <h4 className="text-sm font-extrabold">
        What supports this idea?
      </h4>
      <p className="mt-1 text-xs text-[#75665c]">
        ToyNewsI coverage from the saved observation.
      </p>

      {evidence ? (
        <>
          <dl className="mt-3 grid grid-cols-[minmax(0,1fr)_auto] gap-x-4 gap-y-2 text-xs">
            {metrics.map(([name, value]) => (
              <div key={name} className="contents">
                <dt className="text-[#75665c]">{name}</dt>
                <dd className="text-right font-bold">{count(value)}</dd>
              </div>
            ))}
            <dt className="text-[#75665c]">Latest article</dt>
            <dd className="text-right font-bold">
              {evidence.latest_activity
                ? releaseDate(evidence.latest_activity)
                : "Not recorded"}
            </dd>
          </dl>

          <p className="mt-3 text-xs leading-5 text-[#75665c]">
            Counts overlap. Recent articles include all IP-matched
            coverage. Classification uses article text; coverage
            does not measure sales or demand.
          </p>
        </>
      ) : (
        <p className="mt-3 text-xs text-[#75665c]">
          Evidence details were not recorded in this report.
        </p>
      )}
    </section>
  );
}