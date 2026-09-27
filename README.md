# muranakaaa.github.io

村中の自己紹介ページ（about）。GitHub Pages で公開している。

https://muranakaaa.github.io/

## 構成

- `data/site.json` — タイトル・名前・冒頭の文・経歴・肩書き・SNS リンク・仕事・「好きな○○」の各リスト・音楽の一文とプレイリスト・ほしい物リスト・夢・募集
- `data/posts.json` — Xの投稿（本文・日付・写真のファイル名とサイズ）
- `images/` — 投稿の写真。`<投稿ID>-<連番>.jpg`
- `template.html` — 両ページ共通の雛形。CSS と写真の全画面表示の JS もここ
- `build.py` — `data/` と `template.html` から `index.html`（about）と `posts.html`（好きな自分のポスト）を生成する。最終更新日は実行日

## 更新する

1. `data/site.json` か `data/posts.json` を書き換える。項目の追加・順序は `build.py` の `top_body`
2. `python3 build.py`
3. commit して push する。Pages が `main` の `/` をそのまま配信する

## 投稿を足す

1. 取得する（`<id>` は投稿URL末尾の数字）

```
curl -sL "https://cdn.syndication.twimg.com/tweet-result?id=<id>&lang=ja&token=a<id>"
```

2. 本文・日付・写真を `data/posts.json` に追記し、写真を `images/` に置く（`?format=jpg&name=medium` で取る）
3. `python3 build.py`
