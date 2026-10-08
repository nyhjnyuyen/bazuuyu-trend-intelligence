import { Link, createFileRoute } from "@tanstack/react-router";
import { ArrowRight } from "lucide-react";

export const Route = createFileRoute("/")({
  codeSplitGroupings: [],
  head: () => ({
    meta: [
      { title: "Bazuuyu — Trend Intelligence" },
      {
        name: "description",
        content:
          "Explore character opportunities, entertainment signals, and community trends for Bazuuyu.",
      },
      { property: "og:title", content: "Bazuuyu — Trend Intelligence" },
      {
        property: "og:description",
        content: "A little curiosity. Your next big idea.",
      },
    ],
  }),
  component: HomePage,
});

function HomePage() {
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
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-5 py-5 sm:px-8">
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

          <nav
            aria-label="Main navigation"
            className="flex gap-5 text-sm font-semibold text-[#75665c]"
          >
            <Link to="/future" className="hover:text-[#a62f4d]">
              Opportunities
            </Link>
            <Link to="/explore" className="hover:text-[#a62f4d]">
              Community trends
            </Link>
          </nav>
        </div>
      </header>

      <section className="mx-auto max-w-6xl px-5 pb-16 pt-14 sm:px-8 sm:pt-20">
        <div className="grid items-center gap-10 md:grid-cols-[1.4fr_1fr]">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-[#976650]">
              Bazuuyu Trend Intelligence
            </p>

            <h1 className="mt-5 max-w-xl text-5xl font-black leading-[1.08] tracking-tight sm:text-6xl">
              A little curiosity.
              <br />
              <span className="text-[#b83e5b]">
                Your next big idea.
              </span>
            </h1>

            <p className="mt-6 max-w-lg text-base leading-7 text-[#75665c]">
              Explore upcoming stories, character potential, and
              community conversations. Find what deserves a closer look
              for Bazuuyu.
            </p>

            <Link
              to="/future"
              className="mt-8 inline-flex items-center gap-3 rounded-xl bg-[#42362f] px-5 py-3 text-sm font-bold text-[#fffdf8] transition hover:bg-[#65483e]"
            >
              See what&apos;s next
              <ArrowRight size={17} />
            </Link>
          </div>

          <div
            aria-hidden="true"
            className="relative mx-auto flex h-64 w-full max-w-sm items-center justify-center"
          >
            <div className="absolute left-5 top-7 flex h-36 w-36 rotate-[-12deg] items-center justify-center rounded-[40px] bg-[#f7c6d0] text-7xl text-[#a62f4d]">
              ✿
            </div>

            <div className="absolute bottom-5 right-4 flex h-36 w-36 rotate-[10deg] items-center justify-center rounded-[40px] bg-[#e4eddf] text-7xl text-[#52724c]">
              ✳
            </div>

            <div className="absolute right-12 top-0 text-5xl text-[#b88932]">
              ✦
            </div>

            <div className="absolute bottom-1 left-8 rotate-[-5deg] rounded-lg border border-[#e4d9cb] bg-[#fffdf8] px-4 py-2 text-sm font-bold">
              Small signals. Fresh possibilities.
            </div>
          </div>
        </div>

        <div className="mb-5 mt-16 flex items-center gap-4">
          <h2 className="text-sm font-bold">Where shall we look?</h2>
          <div className="h-px flex-1 bg-[#e8dfd3]" />
        </div>

        <div className="grid gap-5 md:grid-cols-[1.2fr_1fr]">
          <Link
            to="/future"
            className="group rounded-2xl border border-[#e9bdc8] bg-[#fbe5e9] p-6 transition hover:bg-[#f8dbe2] sm:p-8"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#a62f4d]">
                Look ahead
              </span>
              <ArrowRight
                size={20}
                className="text-[#a62f4d] transition group-hover:translate-x-1"
              />
            </div>

            <h3 className="mt-6 text-2xl font-black">
              Future Opportunities
            </h3>

            <p className="mt-3 max-w-md text-sm leading-6 text-[#75535c]">
              Compare upcoming entertainment IPs by momentum,
              release timing, and product fit. Start with the
              opportunities worth researching first.
            </p>

            <p className="mt-6 text-xs font-bold text-[#a62f4d]">
              Character potential · Product fit · Research priorities
            </p>
          </Link>

          <Link
            to="/explore"
            className="group rounded-2xl border border-[#d4ddca] bg-[#eaf0e4] p-6 transition hover:bg-[#e1ead9] sm:p-8"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-wider text-[#456740]">
                Listen in
              </span>
              <ArrowRight
                size={20}
                className="text-[#456740] transition group-hover:translate-x-1"
              />
            </div>

            <h3 className="mt-6 text-2xl font-black">
              Community Trends
            </h3>

            <p className="mt-3 text-sm leading-6 text-[#596650]">
              Explore saved Reddit conversations by community and
              week. Use audience interests as starting points for
              further research.
            </p>

            <p className="mt-6 text-xs font-bold text-[#456740]">
              Conversations · Weekly topics · Audience interests
            </p>
          </Link>
        </div>

        <footer className="mt-12 border-t border-[#e8dfd3] pt-5 text-xs text-[#75665c]">
          Bazuuyu · A place for curious ideas
        </footer>
      </section>
    </main>
  );
}