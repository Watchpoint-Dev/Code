import { PageHeader } from "@/app/components/ui/PageHeader";
import { ContentCard } from "@/app/components/ui/ContentCard";
import newsData from "@/data/dummy-data/market-news/news.json";

const formatIndexChange = (value: number) => `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;

const formatNewsTime = (value: string) =>
  new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(new Date(value));

const MarketNews = () => {
  return (
    <div>
      <PageHeader title="Market News" subtitle="Real-time watch market headlines and analysis" />

      <section aria-label="Market index banner" className="mb-6">
        <div className="-mx-1 flex snap-x gap-3 overflow-x-auto px-1 pb-2 md:mx-0 md:grid md:grid-cols-3 md:gap-4 md:overflow-visible md:px-0 lg:grid-cols-5">
          {newsData.indices.map((index) => {
            const positive = index.changePct >= 0;

            return (
              <ContentCard
                key={index.id}
                className="min-w-[220px] snap-start rounded-3xl border border-border/60 bg-card/90 p-4 md:min-w-0"
              >
                <h3 className="text-sm font-medium text-foreground">{index.name}</h3>
                <div className="mt-3 flex items-baseline gap-2">
                  <p className="text-2xl font-semibold text-foreground">{index.value.toFixed(1)}</p>
                  <p className={`text-sm font-medium ${positive ? "text-emerald-600" : "text-rose-600"}`}>
                    {formatIndexChange(index.changePct)} ({index.changePoints >= 0 ? "+" : ""}
                    {index.changePoints.toFixed(1)})
                  </p>
                </div>
              </ContentCard>
            );
          })}
        </div>
      </section>

      <section aria-label="Lead and top stories" id="all-news">
        <div className="grid gap-4 lg:grid-cols-3">
          <div id={newsData.leadStory.category.toLowerCase().replaceAll(" ", "-")} className="lg:col-span-2">
            <h3 className="mb-3 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">Lead Story</h3>
            <div className="aspect-video rounded-3xl bg-muted" aria-hidden="true" />

            <p className="mt-6 text-xs uppercase tracking-[0.2em] text-muted-foreground">{newsData.leadStory.category}</p>
            <h3 className="mt-3 text-2xl font-semibold leading-tight text-foreground md:text-3xl">
              {newsData.leadStory.title}
            </h3>
            <p className="mt-4 text-sm leading-6 text-muted-foreground">{newsData.leadStory.summary}</p>
            <div className="mt-6 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
              <span>{newsData.leadStory.source}</span>
              <span>|</span>
              <span>{formatNewsTime(newsData.leadStory.publishedAt)}</span>
              <span>|</span>
              <span>{newsData.leadStory.readTimeMinutes} min read</span>
            </div>

            <div className="mt-8">
              <h4 className="mb-3 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">More News</h4>
              <ContentCard className="border border-border/60 bg-transparent p-4">
                <div className="grid gap-4 md:grid-cols-2">
                  {newsData.topStories.slice(0, 3).map((story) => (
                    <article key={`more-${story.id}`}>
                      <div className="mb-3 aspect-video rounded-2xl bg-muted" aria-hidden="true" />
                      <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">{story.category}</p>
                      <h5 className="mt-2 text-sm font-semibold leading-snug text-foreground">{story.title}</h5>
                      <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                        <span>{story.source}</span>
                        <span>|</span>
                        <span>{formatNewsTime(story.publishedAt)}</span>
                      </div>
                    </article>
                  ))}
                </div>
              </ContentCard>
            </div>
          </div>

          <div>
            <h3 className="mb-3 text-xs font-medium uppercase tracking-[0.2em] text-muted-foreground">Top Stories</h3>

            <div className="space-y-4">
              {newsData.topStories.map((story) => (
                <article key={story.id} id={story.category.toLowerCase().replaceAll(" ", "-")} className="border-b border-border/60 pb-4 last:border-b-0 last:pb-0">
                  <div className="mb-3 aspect-video rounded-2xl bg-muted" aria-hidden="true" />
                  <p className="text-[11px] uppercase tracking-[0.18em] text-muted-foreground">{story.category}</p>
                  <h4 className="mt-2 text-sm font-semibold leading-snug text-foreground">{story.title}</h4>
                  <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
                    <span>{story.source}</span>
                    <span>|</span>
                    <span>{formatNewsTime(story.publishedAt)}</span>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default MarketNews;
