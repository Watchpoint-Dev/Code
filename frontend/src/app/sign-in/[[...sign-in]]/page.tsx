import { SignIn } from "@clerk/nextjs";
import { AuthShell } from "@/components/auth/AuthShell";
import { clerkAuthAppearance } from "@/components/auth/clerk-appearance";

export default function SignInPage() {
  return (
    <AuthShell
      title="Welcome back"
      description="Sign in to continue tracking markets, managing your assets, and discovering new opportunities."
    >
      <SignIn signUpUrl="/sign-up" appearance={clerkAuthAppearance} />
    </AuthShell>
  );
}
