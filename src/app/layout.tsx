import "../index.css";

import { ClerkProvider } from "@clerk/nextjs";

import { ClerkNeonSync } from "@/app/components/auth/ClerkNeonSync";
import { AppLayout } from "@/app/components/layout/AppLayout";
import { Providers } from "./providers";

export const metadata = {
  title: "Watchpoint 3",
  description: "Converted to Next.js App Router",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ClerkProvider>
          <Providers>
            <ClerkNeonSync />
            <AppLayout>{children}</AppLayout>
          </Providers>
        </ClerkProvider>
      </body>
    </html>
  );
}
