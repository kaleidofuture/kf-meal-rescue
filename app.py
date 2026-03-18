"""KF-MealRescue — Turn leftover ingredients into recipe ideas."""

import streamlit as st

st.set_page_config(
    page_title="KF-MealRescue",
    page_icon="\U0001F373",
    layout="centered",
)

from components.header import render_header
from components.footer import render_footer
from components.i18n import t

import re

# --- Header ---
render_header()

# --- Preset recipe database (keyword-based) ---
RECIPE_DB = [
    {
        "name_ja": "チキンカレー",
        "name_en": "Chicken Curry",
        "ingredients": ["鶏肉", "chicken", "玉ねぎ", "onion", "じゃがいも", "potato",
                        "にんじん", "carrot", "カレールー", "curry roux"],
        "url": "https://www.kurashiru.com/recipes/search?query=チキンカレー",
    },
    {
        "name_ja": "肉じゃが",
        "name_en": "Nikujaga (Meat & Potatoes)",
        "ingredients": ["牛肉", "beef", "豚肉", "pork", "じゃがいも", "potato",
                        "玉ねぎ", "onion", "にんじん", "carrot", "しらたき", "糸こんにゃく"],
        "url": "https://www.kurashiru.com/recipes/search?query=肉じゃが",
    },
    {
        "name_ja": "野菜炒め",
        "name_en": "Stir-fried Vegetables",
        "ingredients": ["キャベツ", "cabbage", "もやし", "bean sprouts", "にんじん", "carrot",
                        "豚肉", "pork", "ピーマン", "bell pepper"],
        "url": "https://www.kurashiru.com/recipes/search?query=野菜炒め",
    },
    {
        "name_ja": "親子丼",
        "name_en": "Oyakodon (Chicken & Egg Bowl)",
        "ingredients": ["鶏肉", "chicken", "卵", "egg", "玉ねぎ", "onion", "ご飯", "rice"],
        "url": "https://www.kurashiru.com/recipes/search?query=親子丼",
    },
    {
        "name_ja": "トマトパスタ",
        "name_en": "Tomato Pasta",
        "ingredients": ["パスタ", "pasta", "トマト", "tomato", "にんにく", "garlic",
                        "玉ねぎ", "onion", "ベーコン", "bacon", "オリーブオイル", "olive oil"],
        "url": "https://www.kurashiru.com/recipes/search?query=トマトパスタ",
    },
    {
        "name_ja": "味噌汁",
        "name_en": "Miso Soup",
        "ingredients": ["豆腐", "tofu", "わかめ", "wakame", "味噌", "miso",
                        "ねぎ", "green onion", "だし", "dashi"],
        "url": "https://www.kurashiru.com/recipes/search?query=味噌汁",
    },
    {
        "name_ja": "オムライス",
        "name_en": "Omurice (Omelette Rice)",
        "ingredients": ["卵", "egg", "ご飯", "rice", "鶏肉", "chicken",
                        "玉ねぎ", "onion", "ケチャップ", "ketchup"],
        "url": "https://www.kurashiru.com/recipes/search?query=オムライス",
    },
    {
        "name_ja": "豚キムチ",
        "name_en": "Pork Kimchi Stir-fry",
        "ingredients": ["豚肉", "pork", "キムチ", "kimchi", "もやし", "bean sprouts",
                        "ニラ", "chives", "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/recipes/search?query=豚キムチ",
    },
    {
        "name_ja": "ポテトサラダ",
        "name_en": "Potato Salad",
        "ingredients": ["じゃがいも", "potato", "きゅうり", "cucumber", "ハム", "ham",
                        "卵", "egg", "マヨネーズ", "mayonnaise", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/recipes/search?query=ポテトサラダ",
    },
    {
        "name_ja": "焼きそば",
        "name_en": "Yakisoba (Fried Noodles)",
        "ingredients": ["中華麺", "noodles", "キャベツ", "cabbage", "豚肉", "pork",
                        "もやし", "bean sprouts", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/recipes/search?query=焼きそば",
    },
    {
        "name_ja": "チャーハン",
        "name_en": "Fried Rice",
        "ingredients": ["ご飯", "rice", "卵", "egg", "ねぎ", "green onion",
                        "チャーシュー", "ham", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/recipes/search?query=チャーハン",
    },
    {
        "name_ja": "麻婆豆腐",
        "name_en": "Mapo Tofu",
        "ingredients": ["豆腐", "tofu", "ひき肉", "ground meat", "ねぎ", "green onion",
                        "にんにく", "garlic", "しょうが", "ginger", "豆板醤", "doubanjiang"],
        "url": "https://www.kurashiru.com/recipes/search?query=麻婆豆腐",
    },
    {
        "name_ja": "鮭のムニエル",
        "name_en": "Salmon Meuniere",
        "ingredients": ["鮭", "salmon", "バター", "butter", "レモン", "lemon", "小麦粉", "flour"],
        "url": "https://www.kurashiru.com/recipes/search?query=鮭のムニエル",
    },
    {
        "name_ja": "唐揚げ",
        "name_en": "Karaage (Fried Chicken)",
        "ingredients": ["鶏肉", "chicken", "しょうが", "ginger", "にんにく", "garlic",
                        "醤油", "soy sauce", "片栗粉", "potato starch"],
        "url": "https://www.kurashiru.com/recipes/search?query=唐揚げ",
    },
    {
        "name_ja": "グラタン",
        "name_en": "Gratin",
        "ingredients": ["マカロニ", "macaroni", "鶏肉", "chicken", "玉ねぎ", "onion",
                        "牛乳", "milk", "バター", "butter", "チーズ", "cheese", "小麦粉", "flour"],
        "url": "https://www.kurashiru.com/recipes/search?query=グラタン",
    },
    {
        "name_ja": "ハンバーグ",
        "name_en": "Hamburg Steak",
        "ingredients": ["ひき肉", "ground meat", "玉ねぎ", "onion", "卵", "egg",
                        "パン粉", "breadcrumbs", "牛乳", "milk"],
        "url": "https://www.kurashiru.com/recipes/search?query=ハンバーグ",
    },
    {
        "name_ja": "きんぴらごぼう",
        "name_en": "Kinpira Gobo (Braised Burdock)",
        "ingredients": ["ごぼう", "burdock", "にんじん", "carrot", "ごま油", "sesame oil",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/recipes/search?query=きんぴらごぼう",
    },
    {
        "name_ja": "豚の生姜焼き",
        "name_en": "Ginger Pork",
        "ingredients": ["豚肉", "pork", "しょうが", "ginger", "玉ねぎ", "onion",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/recipes/search?query=豚の生姜焼き",
    },
    {
        "name_ja": "サンドイッチ",
        "name_en": "Sandwich",
        "ingredients": ["パン", "bread", "レタス", "lettuce", "トマト", "tomato",
                        "ハム", "ham", "チーズ", "cheese", "卵", "egg", "マヨネーズ", "mayonnaise"],
        "url": "https://www.kurashiru.com/recipes/search?query=サンドイッチ",
    },
    {
        "name_ja": "お好み焼き",
        "name_en": "Okonomiyaki (Japanese Pancake)",
        "ingredients": ["キャベツ", "cabbage", "小麦粉", "flour", "卵", "egg",
                        "豚肉", "pork", "天かす", "tenkasu", "ソース", "sauce"],
        "url": "https://www.kurashiru.com/recipes/search?query=お好み焼き",
    },
]


def normalize(text: str) -> str:
    """Normalize ingredient text for matching."""
    return text.strip().lower()


def match_recipes(user_ingredients: list[str]) -> list[dict]:
    """Match user ingredients against recipe database."""
    user_set = {normalize(ing) for ing in user_ingredients if ing.strip()}
    if not user_set:
        return []

    results = []
    for recipe in RECIPE_DB:
        recipe_ings = {normalize(ing) for ing in recipe["ingredients"]}
        matched = set()
        for u_ing in user_set:
            for r_ing in recipe_ings:
                if u_ing in r_ing or r_ing in u_ing:
                    matched.add(r_ing)
        if matched:
            missing = recipe_ings - matched
            score = len(matched) / len(recipe_ings)
            results.append({
                "recipe": recipe,
                "matched": matched,
                "missing": missing,
                "score": score,
            })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results


# --- Mode selection ---
mode = st.radio(
    t("mode_label"),
    [t("mode_search"), t("mode_url")],
    horizontal=True,
)

if mode == t("mode_search"):
    # --- Ingredient search mode ---
    st.subheader(t("input_ingredients_title"))
    st.caption(t("input_ingredients_help"))

    ingredients_text = st.text_area(
        t("ingredients_label"),
        height=120,
        placeholder=t("ingredients_placeholder"),
    )

    if st.button(t("search_button"), type="primary"):
        ingredients = [
            ing.strip()
            for ing in re.split(r"[,、\n\r]+", ingredients_text)
            if ing.strip()
        ]

        if not ingredients:
            st.warning(t("no_ingredients"))
        else:
            st.markdown(f"**{t('your_ingredients')}**: {', '.join(ingredients)}")

            with st.spinner(t("processing")):
                results = match_recipes(ingredients)

            if results:
                st.success(t("found_recipes").format(count=len(results)))
                for i, res in enumerate(results):
                    recipe = res["recipe"]
                    lang = st.session_state.get("lang", "ja")
                    name = recipe["name_ja"] if lang == "ja" else recipe["name_en"]

                    score_pct = int(res["score"] * 100)
                    with st.expander(f"{name}  ({t('match_rate')}: {score_pct}%)", expanded=(i < 3)):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**{t('matched_label')}**")
                            for m in sorted(res["matched"]):
                                st.markdown(f"- :green[{m}]")
                        with col2:
                            if res["missing"]:
                                st.markdown(f"**{t('missing_label')}**")
                                for m in sorted(res["missing"]):
                                    st.markdown(f"- :red[{m}]")
                            else:
                                st.markdown(f"**:green[{t('all_matched')}]**")
                        st.markdown(f"[{t('search_recipe_link')}]({recipe['url']})")
            else:
                st.info(t("no_match"))

else:
    # --- URL parse mode ---
    st.subheader(t("url_mode_title"))
    st.caption(t("url_mode_help"))

    recipe_url = st.text_input(t("url_input_label"), placeholder="https://www.kurashiru.com/recipes/...")

    if recipe_url and st.button(t("parse_button"), type="primary"):
        with st.spinner(t("processing")):
            try:
                from recipe_scrapers import scrape_html
                import urllib.request

                req = urllib.request.Request(recipe_url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=10) as response:
                    html = response.read().decode("utf-8", errors="replace")

                scraper = scrape_html(html=html, org_url=recipe_url)

                st.success(t("parse_success"))
                st.markdown(f"### {scraper.title()}")

                if scraper.total_time():
                    st.markdown(f"**{t('cook_time')}**: {scraper.total_time()} {t('minutes')}")
                if scraper.yields():
                    st.markdown(f"**{t('servings')}**: {scraper.yields()}")

                st.markdown(f"**{t('ingredients_list')}**:")
                for ing in scraper.ingredients():
                    st.markdown(f"- {ing}")

                st.markdown(f"**{t('instructions_label')}**:")
                for step_num, step in enumerate(scraper.instructions_list(), 1):
                    st.markdown(f"{step_num}. {step}")

            except Exception as e:
                st.error(t("parse_error").format(error=str(e)))

# --- Footer ---
render_footer(libraries=["recipe-scrapers", "ingredient-parser-nlp"])
