# マルチメディア研究会2026夏 講演資料

大分大学で研究室を始めて2年半の近況と、AIによって学生・研究活動・引き継ぎがどう変わったかを扱う18枚のBeamer資料です。LuaLaTeX、16:9で作成しています。

## ビルド

```sh
cd slides
make
```

必要なものはTeX Live（LuaLaTeX、latexmk、luatexja、原ノ味フォント）、`uv`、Pythonです。初回ビルド時にローカルの`.venv`を作り、MP4埋め込み処理に使う`pypdf`を導入します。

- 編集元：`main.tex`
- 動画埋め込み：`scripts/embed_richmedia.py`
- 素材：`assets/`
- 配布用PDF：`presentation/talk.pdf`
- 動画の予備ファイル：`presentation/buildabstract-demo-1min.mp4`

## 動画

12ページ目のBuild Abstractデモは、H.264/AACのMP4をPDF内のRich Mediaとして埋め込んでいます。Adobe Acrobat Readerで12ページ目を表示すると自動再生します。外部ファイルへの絶対パスには依存しません。

## スライド構成

- 大分大学DX人材育成プログラム、大学院教育、地域貢献
- DAIB、地域企業、共同研究費、GPUと資産管理
- 九州支部連合大会での研究室9件連続発表
- Build AbstractとCodexによる研究工程の作業化
- WI26論文、提案アルゴリズム、実験結果、査読評価
- GitHub・共有サーバによる引き継ぎとBuzzでの指示共有
- 大分大学を中心にした地域の知的循環

1ページ目は専用タイトル、7・12・18ページ目は全画面スライドです。通常ページは大きな一行メッセージ、`SECTION ID / セクション名`、本文の順で統一しています。
