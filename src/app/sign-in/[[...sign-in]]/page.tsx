import { SignIn } from "@clerk/nextjs";
import { AuthShell } from "@/app/components/auth/AuthShell";
import { clerkAuthAppearance } from "@/app/components/auth/clerk-appearance";

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
