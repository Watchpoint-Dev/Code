import { PageHeader } from "@/components/ui/PageHeader";
import { ContentCard } from "@/components/ui/ContentCard";

const Community = () => {
  return (
    <div>
      <PageHeader title="Community" subtitle="Connect with other investors" />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <ContentCard>Community Feed</ContentCard>
        <ContentCard>Discussion Boards</ContentCard>
        <ContentCard>Top Contributors</ContentCard>
        <ContentCard>Events & Webinars</ContentCard>
        <ContentCard>Groups</ContentCard>
        <ContentCard>Mentorship</ContentCard>
      </div>
    </div>
  );
};

export default Community;
