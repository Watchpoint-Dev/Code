export const clerkAuthAppearance = {
  elements: {
    rootBox: "w-full",
    cardBox: "w-full shadow-none",
    card: "w-full rounded-[calc(var(--radius-card)-0.75rem)] border border-border/60 bg-card p-6 shadow-none",
    headerTitle: "text-2xl font-semibold text-foreground",
    headerSubtitle: "text-sm text-muted-foreground",
    socialButtonsBlockButton:
      "h-11 rounded-[var(--radius-control)] border border-border bg-background text-foreground shadow-none transition-smooth hover:bg-muted",
    socialButtonsBlockButtonText: "text-sm font-medium",
    dividerLine: "bg-border",
    dividerText: "text-xs font-medium text-muted-foreground",
    formFieldLabel: "text-sm font-medium text-foreground",
    formFieldInput:
      "h-11 rounded-[var(--radius-control)] border border-input bg-background px-4 text-foreground shadow-none ring-offset-0 transition-smooth focus:border-primary focus:ring-0 focus-visible:ring-0",
    formButtonPrimary:
      "h-11 rounded-[var(--radius-control)] bg-primary text-primary-foreground shadow-none transition-smooth hover:bg-primary/90",
    footerActionText: "text-sm text-muted-foreground",
    footerActionLink: "text-sm font-semibold text-foreground hover:text-foreground/70",
    identityPreviewText: "text-sm text-foreground",
    identityPreviewEditButton:
      "rounded-[var(--radius-control)] border border-border bg-background px-3 py-1 text-xs font-medium text-foreground transition-smooth hover:bg-muted",
    formResendCodeLink: "text-sm font-medium text-foreground hover:text-foreground/70",
    otpCodeFieldInput:
      "rounded-[var(--radius-control)] border border-input bg-background text-foreground shadow-none focus:border-primary",
    alertText: "text-sm text-destructive",
  },
} as const;
