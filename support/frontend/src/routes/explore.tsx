import {
  Link,
  Outlet,
  createFileRoute,
  useLocation,
} from "@tanstack/react-router";
import { ArrowLeft, ArrowRight, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

export const Route = createFileRoute("/explore")({
  codeSplitGroupings: [],
  head: () => ({
    meta: [
      { title: "Community Lookout — Bazuuyu" },
      {
        name: "description",
        content:
          "Explore plush and collectible communities with Bazuuyu.",
      },
      { property: "og:title", content: "Community Lookout — Bazuuyu" },
      {
        property: "og:description",
        content:
          "Discover what plush and collectible communities are talking about.",
      },
    ],
  }),
  component: ExplorePage,
});

import {
  fetchNiches,
  type NicheSummary,
} from "@/lib/trend-api";

const communities: Record<
  string,
  { label: string; symbol: string; color: string; description: string }
> = {
  plushies: {
    label: "Plushies",
    symbol: "✿",
    color: "#f7d8df",
    description: "Soft companions, collections, and character discoveries.",
  },
  jellycatplush: {
    label: "Jellycat",
    symbol: "✳",
    color: "#e4eddf",
    description: "Collector conversations about whimsical plush characters.",
  },
  squishmallow: {
    label: "Squishmallows",
    symbol: "♡",
    color: "#ffedcb",
    description: "Community favorites, collecting, and new finds.",
  },
};

function ExplorePage() {
  const location = useLocation();
  const [niches, setNiches] = useState<NicheSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const payload = await fetchNiches(controller.signal);

        if (controller.signal.aborted) return;

        setNiches(
          payload.niches.filter((item) =>
            Object.hasOwn(communities, item.niche.toLowerCase()),
          ),
        );
      } catch (caught) {
        if (!controller.signal.aborted) {
          setError(
            caught instanceof Error
              ? caught.message
              : "The community reports could not be loaded.",
          );
        }
      } finally {
        if (!controller.signal.aborted) setLoading(false);
      }
    }

    void load();
    return () => controller.abort();
  }, [reloadKey]);

  if (location.pathname !== "/explore") {
    return <Outlet />;
  }

  return (
    <main
      className="min-h-screen bg-[#faf6ee] text-[#42362f]"
      style={{
        fontFamily:
          '"Avenir Next", "Nunito", "Trebuchet MS", sans-serif',
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
            <span className="text-xl font-black tracking-tight">
              bazuuyu
            </span>
          </Link>

          <Link
            to="/"
            className="flex items-center gap-2 text-sm font-semibold text-[#75665c] hover:text-[#a62f4d]"
          >
            <ArrowLeft size={15} />
            Home
          </Link>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-5 pb-16 pt-10 sm:px-8">
        <div className="mb-9">
          <p className="mb-3 text-xs font-bold uppercase tracking-[0.18em] text-[#976650]">
            The Bazuuyu community lookout
          </p>
          <h1 className="max-w-3xl text-4xl font-black tracking-tight sm:text-5xl">
            What are collectors talking about?
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-6 text-[#75665c]">
            Explore conversations about plushies, character toys,
            and collectibles. Choose a community to browse its
            available weekly reports.
          </p>
        </div>

        {loading ? (
          <p
            role="status"
            className="rounded-2xl border border-[#e4d9cb] bg-[#fffdf8] p-8 text-sm text-[#75665c]"
          >
            Opening the community lookout…
          </p>
        ) : error ? (
          <div
            role="alert"
            className="rounded-2xl border border-[#e4d9cb] bg-[#fffdf8] p-8"
          >
            <h2 className="text-lg font-extrabold">
              We couldn&apos;t open the community reports.
            </h2>
            <p className="mt-2 text-sm text-[#75665c]">
              {error}
            </p>
            <button
              type="button"
              onClick={() => setReloadKey((value) => value + 1)}
              className="mt-5 inline-flex items-center gap-2 rounded-xl bg-[#42362f] px-4 py-2.5 text-sm font-bold text-[#fffdf8]"
            >
              <RefreshCw size={15} />
              Try again
            </button>
          </div>
        ) : niches.length > 0 ? (
          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
            {niches.map((item) => {
              const community = communities[item.niche.toLowerCase()];

              return (
                <Link
                  key={item.niche}
                  to="/explore/$niche"
                  params={{ niche: item.niche }}
                  className="group rounded-2xl border border-[#e4d9cb] bg-[#fffdf8] p-6 transition hover:border-[#c75370] hover:bg-[#fffaf2] focus-visible:outline focus-visible:outline-2 focus-visible:outline-[#c75370]"
                >
                  <div className="flex items-start justify-between">
                    <span
                      aria-hidden="true"
                      style={{ backgroundColor: community.color }}
                      className="flex h-12 w-12 items-center justify-center rounded-2xl text-2xl"
                    >
                      {community.symbol}
                    </span>
                    <ArrowRight
                      size={19}
                      className="mt-3 text-[#9c8878] transition-transform group-hover:translate-x-1"
                    />
                  </div>

                  <h2 className="mt-5 text-2xl font-extrabold">
                    {community.label}
                  </h2>
                  <p className="mt-2 text-sm leading-6 text-[#75665c]">
                    {community.description}
                  </p>

                  <div className="mt-5 border-t border-[#eee5da] pt-4 text-xs text-[#75665c]">
                    <p>r/{item.niche}</p>
                    <p className="mt-1 font-semibold">
                      {item.total_posts.toLocaleString()} posts analyzed
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        ) : (
          <div className="rounded-2xl border border-[#e4d9cb] bg-[#fffdf8] p-8 sm:p-10">
            <span
              aria-hidden="true"
              className="text-3xl text-[#d65c78]"
            >
              ✿
            </span>
            <h2 className="mt-4 text-xl font-extrabold">
              Our community lookout is getting ready.
            </h2>
            <p className="mt-3 max-w-lg text-sm leading-6 text-[#75665c]">
              Reports for Plushies, Jellycat, and Squishmallows
              will appear here once community data is available.
              In the meantime, explore the characters and stories
              on our future lookout.
            </p>

            <Link
              to="/future"
              className="mt-6 inline-flex items-center gap-2 rounded-xl bg-[#f7d8df] px-4 py-3 text-sm font-bold text-[#a62f4d] hover:bg-[#f3c6d1]"
            >
              Explore future opportunities
              <ArrowRight size={17} />
            </Link>
          </div>
        )}
      </section>
    </main>
  );
}