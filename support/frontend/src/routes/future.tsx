import { Link, createFileRoute } from "@tanstack/react-router";
import {
  ArrowLeft,
  CalendarDays,
  Radar,
  Sparkles,
  TrendingUp,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import {
  fetchFutureOpportunities,
  type FutureOpportunity,
} from "@/lib/trend-api";

export const Route = createFileRoute("/future")({
  component: FutureOpportunitiesPage,
  head: () => ({
    meta: [
      {
        title: "Future Opportunities — Bazuuyu Trend Intelligence",
      },
      {
        name: "description",
        content:
          "Ranked future entertainment and IP opportunities for Bazuuyu.",
      },
    ],
  }),
});

function displayLabel(value?: string | null) {
  if (!value) return "—";

  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function scoreLabel(score: number | null) {
  if (score === null) return "Pending";
  return score.toFixed(2);
}

function FutureOpportunitiesPage() {
  const [results, setResults] = useState<FutureOpportunity[]>([]);
  const [generatedAt, setGeneratedAt] = useState<string>();
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<
    "ALL" | "TOP_PRIORITY" | "WATCH" | "LOW_PRIORITY" | "WATCHLIST"
  >("ALL");

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      try {
        setLoading(true);

        const payload = await fetchFutureOpportunities(
          controller.signal,
        );

        setResults(payload.results);
        setGeneratedAt(payload.generated_at);
      } catch (error) {
        if ((error as Error).name !== "AbortError") {
          toast.error("Could not load future opportunities", {
            description:
              "Make sure the API is running at http://localhost:8000.",
          });
        }
      } finally {
        setLoading(false);
      }
    }

    load();

    return () => controller.abort();
  }, []);

  const ranked = useMemo(
    () =>
      results.filter(
        (item) => item.final_score !== null,
      ),
    [results],
  );

  const watchlist = useMemo(
    () =>
      results.filter(
        (item) =>
          item.final_score === null &&
          item.fit_score >= 75,
      ),
    [results],
  );

  const filteredRanked = useMemo(() => {
    if (filter === "ALL") {
      return ranked;
    }

    if (filter === "WATCHLIST") {
      return [];
    }

    return ranked.filter(
      (item) =>
        item.final_priority === filter,
    );
  }, [filter, ranked]);

  const showWatchlist =
    filter === "ALL" ||
    filter === "WATCHLIST";

  const topPriorityCount = ranked.filter(
    (item) => item.final_priority === "TOP_PRIORITY",
  ).length;

  const watchCount = ranked.filter(
    (item) => item.final_priority === "WATCH",
  ).length;

  const lowPriorityCount = ranked.filter(
    (item) => item.final_priority === "LOW_PRIORITY",
  ).length;

  const watchlistCount = watchlist.length;

  return (
    <main className="min-h-screen bg-background px-5 py-8 text-foreground">
      <section className="mx-auto max-w-7xl">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <Button asChild variant="outline">
            <Link to="/">
              <ArrowLeft className="size-4" />
              Home
            </Link>
          </Button>

          {generatedAt && (
            <p className="text-sm text-muted-foreground">
              Updated{" "}
              {new Date(
                generatedAt,
              ).toLocaleString()}
            </p>
          )}
        </div>

        <div className="mb-10">
          <div className="mb-4 inline-flex items-center gap-2 rounded-md border border-primary/30 bg-primary/10 px-3 py-1.5 text-sm font-medium text-primary">
            <Radar className="size-4" />
            Bazuuyu Future Intelligence
          </div>

          <h1 className="font-display text-4xl font-bold sm:text-6xl">
            Future Opportunities
          </h1>

          <p className="mt-4 max-w-3xl text-lg leading-8 text-muted-foreground">
            Future entertainment and IP opportunities ranked by
            momentum, timing, toy-market signals, and Bazuuyu
            product fit.
          </p>
        </div>

        {loading ? (
          <LoadingGrid />
        ) : (
          <>
            <div className="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <SummaryCard
                label="Top Priority"
                value={topPriorityCount}
                description="Act on these first"
              />

              <SummaryCard
                label="Watch"
                value={watchCount}
                description="Monitor closely"
              />

              <SummaryCard
                label="Low Priority"
                value={lowPriorityCount}
                description="Do not invest heavily"
              />

              <SummaryCard
                label="High-Fit Watchlist"
                value={watchlistCount}
                description="Strong fit, more history needed"
              />
            </div>

            <div className="mb-8 flex flex-wrap gap-2">
              {[
                ["ALL", "All"],
                ["TOP_PRIORITY", "Top Priority"],
                ["WATCH", "Watch"],
                ["LOW_PRIORITY", "Low Priority"],
                ["WATCHLIST", "Watchlist"],
              ].map(([value, label]) => (
                <button
                  key={value}
                  onClick={() =>
                    setFilter(
                      value as
                        | "ALL"
                        | "TOP_PRIORITY"
                        | "WATCH"
                        | "LOW_PRIORITY"
                        | "WATCHLIST",
                    )
                  }
                  className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
                    filter === value
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-background text-muted-foreground hover:border-primary/60 hover:text-foreground"
                  }`}
                >
                  {label}
                </button>
              ))}
            </div>

            <div className="mb-6 flex items-center gap-2">
              <TrendingUp className="size-5 text-primary" />
              <h2 className="text-2xl font-bold">
                Ranked Opportunities
              </h2>
            </div>

            <div className="grid gap-5">
              {filteredRanked.map((item, index) => (
                <OpportunityCard
                  key={item.ip}
                  item={item}
                  rank={index + 1}
                />
              ))}
            </div>

            {showWatchlist && watchlist.length > 0 && (
              <section className="mt-14">
                <div className="mb-3 flex items-center gap-2">
                  <Sparkles className="size-5 text-primary" />
                  <h2 className="text-2xl font-bold">
                    High-Fit Watchlist
                  </h2>
                </div>

                <p className="mb-6 text-muted-foreground">
                  These IPs have strong Bazuuyu product fit but
                  need another historical snapshot before
                  momentum can be scored.
                </p>

                <div className="grid gap-4 md:grid-cols-2">
                  {watchlist.map((item) => (
                    <WatchlistCard
                      key={item.ip}
                      item={item}
                    />
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </section>
    </main>
  );
}

function OpportunityCard({
  item,
  rank,
}: {
  item: FutureOpportunity;
  rank: number;
}) {
  return (
    <article
      className={`glass-panel rounded-xl border p-6 transition duration-300 ${
        item.final_priority === "TOP_PRIORITY"
          ? "border-primary/70 bg-primary/5 shadow-lg shadow-primary/10"
          : "border-border hover:border-primary/50"
      }`}
    >
      <div className="flex flex-col justify-between gap-6 lg:flex-row">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-3">
            <span className="flex size-9 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
              #{rank}
            </span>

            <h3 className="text-2xl font-bold">
              {item.ip}
            </h3>

            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                item.final_priority === "TOP_PRIORITY"
                  ? "border-primary bg-primary text-primary-foreground"
                  : item.final_priority === "WATCH"
                    ? "border-primary/30 bg-primary/10 text-primary"
                    : "border-border bg-muted text-muted-foreground"
              }`}
            >
              {displayLabel(item.final_priority)}
            </span>
          </div>

          <p className="mt-2 text-sm text-muted-foreground">
            {item.title}
          </p>

          <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
            <Metric
              label="Final Score"
              value={scoreLabel(item.final_score)}
            />

            <Metric
              label="Momentum"
              value={displayLabel(
                item.momentum_class,
              )}
              secondary={
                item.momentum_score !== null
                  ? item.momentum_score.toFixed(2)
                  : undefined
              }
            />

            <Metric
              label="Product Fit"
              value={displayLabel(item.fit_level)}
              secondary={`${item.fit_score}/100`}
            />

            <Metric
              label="Timing"
              value={displayLabel(
                item.action_timing,
              )}
              secondary={
                item.timing_score !== null
                  ? item.timing_score.toFixed(2)
                  : undefined
              }
              highlight={
                item.action_timing === "ACT_NOW"
              }
            />

            <Metric
              label="Signal"
              value={displayLabel(
                item.signal_profile,
              )}
            />
          </div>

          <div className="mt-6 rounded-lg border border-border bg-background/40 p-4">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Recommended Action
            </p>

            <p className="mt-2 font-semibold text-primary">
              {displayLabel(
                item.recommended_action,
              )}
            </p>

            {item.recommendation_summary && (
              <p className="mt-2 leading-6 text-muted-foreground">
                {item.recommendation_summary}
              </p>
            )}
          </div>
        </div>

        <div className="lg:w-52">
          <div className="rounded-lg border border-border p-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CalendarDays className="size-4" />
              Release
            </div>

            <p className="mt-2 font-semibold">
              {item.release_date
                ? new Date(
                    `${item.release_date}T00:00:00`,
                  ).toLocaleDateString()
                : "Unknown"}
            </p>

            {item.days_to_release !== null && (
              <p className="mt-1 text-sm text-muted-foreground">
                {item.days_to_release} days away
              </p>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}

function WatchlistCard({
  item,
}: {
  item: FutureOpportunity;
}) {
  return (
    <article className="rounded-xl border border-border bg-surface p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-xl font-bold">
            {item.ip}
          </h3>

          <p className="mt-1 text-sm text-muted-foreground">
            {item.title}
          </p>
        </div>

        <span className="rounded-full bg-primary/10 px-3 py-1 text-xs font-semibold text-primary">
          {item.fit_score}/100 fit
        </span>
      </div>

      <div className="mt-5">
        <p className="text-sm font-medium">
          {displayLabel(item.fit_level)} Product Fit
        </p>

        <p className="mt-2 text-sm text-muted-foreground">
          {displayLabel(
            item.recommended_action,
          )}
        </p>
      </div>

      {!!item.fit_signals.length && (
        <div className="mt-4 flex flex-wrap gap-2">
          {item.fit_signals.map((signal) => (
            <span
              key={signal}
              className="rounded-md border border-border px-2 py-1 text-xs text-muted-foreground"
            >
              {displayLabel(signal)}
            </span>
          ))}
        </div>
      )}
    </article>
  );
}

function Metric({
  label,
  value,
  secondary,
  highlight = false,
}: {
  label: string;
  value: string;
  secondary?: string;
  highlight?: boolean;
}) {
  return (
    <div>
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>

      <p
        className={`mt-1 font-semibold ${
          highlight
            ? "text-primary"
            : ""
        }`}
      >
        {value}
      </p>

      {secondary && (
        <p className="mt-1 text-sm text-muted-foreground">
          {secondary}
        </p>
      )}
    </div>
  );
}

function SummaryCard({
  label,
  value,
  description,
}: {
  label: string;
  value: number;
  description: string;
}) {
  return (
    <div className="rounded-xl border border-border bg-surface p-5">
      <p className="text-sm font-medium text-muted-foreground">
        {label}
      </p>

      <p className="mt-2 text-3xl font-bold text-foreground">
        {value}
      </p>

      <p className="mt-1 text-sm text-muted-foreground">
        {description}
      </p>
    </div>
  );
}

function LoadingGrid() {
  return (
    <div className="grid gap-5">
      {Array.from({ length: 5 }).map(
        (_, index) => (
          <div
            key={index}
            className="rounded-xl border border-border p-6"
          >
            <Skeleton className="h-8 w-52" />
            <Skeleton className="mt-4 h-4 w-72" />

            <div className="mt-8 grid gap-4 sm:grid-cols-3">
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
              <Skeleton className="h-16" />
            </div>
          </div>
        ),
      )}
    </div>
  );
}