import { PageHeader } from "@/components/ui/PageHeader";
import { ContentCard } from "@/components/ui/ContentCard";

const MyAssets = () => {
  return (
    <div>
      <PageHeader title="My Assets" subtitle="Manage your owned assets" />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <ContentCard>Portfolio Summary</ContentCard>
        <ContentCard>Asset Performance</ContentCard>
        <ContentCard>Allocation Chart</ContentCard>
        <ContentCard>Recent Activity</ContentCard>
        <ContentCard>Asset Details</ContentCard>
        <ContentCard>Investment Goals</ContentCard>
      </div>
    </div>
  );
};

export default MyAssets;
