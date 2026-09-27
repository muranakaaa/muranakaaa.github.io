"""data/ と images/ から index.html と posts.html を生成する。"""

import datetime
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
DATA = ROOT / "data"
POSTS_PAGE = "posts.html"
POSTS_TITLE = "好きな自分のポスト"


def read_json(name: str) -> dict | list:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


def format_date(iso: str) -> str:
    year, month, day = iso.split("-")
    return f"{year}.{int(month):02d}.{int(day):02d}"


def block(title: str, body: str) -> str:
    return f"<h3>{html.escape(title)}</h3>\n{body}"


def roles_line(text: str) -> str:
    parts = [part for part in text.split("。") if part]
    spans = "".join(f'<span class="role">{html.escape(part)}。</span>' for part in parts)
    return f"<p>{spans}</p>"


def lists(groups: list[dict]) -> str:
    return "\n".join(block(g["title"], f'<p>{"、".join(html.escape(x) for x in g["items"])}</p>') for g in groups)


def bullets(title: str, items: list[str]) -> str:
    rows = "".join(f"<li>{html.escape(item)}</li>" for item in items)
    return block(title, f'<ul class="items">{rows}</ul>')


def render_thumbs(post: dict) -> str:
    if not post["media"]:
        return ""
    thumbs = "".join(
        f'<button class="shot" type="button" data-post="{post["id"]}" data-index="{i}" aria-label="写真{i + 1}">'
        f'<img src="images/{m["file"]}" width="{m["w"]}" height="{m["h"]}" loading="lazy" decoding="async" alt=""></button>'
        for i, m in enumerate(post["media"])
    )
    return f'<div class="thumbs">{thumbs}</div>'


def render_post(post: dict, handle: str) -> str:
    url = f"https://x.com/{handle}/status/{post['id']}"
    text = html.escape(post["text"]).replace("\n", "<br>")
    return (
        f'<li><h3><a href="{url}" target="_blank" rel="noopener">{format_date(post["date"])}</a></h3>'
        f"<p>{text}</p>{render_thumbs(post)}</li>"
    )


def link(label: str, url: str) -> str:
    return f'<a href="{url}" target="_blank" rel="noopener">{html.escape(label)}</a>'


def links(items: list[dict]) -> str:
    return f'<p>{" / ".join(link(x["label"], x["url"]) for x in items)}</p>'


def intro_paragraph(site: dict) -> str:
    text = html.escape(site["profile_intro"])
    marker = "筑波大学国際総合学類卒業。"
    text = text.replace(marker, marker + '<br class="pc-br">', 1)
    return f"<p>{text}</p>"


def music(site: dict) -> str:
    url = html.escape(f'https://open.spotify.com/playlist/{site["playlist_id"]}', quote=True)
    return (
        f'<p>{html.escape(site["music_note"])}</p>'
        f'<p><a class="url" href="{url}" target="_blank" rel="noopener">{url}</a></p>'
    )


def lightbox_data(posts: list[dict]) -> str:
    return json.dumps(
        {p["id"]: [{"src": f"images/{m['file']}", "w": m["w"], "h": m["h"]} for m in p["media"]] for p in posts},
        ensure_ascii=False,
        separators=(",", ":"),
    )


def render_page(site: dict, template: str, values: dict[str, str]) -> str:
    output = template
    for key, value in {
        "DESCRIPTION": site["description"],
        "URL": site["url"],
        "OGP_IMAGE": site["ogp_image"],
        "HANDLE": site["handle"],
        **values,
    }.items():
        output = output.replace("{{" + key + "}}", value)
    leftover = re.findall(r"{{[A-Z_]+}}", output)
    if leftover:
        raise SystemExit(f"未置換のプレースホルダ: {leftover}")
    return output


def main() -> None:
    site = read_json("site.json")
    posts = read_json("posts.json")
    posts.sort(key=lambda p: p["date"], reverse=True)
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    updated = datetime.date.today().strftime("%Y.%m.%d")

    top_body = "\n".join(
        [
            intro_paragraph(site),
            roles_line(site["roles"]),
            links(site["links"]),
            lists(site["likes"]),
            block("好きな音楽", music(site)),
            block("ほしいもの", f'<p>{link("Amazon のほしい物リスト", site["wishlist_url"])}</p>'),
            bullets(site["wanted"]["title"], site["wanted"]["items"]),
            block(POSTS_TITLE, f'<p>X の投稿から選んだ<a href="{POSTS_PAGE}">{len(posts)}件</a>。</p>'),
        ]
    )
    index = render_page(
        site,
        template,
        {
            "TITLE": site["title"],
            "PAGE": "",
            "H1": site["title"],
            "UPDATED": f'<p class="updated">最終更新 {updated}</p>',
            "BODY": top_body,
            "LIGHTBOX_DATA": "{}",
        },
    )
    (ROOT / "index.html").write_text(index, encoding="utf-8")

    posts_body = (
        f"<p>X の投稿から選んだ{len(posts)}件。日付を押すと元の投稿が開き、写真を押すと大きく表示します。</p>"
        f'<p><a href="./">{html.escape(site["title"])} に戻る</a></p>'
        f'<ul class="posts">{"".join(render_post(p, site["handle"]) for p in posts)}</ul>'
    )
    posts_page = render_page(
        site,
        template,
        {
            "TITLE": POSTS_TITLE,
            "PAGE": POSTS_PAGE,
            "H1": POSTS_TITLE,
            "UPDATED": "",
            "BODY": posts_body,
            "LIGHTBOX_DATA": lightbox_data(posts),
        },
    )
    (ROOT / POSTS_PAGE).write_text(posts_page, encoding="utf-8")
    print(f"index.html: {len(site['likes'])} lists / {POSTS_PAGE}: {len(posts)} posts / 最終更新 {updated}")


if __name__ == "__main__":
    main()
