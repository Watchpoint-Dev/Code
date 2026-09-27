import { ShieldCheck, Sparkles, TrendingUp } from "lucide-react";

interface AuthShellProps {
  title: string;
  description: string;
  children: React.ReactNode;
}

const highlights = [
  {
    icon: TrendingUp,
    title: "Market intelligence",
    description: "Track indices, top performers, and auction momentum in one place.",
  },
  {
    icon: ShieldCheck,
    title: "Secure account",
    description: "Protected authentication powered by Clerk and synced with Neon.",
  },
  {
    icon: Sparkles,
    title: "Personalized workspace",
    description: "Sign in to access your watchlist, assets, and tailored market views.",
  },
];

export function AuthShell({ title, description, children }: AuthShellProps) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-24 top-12 h-64 w-64 rounded-full bg-accent/40 blur-3xl" />
        <div className="absolute -right-20 bottom-8 h-72 w-72 rounded-full bg-muted/70 blur-3xl" />
      </div>

      <main className="relative mx-auto grid min-h-screen w-full max-w-6xl gap-10 px-4 py-10 md:px-8 lg:grid-cols-[1.1fr_0.9fr] lg:items-center lg:py-14">
        <section className="space-y-6">
          <span className="inline-flex items-center rounded-full border border-border/70 bg-card/80 px-4 py-1.5 text-xs font-semibold uppercase tracking-[0.2em] text-muted-foreground backdrop-blur">
            Watch Platform
          </span>

          <div className="space-y-3">
            <h1 className="text-3xl font-semibold tracking-tight text-foreground md:text-4xl">{title}</h1>
            <p className="max-w-xl text-base text-muted-foreground md:text-lg">{description}</p>
          </div>

          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            {highlights.map((item) => (
              <article
                key={item.title}
                className="rounded-3xl border border-border/60 bg-card/70 p-4 backdrop-blur"
              >
                <item.icon className="mb-3 h-5 w-5 text-foreground" />
                <h2 className="text-sm font-semibold text-foreground">{item.title}</h2>
                <p className="mt-1 text-sm text-muted-foreground">{item.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="rounded-[var(--radius-card)] border border-border/60 bg-card/75 p-2 backdrop-blur-sm sm:p-3">
          {children}
        </section>
      </main>
    </div>
  );
}
