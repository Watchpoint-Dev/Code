"use client";

import { usePathname } from "next/navigation";

import { SidebarProvider } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";

interface AppLayoutProps {
  children: React.ReactNode;
}

const AUTH_ROUTE_PREFIXES = ["/sign-in", "/sign-up"];

export function AppLayout({ children }: AppLayoutProps) {
  const pathname = usePathname();
  const isAuthRoute = AUTH_ROUTE_PREFIXES.some((prefix) => pathname?.startsWith(prefix));

  if (isAuthRoute) {
    return <main className="min-h-screen">{children}</main>;
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <AppSidebar />
        <main className="flex-1 p-6 overflow-auto">{children}</main>
      </div>
    </SidebarProvider>
  );
}
