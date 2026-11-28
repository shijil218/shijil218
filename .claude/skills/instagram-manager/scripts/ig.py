#!/usr/bin/env python3
"""Free Instagram management through the official Instagram API (Instagram Login, graph.instagram.com).

No extra packages needed. The access token comes from IG_ACCESS_TOKEN (or a file named by IG_TOKEN_FILE).
If neither is set, requests carry an "Authorization: Bearer" header with a placeholder, for cloud sessions
where a network proxy injects the saved token for graph.instagram.com.

Examples:
  python ig.py whoami
  python ig.py media --limit 12
  python ig.py report --limit 12
  python ig.py account-insights --days 28
  python ig.py media-insights 1789xxxxxxxx
  python ig.py comments 1789xxxxxxxx
  python ig.py reply 1790xxxxxxxx "Thank you! WhatsApp us on 94475 40218"
  python ig.py publish-image https://example.com/a.jpg --caption "..."
  python ig.py publish-reel https://example.com/reel.mp4 --caption "..." [--cover-url URL]
  python ig.py publish-carousel URL1 URL2 [...] --caption "..."
  python ig.py limit
  python ig.py refresh-token
Write commands (publish-*, reply, refresh-token) need --yes, so nothing goes live by accident.
"""
import argparse, json, os, ssl, sys, time, urllib.error, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone

HOST = os.environ.get("IG_API_HOST", "https://graph.instagram.com")
VER = os.environ.get("IG_API_VERSION", "")  # e.g. "v23.0"; empty = the app's default version
BASE = HOST.rstrip("/") + ("/" + VER if VER else "")


def _token():
    t = os.environ.get("IG_ACCESS_TOKEN")
    if not t and os.environ.get("IG_TOKEN_FILE"):
        t = open(os.environ["IG_TOKEN_FILE"]).read().strip()
    return t


def _ctx():
    for ca in (os.environ.get("SSL_CERT_FILE"), "/root/.ccr/ca-bundle.crt"):
        if ca and os.path.exists(ca):
            return ssl.create_default_context(cafile=ca)
    return ssl.create_default_context()


def call(path, params=None, method="GET", base=BASE):
    params = dict(params or {})
    tok = _token()
    headers = {"User-Agent": "instagram-manager-skill"}
    if tok:
        params["access_token"] = tok
    else:
        headers["Authorization"] = "Bearer PROXY_INJECTED"
    url = f"{base}/{path.lstrip('/')}"
    data = None
    if method == "GET":
        url += "?" + urllib.parse.urlencode(params)
    else:
        data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, context=_ctx(), timeout=60) as r:
            return json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error", {})
            msg = f"{err.get('type', '')} {err.get('code', '')}: {err.get('message', body)}"
        except Exception:
            msg = body[:500]
        sys.exit(f"Instagram API error (HTTP {e.code}) on {path}: {msg}")
    except urllib.error.URLError as e:
        sys.exit(f"Network error reaching {HOST}: {e.reason}")


def out(x):
    print(json.dumps(x, indent=2, ensure_ascii=False))


def need_yes(a, what):
    if not a.yes:
        sys.exit(f"Refusing to {what} without --yes. Show the user exactly what will be sent and get their OK first.")


def me_id():
    return call("me", {"fields": "user_id"}).get("user_id") or call("me", {"fields": "id"})["id"]


MEDIA_FIELDS = "id,caption,media_type,media_product_type,permalink,timestamp,like_count,comments_count,thumbnail_url,media_url"


def cmd_whoami(a):
    out(call("me", {"fields": "user_id,username,name,account_type,profile_picture_url,followers_count,follows_count,media_count,biography,website"}))


def cmd_media(a):
    out(call("me/media", {"fields": MEDIA_FIELDS, "limit": a.limit}).get("data", []))


def media_insights(mid, metrics):
    r = call(f"{mid}/insights", {"metric": metrics})
    return {m["name"]: (m.get("values") or [{}])[0].get("value", m.get("total_value", {}).get("value")) for m in r.get("data", [])}


DEFAULT_MEDIA_METRICS = "reach,likes,comments,shares,saved,views,total_interactions"


def cmd_media_insights(a):
    out(media_insights(a.media_id, a.metrics or DEFAULT_MEDIA_METRICS))


def cmd_account_insights(a):
    until = datetime.now(timezone.utc)
    since = until - timedelta(days=min(a.days, 30))
    metrics = a.metrics or "reach,views,accounts_engaged,total_interactions,likes,comments,shares,saves,follows_and_unfollows,profile_links_taps"
    r = call(f"{me_id()}/insights", {"metric": metrics, "period": "day", "metric_type": "total_value",
                                     "since": int(since.timestamp()), "until": int(until.timestamp())})
    res = {}
    for m in r.get("data", []):
        tv = m.get("total_value", {})
        res[m["name"]] = tv.get("breakdowns") or tv.get("value")
    out({"days": min(a.days, 30), "metrics": res})


def cmd_report(a):
    who = call("me", {"fields": "username,followers_count,media_count"})
    items = call("me/media", {"fields": MEDIA_FIELDS, "limit": a.limit}).get("data", [])
    rows = []
    for m in items:
        try:
            ins = media_insights(m["id"], "reach,shares,saved,views")
        except SystemExit:
            ins = {}
        rows.append((m, ins))
    print(f"# @{who.get('username')}: {who.get('followers_count')} followers, {who.get('media_count')} posts\n")
    print("| Date | Type | Views | Reach | Likes | Comments | Shares | Saves | Caption |")
    print("|---|---|---|---|---|---|---|---|---|")
    for m, i in rows:
        cap = (m.get("caption") or "").replace("\n", " ").replace("|", "/")[:50]
        print(f"| {m['timestamp'][:10]} | {m.get('media_product_type') or m.get('media_type')} | {i.get('views', '')} | {i.get('reach', '')} | "
              f"{m.get('like_count', '')} | {m.get('comments_count', '')} | {i.get('shares', '')} | {i.get('saved', '')} | {cap} |")
    print("\nLinks:")
    for m, _ in rows:
        print(f"- {m['timestamp'][:10]} {m.get('permalink')}")


def cmd_comments(a):
    out(call(f"{a.media_id}/comments", {"fields": "id,text,username,timestamp,like_count,replies{id,text,username,timestamp}", "limit": a.limit}).get("data", []))


def cmd_reply(a):
    need_yes(a, "post a reply")
    out(call(f"{a.comment_id}/replies", {"message": a.text}, "POST"))


def wait_ready(cid, timeout=600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = call(cid, {"fields": "status_code,status"})
        code = s.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            sys.exit(f"Container {cid} failed: {s}")
        print(f"  processing... ({code})", file=sys.stderr)
        time.sleep(8)
    sys.exit(f"Container {cid} still not ready after {timeout}s")


def publish(uid, cid):
    wait_ready(cid)
    r = call(f"{uid}/media_publish", {"creation_id": cid}, "POST")
    pid = r.get("id")
    link = call(pid, {"fields": "permalink"}).get("permalink") if pid else None
    out({"published_media_id": pid, "permalink": link})


def cmd_publish_image(a):
    need_yes(a, "publish a post")
    uid = me_id()
    c = call(f"{uid}/media", {"image_url": a.url, "caption": a.caption or ""}, "POST")
    publish(uid, c["id"])


def cmd_publish_reel(a):
    need_yes(a, "publish a Reel")
    uid = me_id()
    p = {"media_type": "REELS", "video_url": a.url, "caption": a.caption or "", "share_to_feed": "true" if a.share_to_feed else "false"}
    if a.cover_url:
        p["cover_url"] = a.cover_url
    c = call(f"{uid}/media", p, "POST")
    publish(uid, c["id"])


def cmd_publish_carousel(a):
    need_yes(a, "publish a carousel")
    if not 2 <= len(a.urls) <= 10:
        sys.exit("A carousel needs 2 to 10 items.")
    uid = me_id()
    kids = []
    for u in a.urls:
        is_vid = u.lower().split("?")[0].endswith((".mp4", ".mov"))
        p = {"is_carousel_item": "true", ("video_url" if is_vid else "image_url"): u}
        if is_vid:
            p["media_type"] = "VIDEO"
        cid = call(f"{uid}/media", p, "POST")["id"]
        wait_ready(cid)
        kids.append(cid)
    c = call(f"{uid}/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": a.caption or ""}, "POST")
    publish(uid, c["id"])


def cmd_limit(a):
    out(call(f"{me_id()}/content_publishing_limit", {"fields": "config,quota_usage"}))


def cmd_refresh(a):
    need_yes(a, "refresh the token")
    out(call("refresh_access_token", {"grant_type": "ig_refresh_token"}, base=HOST.rstrip("/")))
    print("Save the new access_token in place of the old one (it lasts about 60 days).", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    def add(name, fn, *args):
        p = sp.add_parser(name); p.set_defaults(fn=fn)
        for spec in args:
            p.add_argument(*spec[0], **spec[1])
        return p
    Y = (["--yes"], {"action": "store_true", "help": "confirm the user approved this exact action"})
    add("whoami", cmd_whoami)
    add("media", cmd_media, (["--limit"], {"type": int, "default": 12}))
    add("report", cmd_report, (["--limit"], {"type": int, "default": 12}))
    add("media-insights", cmd_media_insights, (["media_id"], {}), (["--metrics"], {}))
    add("account-insights", cmd_account_insights, (["--days"], {"type": int, "default": 28}), (["--metrics"], {}))
    add("comments", cmd_comments, (["media_id"], {}), (["--limit"], {"type": int, "default": 50}))
    add("reply", cmd_reply, (["comment_id"], {}), (["text"], {}), Y)
    add("publish-image", cmd_publish_image, (["url"], {}), (["--caption"], {}), Y)
    add("publish-reel", cmd_publish_reel, (["url"], {}), (["--caption"], {}), (["--cover-url"], {}),
        (["--no-feed"], {"dest": "share_to_feed", "action": "store_false"}), Y)
    add("publish-carousel", cmd_publish_carousel, (["urls"], {"nargs": "+"}), (["--caption"], {}), Y)
    add("limit", cmd_limit)
    add("refresh-token", cmd_refresh, Y)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
