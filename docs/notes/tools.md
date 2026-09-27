# Tools

Reference list of the tools/services for the project. Two sections:
1. **Currently used** — what is in the code today.
2. **Planned / to use** — current ones we keep + new ones we will add, with a
   short plain-language explanation of what each does and why.

Status legend: **Current** (in use now) · **Planned** (agreed direction) ·
**Later** (only if/when needed).

---

## 1. Currently used (in the code today)

### Frontend / framework
| Tool | What it does |
|------|--------------|
| **Next.js** (App Router) | The web framework. Pages, routing, server + client components, API routes. |
| **React** | UI library the pages are built with. |
| **TypeScript** | Typed JavaScript. Whole codebase is TS. |
| **Tailwind CSS** | Utility CSS for styling. |
| **shadcn/ui** + **Radix UI** | The component library (~50 prebuilt UI components: buttons, tables, dialogs…). |
| **lucide-react** | Icon set. |
| **Recharts** | Charts (the trend/price graphs). |
| **next-themes** | Light/dark theme switching. |
| **TanStack Query** | Client-side data fetching/caching layer (installed, lightly used). |
| **react-hook-form** + **Zod** | Forms + validation. Zod is installed but barely used yet. |
| **sonner** | Toast notifications. |
| **date-fns** | Date formatting utilities. |

### Auth
| Tool | What it does |
|------|--------------|
| **Clerk** | Authentication (sign-in/up, sessions, route protection, user profile). Done and working. |

### Database
| Tool | What it does |
|------|--------------|
| **Neon** | Serverless Postgres database. Currently stores **only users** (`app_users`). |
| **@neondatabase/serverless** | The driver used to talk to Neon from the app. |

### Dev tooling
| Tool | What it does |
|------|--------------|
| **ESLint** | Linting / code-style checks. |
| **Bun / npm** | Package manager. Both a `bun.lockb` and `package-lock.json` exist — we should pick ONE. |
| **lovable-tagger** (dev dep) | Suggests the app was scaffolded with **Lovable** (AI app builder). Not needed long-term. |

---

## 2. Planned / to use (target stack)

Keeps the current ones that are good, and adds what the data platform needs.
Grouped by role.

### Frontend (keep as-is)
| Tool | Status | What it does / why |
|------|--------|--------------------|
| Next.js, React, TypeScript, Tailwind, shadcn/ui, Recharts, TanStack Query | Current | Solid front-end foundation. Keep all of it. |
| **Zod** | Current → use more | Validate all incoming data at the ingestion boundary before it hits the DB. Already installed. |

### Auth (keep as-is)
| Tool | Status | What it does / why |
|------|--------|--------------------|
| **Clerk** | Current | Auth is done and correct. Keep. |

### Database & storage
| Tool | Status | What it does / why |
|------|--------|--------------------|
| **Neon (Postgres)** | Current | Keep the same instance. Main source of truth. We rebuild the **schema** (watches, listings, price history, auctions, sources, raw staging), not the server. |
| **An ORM** (see box below) | Planned | The library between our code and Neon. Which one depends on the pipeline language: **Drizzle/Prisma** (TypeScript) or **SQLAlchemy** (Python). |

> **What is an ORM?** Object-Relational Mapper — a library that lets you work
> with typed code objects instead of hand-written SQL strings, and that manages
> the schema + migrations (versioned DB changes so every dev/environment stays
> in sync). It lives *inside* the persistence adapter; the domain core and UI
> never see it. **The ORM follows the language of the code that uses it** — so
> the real choice is the pipeline language, not the ORM in isolation.
>
> | ORM | Language | Notes |
> |-----|----------|-------|
> | **Drizzle** | TypeScript | Light, SQL-first, best fit for Neon/serverless. Web app default. |
> | **Prisma** | TypeScript | Gentler learning curve, nice data browser; heavier. |
> | **SQLAlchemy** | Python | Mature, powerful. Right choice **if the pipeline is Python** (scraping + pandas + ML). Connects to the same Neon Postgres. |
>
> Neon is just Postgres, so any of these connect fine. If web (TS) and pipeline
> (Python) are split, we'd use **Drizzle in the web app + SQLAlchemy in the
> pipeline**, both on the same DB — the schema then lives in two places and must
> be kept in sync (treat SQL migrations as the single source of truth). See the
> "Pipeline language" decision in `Plan1_10-07.md`.
| **Cloudflare R2** (or **AWS S3**) | Later | Cheap object storage for **raw scraped payloads** (HTML/JSON). The DB just points to them instead of storing big blobs. |
| **Timescale Cloud** | Later | Postgres for heavy **time-series** price data, *only if* `price_points` gets huge. Note: Neon can't run the Timescale extension, so this would be a separate DB. Not needed at start. |
| **Upstash Redis** | Later | In-memory store for **rate-limiting** scrapers, caching hot queries, and as a job queue if we outgrow Inngest. |
| **Typesense / Meilisearch** | Later | Fast watch search / autocomplete when the catalog is large. |

### Data pipeline / ingestion
> Language for the pipeline is still open (TypeScript vs Python) — see Plan1.
> The tools below list both worlds; pick per that decision.

| Tool | Status | What it does / why |
|------|--------|--------------------|
| **Inngest** | Planned | Runs the ingestion **jobs on a schedule** with retries and step-by-step pipelines. Next-native (TS), no server to manage. |
| **Vercel Cron** | Planned (alt) | Simplest way to trigger scheduled jobs (TS). Good to start; Inngest if we need retries/steps. |
| **Source adapters** (eBay API, WatchCharts, Chrono24, auction houses) | Planned | One adapter per source that fetches and normalizes data into our schema. eBay first (official API). Language depends on pipeline choice. |
| **Python data stack** (pandas / polars, requests, Scrapy) | Planned (if Python pipeline) | Industry-standard for scraping, cleaning, transformation, and analysis/ML. Pairs with SQLAlchemy. |
| **Playwright / Puppeteer** | Later | Headless browser for **scraping** sources that have no API. Exists for both TS and Python. |
| **ScrapingBee / Bright Data** | Later | Paid scraping/proxy service if sources have strong anti-bot protection. |

### Hosting / infrastructure
| Tool | Status | What it does / why |
|------|--------|--------------------|
| **Vercel** | Planned | Hosts the Next.js app; auto-deploys from GitHub on push. |
| **Neon** | Current | Database hosting (already have). |
| **Inngest** | Planned | Hosts/runs the scheduled ingestion functions. |

### Source control / collaboration / CI
| Tool | Status | What it does / why |
|------|--------|--------------------|
| **GitHub** | Current (needs cleanup) | Code hosting + team collaboration. A repo exists (`bavma-project`) but local setup is messy (home folder is the repo). Need a clean dedicated repo. |
| **GitHub Actions** | Planned | CI: run lint / typecheck / tests automatically on every pull request. |
| **pnpm + Turborepo** | Planned | If we go monorepo (web app + ingestion workers in one repo), these manage packages and builds. |

### Quality / monitoring
| Tool | Status | What it does / why |
|------|--------|--------------------|
| **Vitest** | Planned | Unit testing for the domain core and adapters. |
| **Playwright (test mode)** | Later | End-to-end UI testing. |
| **Sentry** | Later | Error monitoring / alerting in production. |

---

## Quick "by role" summary

- **Framework / UI:** Next.js, React, TypeScript, Tailwind, shadcn/ui, Recharts
- **Auth:** Clerk
- **Database:** Neon (Postgres) + an ORM (Drizzle/Prisma if TS, SQLAlchemy if Python); later R2/S3, Timescale, Redis
- **Pipeline:** TS (Inngest/Vercel Cron) or Python (Scrapy/pandas) + per-source adapters; later Playwright
- **Hosting:** Vercel (app) + Neon (DB) + Inngest (jobs)
- **Repo / CI:** GitHub + GitHub Actions; pnpm + Turborepo if monorepo
- **Quality:** Vitest, later Playwright + Sentry

---

## Decisions still open (see Plan1)
- [ ] **Pipeline language: TypeScript vs Python** — drives the ORM choice.
- [ ] ORM: Drizzle vs Prisma (if TS) / SQLAlchemy (if Python).
- [ ] Package manager: Bun vs npm vs pnpm — pick one.
- [ ] Scheduling: Inngest vs Vercel Cron (TS) / cron + worker (Python).
- [ ] Monorepo (pnpm + Turborepo) or single repo.
