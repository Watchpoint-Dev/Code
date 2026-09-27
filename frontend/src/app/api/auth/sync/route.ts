import { NextResponse } from "next/server";
import { auth, currentUser } from "@clerk/nextjs/server";

import { upsertClerkUser } from "@/lib/db/users";
import { isNeonConfigured } from "@/lib/db/client";

export async function POST() {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: "Unauthorized." }, { status: 401 });
  }

  if (!isNeonConfigured()) {
    return NextResponse.json({ error: "DATABASE_URL is not configured." }, { status: 503 });
  }

  const user = await currentUser();
  if (!user) {
    return NextResponse.json({ error: "Unable to resolve Clerk user." }, { status: 500 });
  }

  const primaryEmail =
    user.emailAddresses.find((email) => email.id === user.primaryEmailAddressId)?.emailAddress ??
    user.emailAddresses[0]?.emailAddress ??
    null;

  try {
    await upsertClerkUser({
      clerkUserId: user.id,
      email: primaryEmail,
      firstName: user.firstName,
      lastName: user.lastName,
      imageUrl: user.imageUrl,
    });

    return NextResponse.json({ ok: true });
  } catch (error) {
    console.error("Failed to sync Clerk user with Neon", error);
    return NextResponse.json({ error: "Neon sync failed." }, { status: 500 });
  }
}
