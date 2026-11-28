# One-time setup (free)

Give the user these steps in simple language (Malayalam or Manglish if that is how they write). Meta renames menus fairly often, so if a step's wording doesn't match what they see, help them find the closest option rather than insisting on the exact label.

## 1. Make the Instagram account professional
Instagram app → Profile → ☰ → Settings → Account type and tools → Switch to professional account → **Business** (category: Computer Repair Service). Free.

## 2. Create a free Meta developer app
1. Go to developers.facebook.com, log in with Facebook, and register as a developer (free; may ask to verify a phone number).
2. My Apps → **Create app** → use case **"Manage messaging & content on Instagram"** (sometimes listed as "Other" → app type **Business**). Name it e.g. "Kannur Computers Manager".
3. In the app, open **Instagram → API setup with Instagram login**.

## 3. Connect the Instagram account and get a token
1. Under "Generate access tokens", click **Add account** and log in to the shop's Instagram account. Approve the permissions (basic, content publish, manage comments, insights).
2. If Instagram asks, accept the tester invite: Instagram app → Settings → Website permissions / Apps and websites → Tester invites → Accept.
3. Click **Generate token** next to the account. Copy the token. This is the **access token**; it lasts about 60 days and can be refreshed with `ig.py refresh-token --yes`.

The app can stay in **Development mode**: that is enough for managing your own account, and no App Review is needed. App Review is only needed for managing other people's accounts.

## 4. Give the token to Claude safely
- **Never paste the token in chat.** It is like a password for the Instagram account.
- **Claude Code on the web / cloud session:** Claude calls `request_credential` for host `graph.instagram.com`; the user pastes the token into the secure form. The proxy adds it to requests, so `ig.py` works with no token in the environment. Also allow the host `graph.instagram.com` in the environment's network settings if it is blocked.
- **Own computer:** put it in a file only the user can read, e.g. `~/.ig_token`, then `export IG_TOKEN_FILE=~/.ig_token` (or set `IG_ACCESS_TOKEN`).

## 5. Test
`python scripts/ig.py whoami` should print the username and follower count.

## Common errors
- `OAuthException 190`: token expired or wrong. Generate a new one (step 3) or refresh it.
- `code 10` / `200` permission errors: the permission wasn't approved when generating the token. Regenerate and tick all permissions.
- `Media download has failed` / `2207xxx` when publishing: the media URL is not public or not a direct file link. Open the URL in a private browser window; it must download/show the raw file, not a web page.
- Unknown metric errors in insights: Instagram renames metrics now and then. Run again with `--metrics` and a smaller list (e.g. `reach,likes,comments`).
