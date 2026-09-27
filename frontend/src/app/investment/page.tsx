import { PageHeader } from "@/app/components/ui/PageHeader";
import { ContentCard } from "@/app/components/ui/ContentCard";

const Investment = () => {
  return (
    <div>
      <PageHeader title="Investment" subtitle="Plan and manage your investments" />
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <ContentCard>Investment Plans</ContentCard>
        <ContentCard>Risk Assessment</ContentCard>
        <ContentCard>Portfolio Builder</ContentCard>
        <ContentCard>Investment History</ContentCard>
        <ContentCard>Recommendations</ContentCard>
        <ContentCard>Performance Goals</ContentCard>
      </div>
    </div>
  );
};

export default Investment;
