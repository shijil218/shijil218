---
name: instagram-manager
description: Manage the Kannur Computers Instagram account for free through Instagram's official API, with no paid tool or connector. Shows followers and post performance, makes weekly reports from real Insights, reads and replies to comments, and publishes photos, carousels and Reels (with captions) after the user approves each one. Use this skill whenever the user wants to connect Instagram, check their stats, insights, reach or best posts, reply to comments, post or upload a Reel or photo to Instagram, or manage their Instagram page, including in Manglish ("instagram manage cheyyu", "post cheyyu", "insights nokku"), even if they don't say "skill" or "API".
---

# Instagram Manager (free, official API)

This skill lets Claude work on the shop's own Instagram account through the official Instagram API ("Instagram API with Instagram Login"). It is free: the user creates a Meta developer app once and gets an access token. Everything goes through `scripts/ig.py` (Python standard library only).

For *what* to post (content plans, captions, hashtags, bio advice), use the kannur-insta-growth skill alongside this one. This skill handles the *doing*: reading numbers and publishing.

## First: is it set up?

Run `python scripts/ig.py whoami`.

- **Works** → carry on.
- **Network blocked** (proxy refused `graph.instagram.com`) → in a cloud session, follow the environment tools' rules to allow the host `graph.instagram.com`, then retry.
- **No token / OAuthException 190** → the user hasn't set up a token yet, or it expired. Read `references/setup.md` and walk them through it step by step, one step at a time, in the language they use. In a cloud session, ask for the token with `request_credential` (host `graph.instagram.com`); never ask them to paste it in chat, because the token gives full control of the account.

## What you can do

| User asks | Command |
|---|---|
| Profile stats, follower count | `ig.py whoami` |
| How are my posts doing? weekly report | `ig.py report --limit 12`, plus `ig.py account-insights --days 7` (or 28) |
| Stats for one post | `ig.py media-insights <media_id>` |
| Show comments / reply | `ig.py comments <media_id>`, then `ig.py reply <comment_id> "text" --yes` |
| Post a photo | `ig.py publish-image <public_url> --caption "..." --yes` |
| Post several photos | `ig.py publish-carousel <url1> <url2> ... --caption "..." --yes` |
| Post a Reel | `ig.py publish-reel <public_url.mp4> --caption "..." [--cover-url URL] --yes` |
| How many posts left today | `ig.py limit` |
| Token expiring (about every 60 days) | `ig.py refresh-token --yes`, then save the new token the same way as before |

Get the media IDs from `ig.py media` or `ig.py report`.

## Rules for anything that goes live

Publishing and replying are public and hard to undo (the API cannot delete posts), so:

1. **Always show first, then wait for a clear yes.** Show the exact caption, the file being posted and, for replies, the exact reply text. Only then run the command with `--yes`. Approval for one post does not cover the next one.
2. **Reply like a person from the shop**: short, friendly, in the commenter's language, with the phone/WhatsApp number when it helps (+91 94475 40218). For several comments, draft all replies, show them together, and post only the approved ones. Don't reply to spam; tell the user about it instead.
3. **No fake growth.** The API can't follow, like or DM strangers, and this skill must not try other ways to do that (bots, scraping, password-sharing apps). Instagram blocks accounts for it.
4. Respect the daily publishing limit (`ig.py limit`).

## Media must be at a public URL

Instagram downloads the file from a link; it cannot take a file straight from this computer. Ways to get a direct public link, best first:

1. **The shop's website** (www.kannurcomputers.com), if the user can upload files there.
2. **A public GitHub repository**: commit the file and use its `https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path>` link. Check the repository is public first, and don't put anything private there.
3. Any other host that gives a **direct** file link (opening it shows the raw image/video, not a page).

Google Drive and WhatsApp links don't work because they open a web page. Requirements: images JPEG; Reels MP4 (H.264, AAC), 9:16, 3 s to 15 min; carousels 2 to 10 items. Reels made with the kannur-reel-editor skill or the promo scripts already fit.

After publishing, give the user the permalink the script prints.

## Weekly report format

When asked how the account is doing, run `report` and `account-insights`, then answer with:

```
## Instagram report: <date range>
Followers: <n> (<+/- change if known>)
Top 3 posts: <title> · views · shares · saves · why it worked
Weakest post: <title> · what to change
Do more of: <1–2 concrete ideas based on the numbers>
Next week: <3 posts to make>
```

Shares and saves matter more than likes: they show the post was useful and push it to more people. Keep it short and practical; the user wants to know what to post next, not a data dump.

## Limits to tell the user plainly

- Setup takes about 15 minutes once, and the token needs refreshing about every 60 days.
- The API cannot delete or edit posts after publishing (except comments), schedule posts for later, read DMs (without extra approval), or follow/like accounts.
- Instagram renames metrics now and then; if a metric errors, retry with a shorter `--metrics` list.
