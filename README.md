# KF-MealRescue

> 手持ちの食材からレシピを見つけて、毎日の献立決めをラクにする。

## The Problem

毎日の献立決めがしんどい。冷蔵庫にある食材で何が作れるか分からない。

## How It Works

1. 手持ちの食材をテキスト入力（カンマ・改行区切り）
2. プリセットレシピDBから食材マッチングで検索
3. 一致率順にレシピを表示、足りない食材も確認可能
4. レシピURLを貼り付けて材料・手順を抽出するモードもあり

## Libraries Used

- **recipe-scrapers** — レシピサイトのURLから材料・手順を構造化抽出
- **ingredient-parser-nlp** — 食材テキストの自然言語パース

## Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

Hosted on [Hugging Face Spaces](https://huggingface.co/spaces/mitoi/kf-meal-rescue).

---

Part of the [KaleidoFuture AI-Driven Development Research](https://kaleidofuture.com) — proving that everyday problems can be solved with existing libraries, no AI model required.
