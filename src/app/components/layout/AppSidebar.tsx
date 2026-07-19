"use client";

import { Show, UserButton } from "@clerk/nextjs";
import {
  Award,
  Gavel,
  GitCompare,
  LayoutDashboard,
  LineChart,
  Newspaper,
  Search,
  Store,
  TrendingUp,
  Users,
  Wallet,
} from "lucide-react";

import { NavLink } from "@/app/components/NavLink";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarInput,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/app/components/ui/sidebar";

const navigationItems = [
  { title: "Dashboard", url: "/", icon: LayoutDashboard },
  { title: "Marketplace", url: "/marketplace", icon: Store },
  { title: "Market Index", url: "/market-index", icon: TrendingUp },
  { title: "Top Performers", url: "/top-performers", icon: Award },
  { title: "My Assets", url: "/my-assets", icon: Wallet },
  { title: "Auctions", url: "/auctions", icon: Gavel },
  { title: "Market News", url: "/market-news", icon: Newspaper },
  { title: "Investment", url: "/investment", icon: LineChart },
  { title: "Compare", url: "/compare", icon: GitCompare },
  { title: "Community", url: "/community", icon: Users },
];

export function AppSidebar() {
  return (
    <Sidebar className="border-r border-sidebar-border">
      <SidebarHeader className="h-16 flex items-center px-5 border-b border-sidebar-border">
        <div className="relative w-full">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <SidebarInput placeholder="Search" className="pl-9 py-5" />
        </div>
      </SidebarHeader>

      <SidebarContent className="px-3 py-4">
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu className="space-y-1">
              {navigationItems.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild className="h-10">
                    <NavLink
                      href={item.url}
                      end={item.url === "/"}
                      className="flex items-center gap-3 px-3 rounded-full text-sidebar-muted-foreground transition-smooth hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                      activeClassName="bg-muted text-foreground font-medium"
                    >
                      <item.icon className="h-5 w-5 shrink-0" />
                      <span>{item.title}</span>
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-sidebar-border px-3 py-3">
        <Show when="signed-in">
          <div className="flex items-center justify-between rounded-xl bg-muted/40 px-3 py-2">
            <div className="min-w-0 pr-2">
              <p className="text-xs text-muted-foreground">Signed in</p>
              <p className="truncate text-sm font-medium">Clerk account</p>
            </div>
            <UserButton />
          </div>
        </Show>

        <Show when="signed-out">
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton asChild className="h-10">
                <NavLink
                  href="/sign-in"
                  className="flex items-center justify-center rounded-full border border-sidebar-border px-3 font-medium text-sidebar-foreground transition-smooth hover:bg-sidebar-accent"
                  activeClassName="bg-muted text-foreground"
                >
                  <span>Sign in</span>
                </NavLink>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </Show>
      </SidebarFooter>
    </Sidebar>
  );
}
