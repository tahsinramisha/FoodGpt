import difflib
import os
import re

import pandas as pd
import streamlit as st

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_DATASET_PATHS = [
    os.path.join(BASE_DIR, "data", "bd_food_nutrition_dataset.csv"),
    os.path.join(BASE_DIR, "bd_food_nutrition_dataset.csv"),
]


def normalize_column_name(name):
    cleaned = str(name).strip().lower()
    cleaned = cleaned.replace(" ", "_").replace("-", "_").replace("(", "").replace(")", "")
    cleaned = cleaned.replace("/", "_")
    return cleaned


def to_bool(value):
    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    if isinstance(value, (int, float)):
        return bool(value)
    text = str(value).strip().lower()
    return text in {"yes", "true", "y", "1", "t"}


def load_food_dataset(uploaded_file=None):
    if uploaded_file is not None:
        file_name = str(uploaded_file.name).lower()
        try:
            if file_name.endswith(".csv"):
                return pd.read_csv(uploaded_file)
            return pd.read_excel(uploaded_file)
        except Exception as error:
            st.error(f"Could not read the uploaded dataset file: {error}")
            return pd.DataFrame()

    for file_path in DEFAULT_DATASET_PATHS:
        if os.path.exists(file_path):
            try:
                if str(file_path).lower().endswith(".csv"):
                    return pd.read_csv(file_path)
                return pd.read_excel(file_path)
            except Exception:
                continue

    return pd.DataFrame()


# ---------------------------------------------------------------------------
# Allergen and dietary-filter rules
# ---------------------------------------------------------------------------

ALLERGEN_RULES = {
    "Dairy": {
        "sure": [
            "milk", "cheese", "butter", "ghee", "cream", "creamy", "yogurt", "yoghurt",
            "curd", "doi", "paneer", "khoa", "mawa", "malai", "chena", "kulfi", "lassi",
            "borhani", "payesh", "firni", "kheer", "custard", "ice cream", "rasmalai",
            "rasgulla", "roshogolla", "rosogolla", "sandesh", "chomchom", "cham cham",
            "kalojam", "condensed", "latte", "cappuccino", "milkshake", "cheesecake",
        ],
        "maybe": [
            "korma", "rezala", "shahi", "mughlai", "halwa", "cake", "pastry", "chocolate",
            "biscuit", "mousse", "pudding", "tea", "coffee", "mishti", "misti", "naan",
        ],
        "categories": {
            "Sweet/Dessert": "may contain",
            "Bakery": "may contain",
            "Fast Food/Western": "may contain",
        },
    },
    "Egg": {
        "sure": ["egg", "dim", "dimer", "omelette", "omelet", "mayonnaise", "mayo", "meringue"],
        "maybe": [
            "cake", "pastry", "pudding", "custard", "noodle", "noodles", "pasta", "cutlet",
            "chop", "roll", "patties", "kebab", "meatball", "pancake", "waffle",
            "french toast", "tiramisu", "biscuit", "mousse", "batter", "fried rice",
            "chowmein", "chow mein", "pitha", "muffin", "donut", "doughnut", "bun",
        ],
        "categories": {"Bakery": "may contain"},
    },
    "Fish": {
        "sure": [
            "fish", "mach", "machh", "macher", "rui", "katla", "katol", "ilish", "hilsa",
            "pangas", "pangash", "koi", "shing", "magur", "tilapia", "pabda", "chitol",
            "boal", "tengra", "bata", "mola", "chapila", "puti", "kholisha", "rita",
            "bacha", "vetki", "bhetki", "carp", "mrigel", "tuna", "salmon", "mackerel",
            "sardine", "pomfret", "shutki", "anchovy", "surimi", "air",
        ],
        "maybe": ["worcestershire", "oyster sauce"],
        "categories": {"Fish": "contains"},
    },
    "Shellfish": {
        "sure": [
            "prawn", "shrimp", "chingri", "chingdi", "crab", "kakra", "kankra", "lobster",
            "squid", "octopus", "oyster", "clam", "mussel", "scallop",
        ],
        "maybe": [],
        "categories": {},
    },
    "Gluten": {
        "sure": [
            "flour", "atta", "maida", "suji", "sooji", "semolina", "wheat", "barley", "rye",
            "bread", "pasta", "noodle", "noodles", "chowmein", "chow mein", "roti", "ruti",
            "paratha", "porota", "luchi", "naan", "chapati", "biscuit", "cake", "pastry",
            "bun", "burger", "pizza", "sandwich", "toast", "samosa", "singara", "puri",
            "patties", "spring roll", "dumpling", "momo", "macaroni", "lasagna",
            "spaghetti", "croissant", "donut", "doughnut", "cracker", "cereal", "malt",
            "nimki", "muffin", "waffle", "pancake",
        ],
        "maybe": [
            "soy sauce", "sauce", "gravy", "batter", "pakora", "chop", "cutlet", "kebab",
            "halwa", "oats", "chanachur", "jhalmuri", "roll",
        ],
        "categories": {
            "Bakery": "contains",
            "Bread": "contains",
            "Fast Food/Western": "may contain",
        },
    },
    "Peanut": {
        "sure": ["peanut", "peanuts", "groundnut", "chinabadam", "china badam"],
        "maybe": ["badam", "nut", "nuts", "chanachur", "jhalmuri", "satay", "praline"],
        "categories": {},
    },
    "Tree nuts": {
        "sure": [
            "almond", "cashew", "kaju", "pista", "pistachio", "walnut", "akhrot",
            "hazelnut", "pecan", "coconut", "narikel", "nariyal", "nutella",
        ],
        "maybe": ["badam", "nut", "nuts", "halwa", "payesh", "biryani", "korma", "kheer", "firni"],
        "categories": {"Sweet/Dessert": "may contain"},
    },
    "Soy": {
        "sure": ["soy", "soya", "soybean", "tofu", "edamame", "miso", "tempeh"],
        "maybe": [
            "sauce", "chowmein", "chow mein", "manchurian", "noodle", "noodles", "burger",
            "sausage", "margarine", "mayonnaise", "processed",
        ],
        "categories": {"Fast Food/Western": "may contain"},
    },
    "Sesame": {
        "sure": ["sesame", "til", "tahini", "tahina", "gingelly"],
        "maybe": ["burger", "bun", "hummus", "chanachur", "naru", "halwa"],
        "categories": {},
    },
    "Mustard": {
        "sure": ["mustard", "shorshe", "sorshe", "shorisha", "sarisha", "kasundi"],
        "maybe": ["pickle", "achar", "bhorta"],
        "categories": {},
    },
}

DIET_FILTERS = {
    "Vegetarian": "Only foods marked vegetarian in the dataset.",
    "Vegan": "Only foods marked vegan in the dataset.",
    "Pescatarian": "Vegetarian foods plus fish and seafood.",
    "Eggless": "Removes foods that contain egg.",
    "Dairy-free": "Removes foods that contain milk products.",
    "Gluten-free": "Only foods marked gluten free in the dataset.",
    "Nut-free": "Removes peanut and tree nut foods.",
    "No beef": "Removes beef dishes.",
    "No pork (halal-friendly)": "Removes pork, bacon, ham and alcohol.",
    "No red meat": "Removes beef, pork, mutton, goat, lamb and organ meat.",
    "Low sodium": "Keeps foods with 400 mg sodium or less per listed serving.",
    "Low sugar": "Keeps foods with 8 g sugar or less per listed serving.",
}

BEEF_WORDS = ["beef", "gorur"]
PORK_WORDS = ["pork", "bacon", "ham", "pepperoni", "salami", "sausage", "lard", "prosciutto"]
ALCOHOL_WORDS = ["wine", "beer", "rum", "vodka", "whisky", "whiskey", "brandy", "liquor", "alcohol", "champagne"]
RED_MEAT_WORDS = BEEF_WORDS + PORK_WORDS + ["mutton", "goat", "lamb", "liver", "kidney", "brain", "trotter"]

LOW_SODIUM_LIMIT = 400.0
LOW_SUGAR_LIMIT = 8.0


def compile_word_pattern(words):
    if not words:
        return None
    ordered = sorted({str(word).lower() for word in words}, key=len, reverse=True)
    return re.compile(r"(?<![a-z])(?:" + "|".join(re.escape(word) for word in ordered) + r")(?![a-z])")


ALLERGEN_PATTERNS = {
    allergen: {
        "sure": compile_word_pattern(rule.get("sure", [])),
        "maybe": compile_word_pattern(rule.get("maybe", [])),
        "categories": rule.get("categories", {}),
    }
    for allergen, rule in ALLERGEN_RULES.items()
}

BEEF_PATTERN = compile_word_pattern(BEEF_WORDS)
PORK_PATTERN = compile_word_pattern(PORK_WORDS + ALCOHOL_WORDS)
RED_MEAT_PATTERN = compile_word_pattern(RED_MEAT_WORDS)


def detect_allergens(name, ingredients, tags, category, gluten_free_flag, vegetarian_flag, vegan_flag):
    """Estimate which allergens a food carries and how confident that guess is."""
    blob = " ".join([str(name), str(ingredients), str(tags)]).lower()
    category_text = str(category).strip()
    found = {}

    for allergen, rule in ALLERGEN_PATTERNS.items():
        level = None
        if rule["sure"] is not None and rule["sure"].search(blob):
            level = "contains"
        elif rule["maybe"] is not None and rule["maybe"].search(blob):
            level = "may contain"

        hint = rule["categories"].get(category_text)
        if hint == "contains":
            level = "contains"
        elif hint and level is None:
            level = hint

        if level:
            found[allergen] = level

    if not gluten_free_flag:
        found["Gluten"] = "contains"
    elif found.get("Gluten") == "may contain":
        found.pop("Gluten", None)

    if vegan_flag:
        for allergen in ["Dairy", "Egg", "Fish", "Shellfish"]:
            if found.get(allergen) == "may contain":
                found.pop(allergen, None)
    elif vegetarian_flag:
        for allergen in ["Fish", "Shellfish"]:
            if found.get(allergen) == "may contain":
                found.pop(allergen, None)

    return found


def allergen_summary(allergens):
    if not allergens:
        return "No common allergens detected."
    definite = sorted(name for name, level in allergens.items() if level == "contains")
    possible = sorted(name for name, level in allergens.items() if level != "contains")
    parts = []
    if definite:
        parts.append("Contains " + ", ".join(definite))
    if possible:
        parts.append("May contain " + ", ".join(possible))
    return " · ".join(parts)


def diet_violations(row, diets, strict=False):
    """Reasons why a food does not fit the selected dietary preferences."""
    problems = []
    allergens = row.get("allergens") or {}
    blob = str(row.get("search_text", "")).lower()

    def carries(allergen):
        level = allergens.get(allergen)
        if level == "contains":
            return True
        return bool(level) and strict

    for diet in diets:
        if diet == "Vegetarian" and not bool(row.get("vegetarian")):
            problems.append("not vegetarian")
        elif diet == "Vegan" and not bool(row.get("vegan")):
            problems.append("not vegan")
        elif diet == "Pescatarian":
            seafood = allergens.get("Fish") == "contains" or allergens.get("Shellfish") == "contains"
            if not bool(row.get("vegetarian")) and not seafood:
                problems.append("not pescatarian")
        elif diet == "Eggless" and carries("Egg"):
            problems.append("has egg")
        elif diet == "Dairy-free" and carries("Dairy"):
            problems.append("has dairy")
        elif diet == "Gluten-free" and not bool(row.get("gluten_free")):
            problems.append("not gluten free")
        elif diet == "Nut-free" and (carries("Peanut") or carries("Tree nuts")):
            problems.append("has nuts")
        elif diet == "No beef" and BEEF_PATTERN.search(blob):
            problems.append("has beef")
        elif diet == "No pork (halal-friendly)" and PORK_PATTERN.search(blob):
            problems.append("has pork or alcohol")
        elif diet == "No red meat" and RED_MEAT_PATTERN.search(blob):
            problems.append("has red meat")
        elif diet == "Low sodium" and float(row.get("sodium", 0) or 0) > LOW_SODIUM_LIMIT:
            problems.append(f"sodium above {LOW_SODIUM_LIMIT:.0f} mg")
        elif diet == "Low sugar" and float(row.get("sugar", 0) or 0) > LOW_SUGAR_LIMIT:
            problems.append(f"sugar above {LOW_SUGAR_LIMIT:.0f} g")

    return problems


def food_filter_report(row, diets, avoid_allergens, avoid_words, strict=False):
    """Return (fits_the_filters, list_of_reasons_it_does_not)."""
    reasons = []
    allergens = row.get("allergens") or {}

    for allergen in avoid_allergens:
        level = allergens.get(allergen)
        if level == "contains":
            reasons.append(f"contains {allergen.lower()}")
        elif level and strict:
            reasons.append(f"may contain {allergen.lower()}")

    reasons.extend(diet_violations(row, diets, strict))

    blob = str(row.get("search_text", "")).lower()
    for word in avoid_words:
        if word and word in blob:
            reasons.append(f"has {word}")

    unique_reasons = list(dict.fromkeys(reasons))
    return (not unique_reasons), unique_reasons


def apply_food_filters(df, diets, avoid_allergens, avoid_words, strict=False):
    if df.empty:
        return df.copy()
    if not diets and not avoid_allergens and not avoid_words:
        return df.copy()
    keep = df.apply(
        lambda row: food_filter_report(row, diets, avoid_allergens, avoid_words, strict)[0],
        axis=1,
    )
    return df[keep].copy()


# ---------------------------------------------------------------------------
# Cleaning and lookup
# ---------------------------------------------------------------------------


def clean_food_dataset(df):
    if df.empty:
        return df

    cleaned = df.copy()
    cleaned.columns = [normalize_column_name(column) for column in cleaned.columns]

    name_candidates = ["food_name", "food", "name", "dish", "item", "fooditem", "meal"]
    calories_candidates = ["calories", "calories_kcal", "calorie", "energy_kcal", "kcal", "energy"]
    protein_candidates = ["protein", "protein_g", "protein_grams", "protein_gm"]
    carbs_candidates = ["carbs", "carbohydrates", "carb", "carbohydrate", "carbs_g", "carbohydrates_g"]
    fat_candidates = ["fat", "fat_g", "total_fat", "fats", "fat_grams"]
    fiber_candidates = ["fiber", "fiber_g", "dietary_fiber"]
    sugar_candidates = ["sugar", "sugar_g", "total_sugar"]
    sodium_candidates = ["sodium", "sodium_mg", "salt_mg"]
    ingredient_candidates = ["ingredients", "ingredient", "ingredients_list", "components", "main_ingredients"]
    recipe_candidates = ["recipe", "instructions", "cooking_instructions", "method"]

    name_column = next((col for col in name_candidates if col in cleaned.columns), None)
    calories_column = next((col for col in calories_candidates if col in cleaned.columns), None)
    protein_column = next((col for col in protein_candidates if col in cleaned.columns), None)
    carbs_column = next((col for col in carbs_candidates if col in cleaned.columns), None)
    fat_column = next((col for col in fat_candidates if col in cleaned.columns), None)
    fiber_column = next((col for col in fiber_candidates if col in cleaned.columns), None)
    sugar_column = next((col for col in sugar_candidates if col in cleaned.columns), None)
    sodium_column = next((col for col in sodium_candidates if col in cleaned.columns), None)
    ingredient_column = next((col for col in ingredient_candidates if col in cleaned.columns), None)
    recipe_column = next((col for col in recipe_candidates if col in cleaned.columns), None)

    if not name_column:
        return pd.DataFrame()

    cleaned["food_name"] = cleaned[name_column].fillna("Unknown Food").astype(str).str.strip()
    cleaned["calories"] = pd.to_numeric(cleaned[calories_column], errors="coerce").fillna(0) if calories_column else 0
    cleaned["protein"] = pd.to_numeric(cleaned[protein_column], errors="coerce").fillna(0) if protein_column else 0
    cleaned["carbs"] = pd.to_numeric(cleaned[carbs_column], errors="coerce").fillna(0) if carbs_column else 0
    cleaned["fat"] = pd.to_numeric(cleaned[fat_column], errors="coerce").fillna(0) if fat_column else 0
    cleaned["fiber"] = pd.to_numeric(cleaned[fiber_column], errors="coerce").fillna(0) if fiber_column else 0
    cleaned["sugar"] = pd.to_numeric(cleaned[sugar_column], errors="coerce").fillna(0) if sugar_column else 0
    cleaned["sodium"] = pd.to_numeric(cleaned[sodium_column], errors="coerce").fillna(0) if sodium_column else 0
    cleaned["ingredients"] = (
        cleaned[ingredient_column].fillna("Mixed ingredients").astype(str) if ingredient_column else "Mixed ingredients"
    )
    cleaned["recipe"] = cleaned[recipe_column].fillna("").astype(str) if recipe_column else ""

    for column in [
        "vegetarian", "vegan", "gluten_free", "diabetic_friendly",
        "high_protein", "low_fat", "heart_healthy", "weight_loss_friendly",
    ]:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].apply(to_bool)
        else:
            cleaned[column] = False

    for placeholder_column in ["category", "cuisine", "meal_type", "tags"]:
        if placeholder_column not in cleaned.columns:
            cleaned[placeholder_column] = ""
        cleaned[placeholder_column] = cleaned[placeholder_column].fillna("").astype(str)

    if "serving_size_g" in cleaned.columns:
        cleaned["serving_size_g"] = pd.to_numeric(cleaned["serving_size_g"], errors="coerce")
    else:
        cleaned["serving_size_g"] = pd.NA
    cleaned["serving_size_g"] = cleaned["serving_size_g"].fillna(100.0).astype(float)
    cleaned.loc[cleaned["serving_size_g"] <= 0, "serving_size_g"] = 100.0

    cleaned["search_text"] = (
        cleaned["food_name"].astype(str)
        + " " + cleaned["ingredients"].astype(str)
        + " " + cleaned["tags"].astype(str)
        + " " + cleaned["category"].astype(str)
    ).str.lower()

    cleaned["allergens"] = [
        detect_allergens(
            record["food_name"],
            record["ingredients"],
            record["tags"],
            record["category"],
            record["gluten_free"],
            record["vegetarian"],
            record["vegan"],
        )
        for record in cleaned.to_dict("records")
    ]
    cleaned["allergen_text"] = [allergen_summary(item) for item in cleaned["allergens"]]

    return cleaned[
        [
            "food_name", "calories", "protein", "carbs", "fat", "fiber", "sugar", "sodium",
            "ingredients", "recipe", "category", "cuisine", "meal_type", "serving_size_g", "tags",
            "vegetarian", "vegan", "gluten_free", "diabetic_friendly", "high_protein", "low_fat",
            "heart_healthy", "weight_loss_friendly", "search_text", "allergens", "allergen_text",
        ]
    ]


@st.cache_data(show_spinner=False)
def get_prepared_dataset():
    return clean_food_dataset(load_food_dataset(None))


def get_food_choices(df, limit=120, prefer_healthy=True, category_filter=None):
    if df.empty:
        return []

    options = df.copy()
    options["food_name"] = options["food_name"].astype(str).str.strip()
    options = options[
        options["food_name"].ne("")
        & ~options["food_name"].str.lower().str.contains("unknown")
        & ~options["food_name"].str.lower().str.contains("mixed")
    ]
    options = options.drop_duplicates(subset=["food_name"])

    if category_filter and str(category_filter).lower() != "all":
        options = options[options["category"].astype(str).str.lower() == str(category_filter).lower()]

    if options.empty:
        return []

    if prefer_healthy:
        options["score"] = (
            options["protein"] * 1.2
            + options["fiber"] * 0.8
            - options["fat"] * 0.5
            - options["sugar"] * 0.2
            - options["sodium"] / 1000
        )
        options = options.sort_values(["score", "protein", "calories"], ascending=[False, False, True])
    else:
        options = options.sort_values(["food_name"])

    return options.head(limit)["food_name"].tolist()


def get_best_match(food_name, df):
    if df.empty:
        return None, []
    food_names = df["food_name"].astype(str).tolist()
    if not food_name:
        return None, []
    exact = df[df["food_name"].str.lower() == food_name.lower()]
    if not exact.empty:
        return exact.iloc[0], []
    matches = difflib.get_close_matches(food_name.lower(), [name.lower() for name in food_names], n=5, cutoff=0.45)
    if not matches:
        return None, []
    matched_rows = df[df["food_name"].str.lower().isin(matches)]
    return None, matched_rows.to_dict("records")
