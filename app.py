"""KF-MealRescue — Turn leftover ingredients into recipe ideas."""

import streamlit as st

st.set_page_config(
    page_title="KF-MealRescue",
    page_icon="\U0001F373",
    layout="centered",
)

from components.header import render_header
from components.footer import render_footer
from components.i18n import t, get_lang

import re
import random
from datetime import datetime

# --- Ingredient presets (checkbox-based selection) ---
INGREDIENT_PRESETS = {
    "meat": {
        "emoji": "\U0001F969",
        "items_ja": ["鶏もも肉", "鶏むね肉", "豚バラ", "豚ロース", "牛切り落とし", "ひき肉", "ベーコン", "ウインナー"],
        "items_en": ["Chicken thigh", "Chicken breast", "Pork belly", "Pork loin", "Beef slices", "Ground meat", "Bacon", "Sausage"],
    },
    "seafood": {
        "emoji": "\U0001F41F",
        "items_ja": ["鮭", "サバ", "エビ", "ツナ缶", "イカ", "アサリ", "タラ", "しらす"],
        "items_en": ["Salmon", "Mackerel", "Shrimp", "Canned tuna", "Squid", "Clams", "Cod", "Whitebait"],
    },
    "vegetable": {
        "emoji": "\U0001F96C",
        "items_ja": ["にんじん", "たまねぎ", "じゃがいも", "キャベツ", "トマト", "ほうれん草", "大根", "もやし", "ピーマン", "なす", "きのこ", "ブロッコリー"],
        "items_en": ["Carrot", "Onion", "Potato", "Cabbage", "Tomato", "Spinach", "Daikon", "Bean sprouts", "Bell pepper", "Eggplant", "Mushroom", "Broccoli"],
    },
    "other": {
        "emoji": "\U0001F95A",
        "items_ja": ["卵", "豆腐", "牛乳", "チーズ", "油揚げ", "こんにゃく", "パスタ", "うどん", "ご飯"],
        "items_en": ["Egg", "Tofu", "Milk", "Cheese", "Fried tofu", "Konjac", "Pasta", "Udon", "Rice"],
    },
}

# --- Preset ingredient bundles ---
INGREDIENT_BUNDLES = {
    "fridge_staples": {
        "items_ja": ["卵", "たまねぎ", "にんじん", "豆腐", "牛乳", "ご飯", "もやし", "キャベツ"],
        "items_en": ["Egg", "Onion", "Carrot", "Tofu", "Milk", "Rice", "Bean sprouts", "Cabbage"],
    },
    "meat_lover": {
        "items_ja": ["鶏もも肉", "豚バラ", "ひき肉", "たまねぎ", "にんじん", "卵", "ご飯"],
        "items_en": ["Chicken thigh", "Pork belly", "Ground meat", "Onion", "Carrot", "Egg", "Rice"],
    },
    "healthy_set": {
        "items_ja": ["鶏むね肉", "ブロッコリー", "ほうれん草", "トマト", "卵", "豆腐", "きのこ"],
        "items_en": ["Chicken breast", "Broccoli", "Spinach", "Tomato", "Egg", "Tofu", "Mushroom"],
    },
    "japanese_basic": {
        "items_ja": ["鮭", "大根", "豆腐", "油揚げ", "たまねぎ", "にんじん", "ご飯", "卵"],
        "items_en": ["Salmon", "Daikon", "Tofu", "Fried tofu", "Onion", "Carrot", "Rice", "Egg"],
    },
}

# --- Header ---
render_header()

# --- Preset recipe database (keyword-based) ---
# Categories: main(主菜), side(副菜), soup(汁物), bowl(丼), noodle(麺)
RECIPE_DB = [
    # === 主菜 (Main dishes) ===
    {
        "name_ja": "チキンカレー",
        "name_en": "Chicken Curry",
        "ingredients": ["鶏肉", "chicken", "玉ねぎ", "onion", "じゃがいも", "potato",
                        "にんじん", "carrot", "カレールー", "curry roux"],
        "url": "https://www.kurashiru.com/search?query=チキンカレー",
        "category": "main",
        "time_minutes": 40,
    },
    {
        "name_ja": "肉じゃが",
        "name_en": "Nikujaga (Meat & Potatoes)",
        "ingredients": ["牛肉", "beef", "豚肉", "pork", "じゃがいも", "potato",
                        "玉ねぎ", "onion", "にんじん", "carrot", "しらたき", "糸こんにゃく"],
        "url": "https://www.kurashiru.com/search?query=肉じゃが",
        "category": "main",
        "time_minutes": 35,
    },
    {
        "name_ja": "野菜炒め",
        "name_en": "Stir-fried Vegetables",
        "ingredients": ["キャベツ", "cabbage", "もやし", "bean sprouts", "にんじん", "carrot",
                        "豚肉", "pork", "ピーマン", "bell pepper"],
        "url": "https://www.kurashiru.com/search?query=野菜炒め",
        "category": "main",
        "time_minutes": 10,
    },
    {
        "name_ja": "トマトパスタ",
        "name_en": "Tomato Pasta",
        "ingredients": ["パスタ", "pasta", "トマト", "tomato", "にんにく", "garlic",
                        "玉ねぎ", "onion", "ベーコン", "bacon", "オリーブオイル", "olive oil"],
        "url": "https://www.kurashiru.com/search?query=トマトパスタ",
        "category": "noodle",
        "time_minutes": 20,
    },
    {
        "name_ja": "オムライス",
        "name_en": "Omurice (Omelette Rice)",
        "ingredients": ["卵", "egg", "ご飯", "rice", "鶏肉", "chicken",
                        "玉ねぎ", "onion", "ケチャップ", "ketchup"],
        "url": "https://www.kurashiru.com/search?query=オムライス",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "豚キムチ",
        "name_en": "Pork Kimchi Stir-fry",
        "ingredients": ["豚肉", "pork", "キムチ", "kimchi", "もやし", "bean sprouts",
                        "ニラ", "chives", "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=豚キムチ",
        "category": "main",
        "time_minutes": 10,
    },
    {
        "name_ja": "焼きそば",
        "name_en": "Yakisoba (Fried Noodles)",
        "ingredients": ["中華麺", "noodles", "キャベツ", "cabbage", "豚肉", "pork",
                        "もやし", "bean sprouts", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/search?query=焼きそば",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "チャーハン",
        "name_en": "Fried Rice",
        "ingredients": ["ご飯", "rice", "卵", "egg", "ねぎ", "green onion",
                        "チャーシュー", "ham", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/search?query=チャーハン",
        "category": "bowl",
        "time_minutes": 10,
    },
    {
        "name_ja": "麻婆豆腐",
        "name_en": "Mapo Tofu",
        "ingredients": ["豆腐", "tofu", "ひき肉", "ground meat", "ねぎ", "green onion",
                        "にんにく", "garlic", "しょうが", "ginger", "豆板醤", "doubanjiang"],
        "url": "https://www.kurashiru.com/search?query=麻婆豆腐",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "鮭のムニエル",
        "name_en": "Salmon Meuniere",
        "ingredients": ["鮭", "salmon", "バター", "butter", "レモン", "lemon", "小麦粉", "flour"],
        "url": "https://www.kurashiru.com/search?query=鮭のムニエル",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "唐揚げ",
        "name_en": "Karaage (Fried Chicken)",
        "ingredients": ["鶏肉", "chicken", "しょうが", "ginger", "にんにく", "garlic",
                        "醤油", "soy sauce", "片栗粉", "potato starch"],
        "url": "https://www.kurashiru.com/search?query=唐揚げ",
        "category": "main",
        "time_minutes": 25,
    },
    {
        "name_ja": "グラタン",
        "name_en": "Gratin",
        "ingredients": ["マカロニ", "macaroni", "鶏肉", "chicken", "玉ねぎ", "onion",
                        "牛乳", "milk", "バター", "butter", "チーズ", "cheese", "小麦粉", "flour"],
        "url": "https://www.kurashiru.com/search?query=グラタン",
        "category": "main",
        "time_minutes": 40,
    },
    {
        "name_ja": "ハンバーグ",
        "name_en": "Hamburg Steak",
        "ingredients": ["ひき肉", "ground meat", "玉ねぎ", "onion", "卵", "egg",
                        "パン粉", "breadcrumbs", "牛乳", "milk"],
        "url": "https://www.kurashiru.com/search?query=ハンバーグ",
        "category": "main",
        "time_minutes": 30,
    },
    {
        "name_ja": "豚の生姜焼き",
        "name_en": "Ginger Pork",
        "ingredients": ["豚肉", "pork", "しょうが", "ginger", "玉ねぎ", "onion",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=豚の生姜焼き",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "サンドイッチ",
        "name_en": "Sandwich",
        "ingredients": ["パン", "bread", "レタス", "lettuce", "トマト", "tomato",
                        "ハム", "ham", "チーズ", "cheese", "卵", "egg", "マヨネーズ", "mayonnaise"],
        "url": "https://www.kurashiru.com/search?query=サンドイッチ",
        "category": "main",
        "time_minutes": 10,
    },
    {
        "name_ja": "お好み焼き",
        "name_en": "Okonomiyaki (Japanese Pancake)",
        "ingredients": ["キャベツ", "cabbage", "小麦粉", "flour", "卵", "egg",
                        "豚肉", "pork", "天かす", "tenkasu", "ソース", "sauce"],
        "url": "https://www.kurashiru.com/search?query=お好み焼き",
        "category": "main",
        "time_minutes": 25,
    },
    {
        "name_ja": "鶏の照り焼き",
        "name_en": "Teriyaki Chicken",
        "ingredients": ["鶏肉", "chicken", "醤油", "soy sauce", "みりん", "mirin",
                        "砂糖", "sugar"],
        "url": "https://www.kurashiru.com/search?query=鶏の照り焼き",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "サバの味噌煮",
        "name_en": "Saba Misoni (Mackerel in Miso)",
        "ingredients": ["サバ", "mackerel", "味噌", "miso", "しょうが", "ginger",
                        "砂糖", "sugar", "酒", "sake"],
        "url": "https://www.kurashiru.com/search?query=サバの味噌煮",
        "category": "main",
        "time_minutes": 25,
    },
    {
        "name_ja": "エビチリ",
        "name_en": "Shrimp in Chili Sauce",
        "ingredients": ["エビ", "shrimp", "ケチャップ", "ketchup", "豆板醤", "doubanjiang",
                        "ねぎ", "green onion", "にんにく", "garlic", "しょうが", "ginger"],
        "url": "https://www.kurashiru.com/search?query=エビチリ",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "回鍋肉",
        "name_en": "Twice-Cooked Pork",
        "ingredients": ["豚肉", "pork", "キャベツ", "cabbage", "ピーマン", "bell pepper",
                        "味噌", "miso", "豆板醤", "doubanjiang"],
        "url": "https://www.kurashiru.com/search?query=回鍋肉",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "チキン南蛮",
        "name_en": "Chicken Nanban",
        "ingredients": ["鶏肉", "chicken", "卵", "egg", "小麦粉", "flour",
                        "酢", "vinegar", "マヨネーズ", "mayonnaise", "玉ねぎ", "onion"],
        "url": "https://www.kurashiru.com/search?query=チキン南蛮",
        "category": "main",
        "time_minutes": 30,
    },
    {
        "name_ja": "ぶり大根",
        "name_en": "Buri Daikon (Yellowtail & Daikon)",
        "ingredients": ["ぶり", "yellowtail", "大根", "daikon", "しょうが", "ginger",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=ぶり大根",
        "category": "main",
        "time_minutes": 40,
    },
    {
        "name_ja": "酢豚",
        "name_en": "Sweet and Sour Pork",
        "ingredients": ["豚肉", "pork", "玉ねぎ", "onion", "にんじん", "carrot",
                        "ピーマン", "bell pepper", "酢", "vinegar", "ケチャップ", "ketchup"],
        "url": "https://www.kurashiru.com/search?query=酢豚",
        "category": "main",
        "time_minutes": 30,
    },
    {
        "name_ja": "肉豆腐",
        "name_en": "Niku Tofu (Meat & Tofu)",
        "ingredients": ["牛肉", "beef", "豆腐", "tofu", "ねぎ", "green onion",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=肉豆腐",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "アジフライ",
        "name_en": "Aji Fry (Fried Horse Mackerel)",
        "ingredients": ["アジ", "horse mackerel", "小麦粉", "flour", "卵", "egg",
                        "パン粉", "breadcrumbs"],
        "url": "https://www.kurashiru.com/search?query=アジフライ",
        "category": "main",
        "time_minutes": 25,
    },
    {
        "name_ja": "豚カツ",
        "name_en": "Tonkatsu (Pork Cutlet)",
        "ingredients": ["豚ロース", "pork loin", "小麦粉", "flour", "卵", "egg",
                        "パン粉", "breadcrumbs"],
        "url": "https://www.kurashiru.com/search?query=豚カツ",
        "category": "main",
        "time_minutes": 25,
    },
    {
        "name_ja": "鶏つくね",
        "name_en": "Chicken Tsukune (Meatballs)",
        "ingredients": ["鶏ひき肉", "ground chicken", "ねぎ", "green onion",
                        "卵", "egg", "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=鶏つくね",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "タラのホイル焼き",
        "name_en": "Cod Foil Bake",
        "ingredients": ["タラ", "cod", "玉ねぎ", "onion", "きのこ", "mushroom",
                        "バター", "butter", "レモン", "lemon"],
        "url": "https://www.kurashiru.com/search?query=タラのホイル焼き",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "餃子",
        "name_en": "Gyoza (Dumplings)",
        "ingredients": ["ひき肉", "ground meat", "キャベツ", "cabbage", "ニラ", "chives",
                        "にんにく", "garlic", "しょうが", "ginger", "餃子の皮", "gyoza wrappers"],
        "url": "https://www.kurashiru.com/search?query=餃子",
        "category": "main",
        "time_minutes": 35,
    },
    {
        "name_ja": "シチュー",
        "name_en": "Cream Stew",
        "ingredients": ["鶏肉", "chicken", "じゃがいも", "potato", "にんじん", "carrot",
                        "玉ねぎ", "onion", "牛乳", "milk", "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=クリームシチュー",
        "category": "main",
        "time_minutes": 40,
    },
    {
        "name_ja": "麻婆なす",
        "name_en": "Mapo Eggplant",
        "ingredients": ["なす", "eggplant", "ひき肉", "ground meat", "にんにく", "garlic",
                        "しょうが", "ginger", "豆板醤", "doubanjiang"],
        "url": "https://www.kurashiru.com/search?query=麻婆なす",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "イカの煮物",
        "name_en": "Simmered Squid",
        "ingredients": ["イカ", "squid", "大根", "daikon", "醤油", "soy sauce",
                        "みりん", "mirin", "しょうが", "ginger"],
        "url": "https://www.kurashiru.com/search?query=イカの煮物",
        "category": "main",
        "time_minutes": 25,
    },
    {
        "name_ja": "鶏ささみのチーズ焼き",
        "name_en": "Chicken Tender Cheese Bake",
        "ingredients": ["鶏肉", "chicken", "チーズ", "cheese", "トマト", "tomato"],
        "url": "https://www.kurashiru.com/search?query=ささみチーズ焼き",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "青椒肉絲",
        "name_en": "Chinjao Rosu (Pepper Steak)",
        "ingredients": ["牛肉", "beef", "ピーマン", "bell pepper", "たけのこ", "bamboo shoot",
                        "醤油", "soy sauce", "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=青椒肉絲",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "アサリの酒蒸し",
        "name_en": "Sake-Steamed Clams",
        "ingredients": ["アサリ", "clams", "酒", "sake", "にんにく", "garlic",
                        "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=アサリの酒蒸し",
        "category": "main",
        "time_minutes": 10,
    },
    # === 副菜 (Side dishes) ===
    {
        "name_ja": "ポテトサラダ",
        "name_en": "Potato Salad",
        "ingredients": ["じゃがいも", "potato", "きゅうり", "cucumber", "ハム", "ham",
                        "卵", "egg", "マヨネーズ", "mayonnaise", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/search?query=ポテトサラダ",
        "category": "side",
        "time_minutes": 20,
    },
    {
        "name_ja": "きんぴらごぼう",
        "name_en": "Kinpira Gobo (Braised Burdock)",
        "ingredients": ["ごぼう", "burdock", "にんじん", "carrot", "ごま油", "sesame oil",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=きんぴらごぼう",
        "category": "side",
        "time_minutes": 15,
    },
    {
        "name_ja": "ほうれん草のおひたし",
        "name_en": "Boiled Spinach (Ohitashi)",
        "ingredients": ["ほうれん草", "spinach", "醤油", "soy sauce", "かつお節", "bonito flakes"],
        "url": "https://www.kurashiru.com/search?query=ほうれん草のおひたし",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "冷奴",
        "name_en": "Hiyayakko (Cold Tofu)",
        "ingredients": ["豆腐", "tofu", "ねぎ", "green onion", "しょうが", "ginger"],
        "url": "https://www.kurashiru.com/search?query=冷奴",
        "category": "side",
        "time_minutes": 3,
    },
    {
        "name_ja": "ナムル",
        "name_en": "Namul (Korean Seasoned Vegetables)",
        "ingredients": ["もやし", "bean sprouts", "ほうれん草", "spinach", "にんじん", "carrot",
                        "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=ナムル",
        "category": "side",
        "time_minutes": 10,
    },
    {
        "name_ja": "卵焼き",
        "name_en": "Tamagoyaki (Japanese Omelette)",
        "ingredients": ["卵", "egg", "砂糖", "sugar", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=卵焼き",
        "category": "side",
        "time_minutes": 10,
    },
    {
        "name_ja": "ひじきの煮物",
        "name_en": "Simmered Hijiki Seaweed",
        "ingredients": ["ひじき", "hijiki", "にんじん", "carrot", "油揚げ", "fried tofu",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=ひじきの煮物",
        "category": "side",
        "time_minutes": 20,
    },
    {
        "name_ja": "白和え",
        "name_en": "Shira-ae (Tofu Salad)",
        "ingredients": ["豆腐", "tofu", "ほうれん草", "spinach", "にんじん", "carrot",
                        "ごま", "sesame"],
        "url": "https://www.kurashiru.com/search?query=白和え",
        "category": "side",
        "time_minutes": 15,
    },
    {
        "name_ja": "かぼちゃの煮物",
        "name_en": "Simmered Pumpkin",
        "ingredients": ["かぼちゃ", "pumpkin", "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=かぼちゃの煮物",
        "category": "side",
        "time_minutes": 20,
    },
    {
        "name_ja": "もやしのごま和え",
        "name_en": "Bean Sprouts with Sesame",
        "ingredients": ["もやし", "bean sprouts", "ごま", "sesame", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=もやしのごま和え",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "ブロッコリーのおかか和え",
        "name_en": "Broccoli with Bonito",
        "ingredients": ["ブロッコリー", "broccoli", "かつお節", "bonito flakes", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=ブロッコリーおかか和え",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "なすの煮浸し",
        "name_en": "Simmered Eggplant",
        "ingredients": ["なす", "eggplant", "醤油", "soy sauce", "だし", "dashi",
                        "しょうが", "ginger"],
        "url": "https://www.kurashiru.com/search?query=なすの煮浸し",
        "category": "side",
        "time_minutes": 15,
    },
    {
        "name_ja": "大根サラダ",
        "name_en": "Daikon Salad",
        "ingredients": ["大根", "daikon", "かつお節", "bonito flakes", "ごま", "sesame"],
        "url": "https://www.kurashiru.com/search?query=大根サラダ",
        "category": "side",
        "time_minutes": 10,
    },
    {
        "name_ja": "ピーマンのおかか炒め",
        "name_en": "Stir-fried Bell Pepper with Bonito",
        "ingredients": ["ピーマン", "bell pepper", "かつお節", "bonito flakes",
                        "醤油", "soy sauce", "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=ピーマンおかか炒め",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "きゅうりの漬物",
        "name_en": "Pickled Cucumber",
        "ingredients": ["きゅうり", "cucumber", "塩", "salt", "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=きゅうりの漬物",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "コールスロー",
        "name_en": "Coleslaw",
        "ingredients": ["キャベツ", "cabbage", "にんじん", "carrot", "マヨネーズ", "mayonnaise",
                        "酢", "vinegar"],
        "url": "https://www.kurashiru.com/search?query=コールスロー",
        "category": "side",
        "time_minutes": 10,
    },
    {
        "name_ja": "マカロニサラダ",
        "name_en": "Macaroni Salad",
        "ingredients": ["マカロニ", "macaroni", "きゅうり", "cucumber", "ハム", "ham",
                        "マヨネーズ", "mayonnaise", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/search?query=マカロニサラダ",
        "category": "side",
        "time_minutes": 15,
    },
    {
        "name_ja": "切り干し大根",
        "name_en": "Dried Daikon Strips",
        "ingredients": ["切り干し大根", "dried daikon", "にんじん", "carrot", "油揚げ", "fried tofu",
                        "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=切り干し大根",
        "category": "side",
        "time_minutes": 20,
    },
    {
        "name_ja": "揚げ出し豆腐",
        "name_en": "Agedashi Tofu",
        "ingredients": ["豆腐", "tofu", "片栗粉", "potato starch", "だし", "dashi",
                        "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=揚げ出し豆腐",
        "category": "side",
        "time_minutes": 15,
    },
    {
        "name_ja": "トマトとモッツァレラのカプレーゼ",
        "name_en": "Caprese Salad",
        "ingredients": ["トマト", "tomato", "チーズ", "cheese", "オリーブオイル", "olive oil"],
        "url": "https://www.kurashiru.com/search?query=カプレーゼ",
        "category": "side",
        "time_minutes": 5,
    },
    # === 汁物 (Soups) ===
    {
        "name_ja": "味噌汁",
        "name_en": "Miso Soup",
        "ingredients": ["豆腐", "tofu", "わかめ", "wakame", "味噌", "miso",
                        "ねぎ", "green onion", "だし", "dashi"],
        "url": "https://www.kurashiru.com/search?query=味噌汁",
        "category": "soup",
        "time_minutes": 10,
    },
    {
        "name_ja": "豚汁",
        "name_en": "Tonjiru (Pork Miso Soup)",
        "ingredients": ["豚肉", "pork", "大根", "daikon", "にんじん", "carrot",
                        "こんにゃく", "konjac", "ねぎ", "green onion", "味噌", "miso"],
        "url": "https://www.kurashiru.com/search?query=豚汁",
        "category": "soup",
        "time_minutes": 25,
    },
    {
        "name_ja": "けんちん汁",
        "name_en": "Kenchin-jiru (Vegetable Soup)",
        "ingredients": ["大根", "daikon", "にんじん", "carrot", "こんにゃく", "konjac",
                        "豆腐", "tofu", "ねぎ", "green onion", "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=けんちん汁",
        "category": "soup",
        "time_minutes": 25,
    },
    {
        "name_ja": "コーンスープ",
        "name_en": "Corn Soup",
        "ingredients": ["コーン", "corn", "牛乳", "milk", "バター", "butter",
                        "玉ねぎ", "onion"],
        "url": "https://www.kurashiru.com/search?query=コーンスープ",
        "category": "soup",
        "time_minutes": 15,
    },
    {
        "name_ja": "かきたま汁",
        "name_en": "Egg Drop Soup",
        "ingredients": ["卵", "egg", "だし", "dashi", "ねぎ", "green onion"],
        "url": "https://www.kurashiru.com/search?query=かきたま汁",
        "category": "soup",
        "time_minutes": 5,
    },
    {
        "name_ja": "わかめスープ",
        "name_en": "Seaweed Soup",
        "ingredients": ["わかめ", "wakame", "ごま油", "sesame oil", "ねぎ", "green onion"],
        "url": "https://www.kurashiru.com/search?query=わかめスープ",
        "category": "soup",
        "time_minutes": 5,
    },
    {
        "name_ja": "ミネストローネ",
        "name_en": "Minestrone",
        "ingredients": ["トマト", "tomato", "玉ねぎ", "onion", "にんじん", "carrot",
                        "キャベツ", "cabbage", "ベーコン", "bacon"],
        "url": "https://www.kurashiru.com/search?query=ミネストローネ",
        "category": "soup",
        "time_minutes": 25,
    },
    {
        "name_ja": "クラムチャウダー",
        "name_en": "Clam Chowder",
        "ingredients": ["アサリ", "clams", "じゃがいも", "potato", "玉ねぎ", "onion",
                        "牛乳", "milk", "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=クラムチャウダー",
        "category": "soup",
        "time_minutes": 30,
    },
    {
        "name_ja": "キムチチゲ",
        "name_en": "Kimchi Jjigae (Kimchi Stew)",
        "ingredients": ["キムチ", "kimchi", "豚肉", "pork", "豆腐", "tofu",
                        "ねぎ", "green onion", "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=キムチチゲ",
        "category": "soup",
        "time_minutes": 20,
    },
    {
        "name_ja": "中華スープ",
        "name_en": "Chinese Egg Soup",
        "ingredients": ["卵", "egg", "わかめ", "wakame", "ねぎ", "green onion",
                        "ごま油", "sesame oil"],
        "url": "https://www.kurashiru.com/search?query=中華スープ",
        "category": "soup",
        "time_minutes": 5,
    },
    {
        "name_ja": "オニオンスープ",
        "name_en": "French Onion Soup",
        "ingredients": ["玉ねぎ", "onion", "バター", "butter", "チーズ", "cheese",
                        "パン", "bread"],
        "url": "https://www.kurashiru.com/search?query=オニオンスープ",
        "category": "soup",
        "time_minutes": 30,
    },
    {
        "name_ja": "なめこの味噌汁",
        "name_en": "Nameko Mushroom Miso Soup",
        "ingredients": ["なめこ", "nameko", "豆腐", "tofu", "味噌", "miso",
                        "ねぎ", "green onion"],
        "url": "https://www.kurashiru.com/search?query=なめこの味噌汁",
        "category": "soup",
        "time_minutes": 10,
    },
    {
        "name_ja": "野菜コンソメスープ",
        "name_en": "Vegetable Consomme Soup",
        "ingredients": ["キャベツ", "cabbage", "にんじん", "carrot", "玉ねぎ", "onion",
                        "ベーコン", "bacon"],
        "url": "https://www.kurashiru.com/search?query=野菜コンソメスープ",
        "category": "soup",
        "time_minutes": 15,
    },
    # === 丼 (Bowl dishes) ===
    {
        "name_ja": "親子丼",
        "name_en": "Oyakodon (Chicken & Egg Bowl)",
        "ingredients": ["鶏肉", "chicken", "卵", "egg", "玉ねぎ", "onion", "ご飯", "rice"],
        "url": "https://www.kurashiru.com/search?query=親子丼",
        "category": "bowl",
        "time_minutes": 15,
    },
    {
        "name_ja": "牛丼",
        "name_en": "Gyudon (Beef Bowl)",
        "ingredients": ["牛肉", "beef", "玉ねぎ", "onion", "ご飯", "rice",
                        "醤油", "soy sauce", "みりん", "mirin"],
        "url": "https://www.kurashiru.com/search?query=牛丼",
        "category": "bowl",
        "time_minutes": 15,
    },
    {
        "name_ja": "豚丼",
        "name_en": "Butadon (Pork Bowl)",
        "ingredients": ["豚肉", "pork", "玉ねぎ", "onion", "ご飯", "rice",
                        "醤油", "soy sauce", "しょうが", "ginger"],
        "url": "https://www.kurashiru.com/search?query=豚丼",
        "category": "bowl",
        "time_minutes": 15,
    },
    {
        "name_ja": "カツ丼",
        "name_en": "Katsudon (Pork Cutlet Bowl)",
        "ingredients": ["豚ロース", "pork loin", "卵", "egg", "玉ねぎ", "onion",
                        "ご飯", "rice", "パン粉", "breadcrumbs"],
        "url": "https://www.kurashiru.com/search?query=カツ丼",
        "category": "bowl",
        "time_minutes": 25,
    },
    {
        "name_ja": "天津飯",
        "name_en": "Tenshinhan (Crab Omelette Rice)",
        "ingredients": ["卵", "egg", "カニカマ", "crab stick", "ご飯", "rice",
                        "ねぎ", "green onion"],
        "url": "https://www.kurashiru.com/search?query=天津飯",
        "category": "bowl",
        "time_minutes": 15,
    },
    {
        "name_ja": "海鮮丼",
        "name_en": "Kaisendon (Seafood Bowl)",
        "ingredients": ["刺身", "sashimi", "ご飯", "rice", "わさび", "wasabi",
                        "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=海鮮丼",
        "category": "bowl",
        "time_minutes": 10,
    },
    {
        "name_ja": "中華丼",
        "name_en": "Chukadon (Chinese-style Bowl)",
        "ingredients": ["豚肉", "pork", "白菜", "napa cabbage", "にんじん", "carrot",
                        "エビ", "shrimp", "ご飯", "rice", "きのこ", "mushroom"],
        "url": "https://www.kurashiru.com/search?query=中華丼",
        "category": "bowl",
        "time_minutes": 20,
    },
    {
        "name_ja": "そぼろ丼",
        "name_en": "Soboro Don (Minced Meat Bowl)",
        "ingredients": ["ひき肉", "ground meat", "卵", "egg", "ご飯", "rice",
                        "しょうが", "ginger", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=そぼろ丼",
        "category": "bowl",
        "time_minutes": 15,
    },
    {
        "name_ja": "ネギトロ丼",
        "name_en": "Negitoro Don (Tuna Belly Bowl)",
        "ingredients": ["マグロ", "tuna", "ねぎ", "green onion", "ご飯", "rice"],
        "url": "https://www.kurashiru.com/search?query=ネギトロ丼",
        "category": "bowl",
        "time_minutes": 5,
    },
    {
        "name_ja": "しらす丼",
        "name_en": "Shirasu Don (Whitebait Bowl)",
        "ingredients": ["しらす", "whitebait", "ご飯", "rice", "卵", "egg",
                        "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=しらす丼",
        "category": "bowl",
        "time_minutes": 5,
    },
    {
        "name_ja": "鉄火丼",
        "name_en": "Tekka Don (Tuna Sashimi Bowl)",
        "ingredients": ["マグロ", "tuna", "ご飯", "rice", "わさび", "wasabi",
                        "醤油", "soy sauce", "海苔", "nori"],
        "url": "https://www.kurashiru.com/search?query=鉄火丼",
        "category": "bowl",
        "time_minutes": 5,
    },
    {
        "name_ja": "タコライス",
        "name_en": "Taco Rice",
        "ingredients": ["ひき肉", "ground meat", "レタス", "lettuce", "トマト", "tomato",
                        "チーズ", "cheese", "ご飯", "rice"],
        "url": "https://www.kurashiru.com/search?query=タコライス",
        "category": "bowl",
        "time_minutes": 15,
    },
    # === 麺 (Noodle dishes) ===
    {
        "name_ja": "ナポリタン",
        "name_en": "Napolitan Spaghetti",
        "ingredients": ["パスタ", "pasta", "ウインナー", "sausage", "ピーマン", "bell pepper",
                        "玉ねぎ", "onion", "ケチャップ", "ketchup"],
        "url": "https://www.kurashiru.com/search?query=ナポリタン",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "カルボナーラ",
        "name_en": "Carbonara",
        "ingredients": ["パスタ", "pasta", "ベーコン", "bacon", "卵", "egg",
                        "チーズ", "cheese", "牛乳", "milk"],
        "url": "https://www.kurashiru.com/search?query=カルボナーラ",
        "category": "noodle",
        "time_minutes": 20,
    },
    {
        "name_ja": "和風パスタ",
        "name_en": "Japanese-style Pasta",
        "ingredients": ["パスタ", "pasta", "きのこ", "mushroom", "ベーコン", "bacon",
                        "醤油", "soy sauce", "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=和風パスタ",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "ペペロンチーノ",
        "name_en": "Peperoncino",
        "ingredients": ["パスタ", "pasta", "にんにく", "garlic", "唐辛子", "chili",
                        "オリーブオイル", "olive oil"],
        "url": "https://www.kurashiru.com/search?query=ペペロンチーノ",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "きつねうどん",
        "name_en": "Kitsune Udon",
        "ingredients": ["うどん", "udon", "油揚げ", "fried tofu", "ねぎ", "green onion",
                        "だし", "dashi"],
        "url": "https://www.kurashiru.com/search?query=きつねうどん",
        "category": "noodle",
        "time_minutes": 10,
    },
    {
        "name_ja": "カレーうどん",
        "name_en": "Curry Udon",
        "ingredients": ["うどん", "udon", "豚肉", "pork", "玉ねぎ", "onion",
                        "カレールー", "curry roux", "ねぎ", "green onion"],
        "url": "https://www.kurashiru.com/search?query=カレーうどん",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "担々麺",
        "name_en": "Tantan Noodles",
        "ingredients": ["中華麺", "noodles", "ひき肉", "ground meat", "ねぎ", "green onion",
                        "ごま", "sesame", "豆板醤", "doubanjiang"],
        "url": "https://www.kurashiru.com/search?query=担々麺",
        "category": "noodle",
        "time_minutes": 20,
    },
    {
        "name_ja": "冷やし中華",
        "name_en": "Hiyashi Chuka (Cold Noodles)",
        "ingredients": ["中華麺", "noodles", "卵", "egg", "きゅうり", "cucumber",
                        "ハム", "ham", "トマト", "tomato"],
        "url": "https://www.kurashiru.com/search?query=冷やし中華",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "焼うどん",
        "name_en": "Yaki Udon (Stir-fried Udon)",
        "ingredients": ["うどん", "udon", "豚肉", "pork", "キャベツ", "cabbage",
                        "にんじん", "carrot", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=焼うどん",
        "category": "noodle",
        "time_minutes": 10,
    },
    {
        "name_ja": "鍋焼きうどん",
        "name_en": "Nabeyaki Udon (Hot Pot Udon)",
        "ingredients": ["うどん", "udon", "鶏肉", "chicken", "卵", "egg",
                        "ねぎ", "green onion", "きのこ", "mushroom"],
        "url": "https://www.kurashiru.com/search?query=鍋焼きうどん",
        "category": "noodle",
        "time_minutes": 20,
    },
    {
        "name_ja": "ソーメンチャンプルー",
        "name_en": "Somen Champloo",
        "ingredients": ["そうめん", "somen", "ツナ缶", "canned tuna", "にんじん", "carrot",
                        "ニラ", "chives", "卵", "egg"],
        "url": "https://www.kurashiru.com/search?query=ソーメンチャンプルー",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "たらこパスタ",
        "name_en": "Tarako Pasta (Cod Roe Pasta)",
        "ingredients": ["パスタ", "pasta", "たらこ", "cod roe", "バター", "butter",
                        "海苔", "nori"],
        "url": "https://www.kurashiru.com/search?query=たらこパスタ",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "明太子クリームパスタ",
        "name_en": "Mentaiko Cream Pasta",
        "ingredients": ["パスタ", "pasta", "明太子", "mentaiko", "牛乳", "milk",
                        "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=明太子クリームパスタ",
        "category": "noodle",
        "time_minutes": 15,
    },
    {
        "name_ja": "ミートソースパスタ",
        "name_en": "Meat Sauce Pasta",
        "ingredients": ["パスタ", "pasta", "ひき肉", "ground meat", "玉ねぎ", "onion",
                        "トマト", "tomato", "にんじん", "carrot"],
        "url": "https://www.kurashiru.com/search?query=ミートソース",
        "category": "noodle",
        "time_minutes": 30,
    },
    # === Additional main dishes to reach 100+ ===
    {
        "name_ja": "肉巻きおにぎり",
        "name_en": "Meat-wrapped Rice Ball",
        "ingredients": ["豚肉", "pork", "ご飯", "rice", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=肉巻きおにぎり",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "チーズタッカルビ",
        "name_en": "Cheese Dakgalbi",
        "ingredients": ["鶏肉", "chicken", "チーズ", "cheese", "キャベツ", "cabbage",
                        "コチュジャン", "gochujang", "玉ねぎ", "onion"],
        "url": "https://www.kurashiru.com/search?query=チーズタッカルビ",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "鮭のちゃんちゃん焼き",
        "name_en": "Salmon Chanchan Yaki",
        "ingredients": ["鮭", "salmon", "キャベツ", "cabbage", "玉ねぎ", "onion",
                        "味噌", "miso", "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=鮭のちゃんちゃん焼き",
        "category": "main",
        "time_minutes": 20,
    },
    {
        "name_ja": "豆腐チャンプルー",
        "name_en": "Tofu Champloo",
        "ingredients": ["豆腐", "tofu", "豚肉", "pork", "もやし", "bean sprouts",
                        "ニラ", "chives", "卵", "egg"],
        "url": "https://www.kurashiru.com/search?query=豆腐チャンプルー",
        "category": "main",
        "time_minutes": 10,
    },
    {
        "name_ja": "鶏のさっぱり煮",
        "name_en": "Chicken Vinegar Simmer",
        "ingredients": ["鶏肉", "chicken", "酢", "vinegar", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=鶏のさっぱり煮",
        "category": "main",
        "time_minutes": 25,
    },
    {
        "name_ja": "ツナマヨおにぎり",
        "name_en": "Tuna Mayo Onigiri",
        "ingredients": ["ツナ缶", "canned tuna", "マヨネーズ", "mayonnaise", "ご飯", "rice"],
        "url": "https://www.kurashiru.com/search?query=ツナマヨおにぎり",
        "category": "main",
        "time_minutes": 5,
    },
    {
        "name_ja": "エビマヨ",
        "name_en": "Shrimp with Mayo Sauce",
        "ingredients": ["エビ", "shrimp", "マヨネーズ", "mayonnaise", "片栗粉", "potato starch"],
        "url": "https://www.kurashiru.com/search?query=エビマヨ",
        "category": "main",
        "time_minutes": 15,
    },
    {
        "name_ja": "焼き鮭",
        "name_en": "Grilled Salmon",
        "ingredients": ["鮭", "salmon", "塩", "salt"],
        "url": "https://www.kurashiru.com/search?query=焼き鮭",
        "category": "main",
        "time_minutes": 10,
    },
    {
        "name_ja": "目玉焼き",
        "name_en": "Sunny-side Up Egg",
        "ingredients": ["卵", "egg"],
        "url": "https://www.kurashiru.com/search?query=目玉焼き",
        "category": "side",
        "time_minutes": 3,
    },
    {
        "name_ja": "ウインナー炒め",
        "name_en": "Pan-fried Sausage",
        "ingredients": ["ウインナー", "sausage", "ケチャップ", "ketchup"],
        "url": "https://www.kurashiru.com/search?query=ウインナー炒め",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "ベーコンエッグ",
        "name_en": "Bacon and Eggs",
        "ingredients": ["ベーコン", "bacon", "卵", "egg"],
        "url": "https://www.kurashiru.com/search?query=ベーコンエッグ",
        "category": "main",
        "time_minutes": 5,
    },
    {
        "name_ja": "トースト",
        "name_en": "Toast",
        "ingredients": ["パン", "bread", "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=トースト",
        "category": "main",
        "time_minutes": 3,
    },
    {
        "name_ja": "フレンチトースト",
        "name_en": "French Toast",
        "ingredients": ["パン", "bread", "卵", "egg", "牛乳", "milk", "砂糖", "sugar"],
        "url": "https://www.kurashiru.com/search?query=フレンチトースト",
        "category": "main",
        "time_minutes": 10,
    },
    {
        "name_ja": "おにぎり",
        "name_en": "Onigiri (Rice Ball)",
        "ingredients": ["ご飯", "rice", "海苔", "nori", "塩", "salt"],
        "url": "https://www.kurashiru.com/search?query=おにぎり",
        "category": "main",
        "time_minutes": 5,
    },
    {
        "name_ja": "卵かけご飯",
        "name_en": "Tamago Kake Gohan (Egg on Rice)",
        "ingredients": ["卵", "egg", "ご飯", "rice", "醤油", "soy sauce"],
        "url": "https://www.kurashiru.com/search?query=卵かけご飯",
        "category": "bowl",
        "time_minutes": 2,
    },
    {
        "name_ja": "納豆ご飯",
        "name_en": "Natto Rice",
        "ingredients": ["納豆", "natto", "ご飯", "rice", "ねぎ", "green onion"],
        "url": "https://www.kurashiru.com/search?query=納豆ご飯",
        "category": "bowl",
        "time_minutes": 2,
    },
    {
        "name_ja": "お茶漬け",
        "name_en": "Ochazuke (Rice with Tea)",
        "ingredients": ["ご飯", "rice", "鮭", "salmon", "海苔", "nori"],
        "url": "https://www.kurashiru.com/search?query=お茶漬け",
        "category": "bowl",
        "time_minutes": 3,
    },
    {
        "name_ja": "雑炊",
        "name_en": "Zosui (Rice Porridge)",
        "ingredients": ["ご飯", "rice", "卵", "egg", "ねぎ", "green onion", "だし", "dashi"],
        "url": "https://www.kurashiru.com/search?query=雑炊",
        "category": "bowl",
        "time_minutes": 10,
    },
    {
        "name_ja": "豆腐の味噌汁",
        "name_en": "Tofu Miso Soup",
        "ingredients": ["豆腐", "tofu", "味噌", "miso", "ねぎ", "green onion"],
        "url": "https://www.kurashiru.com/search?query=豆腐の味噌汁",
        "category": "soup",
        "time_minutes": 5,
    },
    {
        "name_ja": "スクランブルエッグ",
        "name_en": "Scrambled Eggs",
        "ingredients": ["卵", "egg", "牛乳", "milk", "バター", "butter"],
        "url": "https://www.kurashiru.com/search?query=スクランブルエッグ",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "ツナサラダ",
        "name_en": "Tuna Salad",
        "ingredients": ["ツナ缶", "canned tuna", "レタス", "lettuce", "トマト", "tomato",
                        "きゅうり", "cucumber"],
        "url": "https://www.kurashiru.com/search?query=ツナサラダ",
        "category": "side",
        "time_minutes": 5,
    },
    {
        "name_ja": "しらすトースト",
        "name_en": "Whitebait Toast",
        "ingredients": ["しらす", "whitebait", "パン", "bread", "チーズ", "cheese"],
        "url": "https://www.kurashiru.com/search?query=しらすトースト",
        "category": "main",
        "time_minutes": 5,
    },
    {
        "name_ja": "豚しゃぶサラダ",
        "name_en": "Pork Shabu Salad",
        "ingredients": ["豚肉", "pork", "レタス", "lettuce", "トマト", "tomato",
                        "きゅうり", "cucumber"],
        "url": "https://www.kurashiru.com/search?query=豚しゃぶサラダ",
        "category": "main",
        "time_minutes": 15,
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


def get_time_of_day() -> str:
    """Return time of day: morning, lunch, or dinner."""
    hour = datetime.now().hour
    if 5 <= hour < 10:
        return "morning"
    elif 10 <= hour < 15:
        return "lunch"
    else:
        return "dinner"


def get_season() -> str:
    """Return current season."""
    month = datetime.now().month
    if month in (3, 4, 5):
        return "spring"
    elif month in (6, 7, 8):
        return "summer"
    elif month in (9, 10, 11):
        return "autumn"
    else:
        return "winter"


def get_daily_recommendations() -> list[dict]:
    """Get 3 recommended recipes based on time of day and season."""
    time_of_day = get_time_of_day()
    season = get_season()

    # Use today's date as seed for consistent daily picks
    today_seed = datetime.now().strftime("%Y%m%d")
    rng = random.Random(today_seed + time_of_day)

    if time_of_day == "morning":
        # Morning: quick, light recipes (<=15 min)
        candidates = [r for r in RECIPE_DB if r["time_minutes"] <= 15]
    elif time_of_day == "lunch":
        # Lunch: bowls and noodles preferred
        preferred = [r for r in RECIPE_DB if r["category"] in ("bowl", "noodle")]
        others = [r for r in RECIPE_DB if r["category"] not in ("bowl", "noodle")]
        candidates = preferred + others[:10]
    else:
        # Dinner: main dishes, soups
        preferred = [r for r in RECIPE_DB if r["category"] in ("main", "soup")]
        candidates = preferred

    # Season adjustments: prefer warm dishes in winter/autumn, lighter in summer
    if season in ("winter", "autumn"):
        warm = [r for r in candidates if r["category"] in ("soup", "main", "noodle") and r["time_minutes"] >= 15]
        if len(warm) >= 3:
            candidates = warm
    elif season == "summer":
        light = [r for r in candidates if r["time_minutes"] <= 20]
        if len(light) >= 3:
            candidates = light

    if len(candidates) < 3:
        candidates = RECIPE_DB.copy()

    rng.shuffle(candidates)
    return candidates[:3]


def get_tired_mode_recipes() -> list[dict]:
    """Get recipes with <=15 minutes and <=3 ingredients (unique, not counting duplicates)."""
    results = []
    for recipe in RECIPE_DB:
        if recipe["time_minutes"] <= 15:
            # Count unique ingredient concepts (ja/en pairs count as 1)
            ings = recipe["ingredients"]
            unique_count = len(ings) // 2  # Each ingredient has ja + en pair
            if unique_count <= 3:
                results.append(recipe)
    return results


def generate_weekly_menu() -> dict:
    """Generate a weekly menu rotation.
    Mon=meat, Tue=fish, Wed=bowl, Thu=noodle, Fri=meat, Sat=free, Sun=free
    """
    today_seed = datetime.now().strftime("%Y%W")  # Changes weekly
    rng = random.Random(today_seed)

    meat_mains = [r for r in RECIPE_DB if r["category"] == "main" and
                  any(k in " ".join(r["ingredients"]) for k in ["鶏", "豚", "牛", "肉", "chicken", "pork", "beef"])]
    fish_mains = [r for r in RECIPE_DB if r["category"] == "main" and
                  any(k in " ".join(r["ingredients"]) for k in ["鮭", "サバ", "エビ", "魚", "salmon", "mackerel", "shrimp", "cod", "タラ", "イカ", "squid", "アサリ", "clams"])]
    bowls = [r for r in RECIPE_DB if r["category"] == "bowl"]
    noodles = [r for r in RECIPE_DB if r["category"] == "noodle"]
    sides = [r for r in RECIPE_DB if r["category"] == "side"]
    soups = [r for r in RECIPE_DB if r["category"] == "soup"]
    all_mains = [r for r in RECIPE_DB if r["category"] in ("main", "bowl", "noodle")]

    def pick(pool, exclude=None):
        if exclude:
            pool = [r for r in pool if r["name_ja"] not in exclude]
        if not pool:
            pool = all_mains
        return rng.choice(pool)

    def pick_side():
        return rng.choice(sides) if sides else None

    def pick_soup():
        return rng.choice(soups) if soups else None

    used = set()
    weekly = {}
    days = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    day_pools = [meat_mains, fish_mains, bowls, noodles, meat_mains, all_mains, all_mains]

    for day, pool in zip(days, day_pools):
        main = pick(pool, exclude=used)
        used.add(main["name_ja"])
        side = pick_side()
        soup = pick_soup()
        weekly[day] = {"main": main, "side": side, "soup": soup}

    return weekly


# --- Mode selection ---
mode = st.radio(
    t("mode_label"),
    [t("mode_search"), t("mode_weekly"), t("mode_url")],
    horizontal=True,
)

if mode == t("mode_search"):
    # === Today's Recommendations (shown before any input) ===
    st.subheader(t("daily_recommend_title"))
    time_label = t(f"time_{get_time_of_day()}")
    st.caption(t("daily_recommend_subtitle").format(time=time_label))

    recs = get_daily_recommendations()
    rec_cols = st.columns(3)
    for i, recipe in enumerate(recs):
        with rec_cols[i]:
            lang = get_lang()
            name = recipe["name_ja"] if lang == "ja" else recipe["name_en"]
            cat_key = f"cat_label_{recipe['category']}"
            cat_label = t(cat_key)
            st.markdown(f"**{name}**")
            st.caption(f"{cat_label} / {recipe['time_minutes']}{t('minutes')}")
            st.markdown(f"[{t('search_recipe_link')}]({recipe['url']})")

    st.markdown("---")

    # === Tired Mode ===
    tired_mode = st.toggle(t("tired_mode_label"), key="tired_mode")

    if tired_mode:
        st.markdown(f"### {t('tired_mode_title')}")
        st.caption(t("tired_mode_help"))
        tired_recipes = get_tired_mode_recipes()
        if tired_recipes:
            for recipe in tired_recipes:
                lang = get_lang()
                name = recipe["name_ja"] if lang == "ja" else recipe["name_en"]
                cat_label = t(f"cat_label_{recipe['category']}")
                st.markdown(f"- **{name}** ({recipe['time_minutes']}{t('minutes')}, {cat_label}) [{t('search_recipe_link')}]({recipe['url']})")
        else:
            st.info(t("tired_no_recipes"))
        st.markdown("---")

    # --- Ingredient search mode ---
    st.subheader(t("input_ingredients_title"))
    st.caption(t("input_ingredients_help"))

    # === Preset Bundles ===
    st.markdown(f"**{t('bundle_title')}**")
    bundle_cols = st.columns(len(INGREDIENT_BUNDLES))
    for i, (bundle_key, bundle_data) in enumerate(INGREDIENT_BUNDLES.items()):
        with bundle_cols[i]:
            if st.button(t(f"bundle_{bundle_key}"), key=f"bundle_{bundle_key}"):
                lang = get_lang()
                items = bundle_data["items_ja"] if lang == "ja" else bundle_data["items_en"]
                st.session_state["bundle_selected"] = items

    # Apply bundle selection to session state
    bundle_items = st.session_state.get("bundle_selected", [])
    if bundle_items:
        st.info(t("bundle_applied").format(items=", ".join(bundle_items)))

    selected_ingredients = list(bundle_items)

    for cat_key, cat_data in INGREDIENT_PRESETS.items():
        cat_name = t(f"cat_{cat_key}")
        with st.expander(f"{cat_data['emoji']} {cat_name}"):
            items = cat_data["items_ja"] if get_lang() == "ja" else cat_data["items_en"]
            for item in items:
                if st.checkbox(item, key=f"ing_{cat_key}_{item}"):
                    if item not in selected_ingredients:
                        selected_ingredients.append(item)

    # 自由入力
    custom = st.text_input(t("custom_ingredients"), placeholder=t("custom_placeholder"))
    if custom:
        selected_ingredients.extend([x.strip() for x in custom.replace("\u3001", ",").split(",") if x.strip()])

    if selected_ingredients:
        st.caption(t("selected_count").format(count=len(selected_ingredients)) + ": " + ", ".join(selected_ingredients))

    if st.button(t("search_button"), type="primary"):
        # Clear bundle after search
        if "bundle_selected" in st.session_state:
            del st.session_state["bundle_selected"]

        ingredients = selected_ingredients

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
                    cat_label = t(f"cat_label_{recipe['category']}")
                    time_info = f"{recipe['time_minutes']}{t('minutes')}"

                    score_pct = int(res["score"] * 100)
                    with st.expander(f"{name}  ({t('match_rate')}: {score_pct}% | {cat_label} | {time_info})", expanded=(i < 3)):
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

elif mode == t("mode_weekly"):
    # === Weekly Menu ===
    st.subheader(t("weekly_title"))
    st.caption(t("weekly_help"))

    weekly = generate_weekly_menu()

    day_keys = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    day_themes = {
        "mon": t("theme_meat"),
        "tue": t("theme_fish"),
        "wed": t("theme_bowl"),
        "thu": t("theme_noodle"),
        "fri": t("theme_meat"),
        "sat": t("theme_free"),
        "sun": t("theme_free"),
    }

    for day_key in day_keys:
        day_data = weekly[day_key]
        day_name = t(f"day_{day_key}")
        theme = day_themes[day_key]
        lang = get_lang()

        main_name = day_data["main"]["name_ja"] if lang == "ja" else day_data["main"]["name_en"]
        main_time = day_data["main"]["time_minutes"]

        line = f"**{day_name}** ({theme}): {main_name} ({main_time}{t('minutes')})"

        if day_data["side"]:
            side_name = day_data["side"]["name_ja"] if lang == "ja" else day_data["side"]["name_en"]
            line += f" + {side_name}"
        if day_data["soup"]:
            soup_name = day_data["soup"]["name_ja"] if lang == "ja" else day_data["soup"]["name_en"]
            line += f" + {soup_name}"

        st.markdown(line)

    if st.button(t("weekly_refresh"), type="secondary"):
        st.cache_data.clear()
        st.rerun()

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
render_footer(libraries=["recipe-scrapers", "ingredient-parser-nlp"], repo_name="kf-meal-rescue")
