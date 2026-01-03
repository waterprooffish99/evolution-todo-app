/**
 * Better Auth API route handler for Next.js App Router.
 *
 * This catch-all route handles all Better Auth API requests
 * (login, signup, logout, session management).
 */

import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
