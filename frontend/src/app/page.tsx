import { ContentCard } from "@/app/components/ui/ContentCard";

const Dashboard = () => {
  return (
    <div>
      <h1 className="mb-6 text-2xl font-semibold">Dashboard</h1>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <ContentCard>Portfolio Overview</ContentCard>
        <ContentCard>Market Trends</ContentCard>
        <ContentCard>Top Assets</ContentCard>
        <ContentCard>Recent Transactions</ContentCard>
        <ContentCard>Asset Performance</ContentCard>
        <ContentCard>News & Alerts</ContentCard>
      </div>
    </div>
  );
};

export default Dashboard;
