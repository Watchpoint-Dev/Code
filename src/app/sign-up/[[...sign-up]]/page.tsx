import { SignUp } from "@clerk/nextjs";
import { AuthShell } from "@/app/components/auth/AuthShell";
import { clerkAuthAppearance } from "@/app/components/auth/clerk-appearance";

export default function SignUpPage() {
  return (
    <AuthShell
      title="Create your account"
      description="Join the platform to build your watchlist, follow market movements, and access your personal workspace."
    >
      <SignUp signInUrl="/sign-in" appearance={clerkAuthAppearance} />
    </AuthShell>
  );
}
