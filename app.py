"""FoodGPT
A polished food assistant built around a nutrition dataset for Bangladeshi and international foods.
"""

import os
import difflib
import streamlit as st
import pandas as pd

st.set_page_config(page_title="FoodGPT", page_icon="🍽️", layout="wide")

st.markdown(
    """
    <style>
    .main {padding-top: 0.4rem;}
    .hero {
        background: linear-gradient(135deg, #fff8ef 0%, #ffe7c7 45%, #ffd9ab 100%);
        padding: 1.6rem 1.7rem;
        border-radius: 22px;
        border: 1px solid #f4c98d;
        box-shadow: 0 14px 30px rgba(140, 70, 0, 0.13);
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #8a2c00;
        margin-bottom: 0.3rem;
    }
    .hero-sub {
        font-size: 1rem;
        color: #7a3c12;
        line-height: 1.5;
    }
    .card {
        background: white;
        padding: 1rem 1.1rem;
        border-radius: 16px;
        border: 1px solid #f2e0cf;
        box-shadow: 0 6px 18px rgba(0,0,0,0.05);
        margin-bottom: 0.95rem;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #7c2d12;
        margin-bottom: 0.45rem;
    }
    .pill {
        display: inline-block;
        background: #fff0da;
        color: #8a2c00;
        border-radius: 999px;
        padding: 0.35rem 0.7rem;
        margin: 0.2rem 0.3rem 0.2rem 0;
        font-size: 0.9rem;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">FoodGPT</div>
        <div class="hero-sub">Your AI food assistant for nutrition analysis, healthy food suggestions, recipe ideas, and smart meal planning using foods from your dataset.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("Ask about a food, get tailored recommendations, or build a daily meal plan using only foods from the dataset.")
st.markdown("<span class='pill'>Nutrition Analysis</span><span class='pill'>Health Suggestions</span><span class='pill'>Recipe Ideas</span><span class='pill'>Meal Planner</span>", unsafe_allow_html=True)

st.sidebar.title("FoodGPT Assistant")
st.sidebar.write("• Nutrition analysis")
st.sidebar.write("• Condition-based recommendations")
st.sidebar.write("• Recipe creation")
st.sidebar.write("• Daily meal planning")

base_dir = os.path.dirname(__file__) or os.getcwd()
default_dataset_paths = [
    os.path.join(base_dir, "bd_food_nutrition_dataset.csv"),
    os.path.join(base_dir, "data", "bd_food_nutrition_dataset.csv"),
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


def load_food_dataset(uploaded_file):
    if uploaded_file is not None:
        file_name = str(uploaded_file.name).lower()
        try:
            if file_name.endswith(".csv"):
                return pd.read_csv(uploaded_file)
            return pd.read_excel(uploaded_file)
        except Exception as error:
            st.error(f"Could not read the uploaded dataset file: {error}")
            return pd.DataFrame()

    for file_path in default_dataset_paths:
        if os.path.exists(file_path):
            try:
                if str(file_path).lower().endswith(".csv"):
                    return pd.read_csv(file_path)
                return pd.read_excel(file_path)
            except Exception:
                continue

    return pd.DataFrame()


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
    cleaned["ingredients"] = cleaned[ingredient_column].fillna("Mixed ingredients").astype(str) if ingredient_column else "Mixed ingredients"
    cleaned["recipe"] = cleaned[recipe_column].fillna("").astype(str) if recipe_column else ""

    for column in ["vegetarian", "vegan", "gluten_free", "diabetic_friendly", "high_protein", "low_fat", "heart_healthy", "weight_loss_friendly"]:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].apply(to_bool)

    for placeholder_column in ["category", "cuisine", "meal_type", "serving_size_g"]:
        if placeholder_column not in cleaned.columns:
            cleaned[placeholder_column] = ""

    return cleaned[
        [
            "food_name",
            "calories",
            "protein",
            "carbs",
            "fat",
            "fiber",
            "sugar",
            "sodium",
            "ingredients",
            "recipe",
            "category",
            "cuisine",
            "meal_type",
            "serving_size_g",
            "vegetarian",
            "vegan",
            "gluten_free",
            "diabetic_friendly",
            "high_protein",
            "low_fat",
            "heart_healthy",
            "weight_loss_friendly",
        ]
    ]


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


def nutrient_status(value, nutrient):
    if nutrient == "calories":
        if value < 180:
            return "low"
        if value < 350:
            return "moderate"
        return "high"
    if nutrient == "protein":
        if value >= 20:
            return "high"
        if value >= 10:
            return "good"
        return "low"
    if nutrient == "fat":
        if value < 10:
            return "low"
        if value < 20:
            return "moderate"
        return "high"
    if nutrient == "fiber":
        if value >= 3:
            return "high"
        if value >= 1:
            return "moderate"
        return "low"
    if nutrient == "sugar":
        if value <= 5:
            return "low"
        if value <= 15:
            return "moderate"
        return "high"
    if nutrient == "sodium":
        if value <= 300:
            return "low"
        if value <= 600:
            return "moderate"
        return "high"
    return "normal"


def explain_food(row):
    if row is None:
        return "No matching food was found."
    explanations = [
        f"Calories: {row['calories']:.1f} kcal, which is {nutrient_status(row['calories'], 'calories')} for a typical meal portion.",
        f"Protein: {row['protein']:.1f} g, which is {nutrient_status(row['protein'], 'protein')}.",
        f"Carbs: {row['carbs']:.1f} g, with {nutrient_status(row['carbs'], 'carbs')} carbohydrate content.",
        f"Fat: {row['fat']:.1f} g, which is {nutrient_status(row['fat'], 'fat')}.",
        f"Fiber: {row['fiber']:.1f} g, which is {nutrient_status(row['fiber'], 'fiber')}.",
        f"Sugar: {row['sugar']:.1f} g, which is {nutrient_status(row['sugar'], 'sugar')}.",
        f"Sodium: {row['sodium']:.1f} mg, which is {nutrient_status(row['sodium'], 'sodium')}.",
    ]
    return " ".join(explanations)


def recommend_foods(condition, df, limit=6):
    if df.empty:
        return []
    if condition == "diabetes":
        pool = df[(df["diabetic_friendly"] == True) & (df["sugar"] <= 10)].copy()
    elif condition == "hypertension":
        pool = df[(df["heart_healthy"] == True) & (df["sodium"] <= 400)].copy()
    elif condition == "heart disease":
        pool = df[(df["heart_healthy"] == True) & (df["fat"] <= 15) & (df["sodium"] <= 400)].copy()
    elif condition == "weight loss":
        pool = df[(df["weight_loss_friendly"] == True) & (df["calories"] <= 220)].copy()
    elif condition == "weight gain":
        pool = df[(df["calories"] >= 220) & (df["protein"] >= 15)].copy()
    else:
        pool = df.copy()
    if pool.empty:
        return []
    return pool.sort_values(["calories", "protein"], ascending=[True, False]).head(limit).to_dict("records")


def generate_recipe(food_name, df):
    row = None
    if not df.empty:
        exact = df[df["food_name"].str.lower() == food_name.lower()]
        if not exact.empty:
            row = exact.iloc[0]
    if row is None:
        return None

    ingredients = row.get("ingredients", "") if isinstance(row.get("ingredients"), str) else ""
    recipe_text = row.get("recipe", "") if isinstance(row.get("recipe"), str) else ""
    if recipe_text:
        return recipe_text

    ingredient_list = [item.strip() for item in ingredients.split(",") if item.strip()]
    if not ingredient_list:
        ingredient_list = [row["food_name"]]

    cooking_time = max(12, min(40, 8 + len(ingredient_list) * 2 + int(row.get('calories', 0) / 80)))
    style = 'stir-fry'
    if any(word in row['food_name'].lower() for word in ['curry', 'bhuna', 'masala', 'korma']):
        style = 'simmer'
    elif any(word in row['food_name'].lower() for word in ['roast', 'baked', 'grilled', 'tandoori']):
        style = 'roast'
    elif any(word in row['food_name'].lower() for word in ['salad', 'chutney', 'raita']):
        style = 'mix'
    elif any(word in row['food_name'].lower() for word in ['soup', 'shorba']):
        style = 'simmer'

    ingredient_text = ', '.join(ingredient_list[:5])
    if len(ingredient_list) > 5:
        ingredient_text += ', and more'

    steps = [
        f"1. Gather the ingredients for {row['food_name']}: {ingredient_text}.",
        f"2. Prepare the ingredients by chopping, marinating, or seasoning them to suit the dish.",
        f"3. In a pan or pot, {style} the ingredients for {row['food_name']} until their aromas are released.",
        f"4. Add liquid, spices, or sauce and cook until the dish has the right texture and flavor.",
        f"5. Finish the {row['food_name']} with fresh herbs or chutney and serve warm."
    ]
    return f"Recipe for {row['food_name']}\nCooking time: {cooking_time} minutes\n\n" + "\n".join(steps)


def build_meal_plan(target_calories, condition, df):
    if df.empty:
        return []
    pool = df.copy()
    if condition == "diabetes":
        pool = pool[pool["diabetic_friendly"] == True]
    elif condition == "hypertension":
        pool = pool[pool["sodium"] <= 450]
    elif condition == "heart disease":
        pool = pool[(pool["heart_healthy"] == True) & (pool["sodium"] <= 450)]
    elif condition == "weight loss":
        pool = pool[pool["weight_loss_friendly"] == True]
    elif condition == "weight gain":
        pool = pool[pool["calories"] >= 220]

    if pool.empty:
        pool = df.copy()

    breakfast = pool[pool["calories"] <= 300].sort_values("protein", ascending=False).head(1)
    lunch = pool[pool["calories"].between(250, 450)].sort_values("protein", ascending=False).head(1)
    dinner = pool[pool["calories"].between(250, 500)].sort_values("protein", ascending=False).head(1)
    snack = pool[pool["calories"] <= 180].sort_values("calories", ascending=False).head(1)

    meals = []
    for meal_name, meal_row in [("Breakfast", breakfast), ("Lunch", lunch), ("Dinner", dinner), ("Snack", snack)]:
        if not meal_row.empty:
            row = meal_row.iloc[0]
            meals.append((meal_name, row))

    total = sum(meal[1]["calories"] for meal in meals)
    return meals, total


dataset = load_food_dataset(None)
cleaned_dataset = clean_food_dataset(dataset)

if cleaned_dataset.empty:
    st.error(
        "No dataset was found. Add a file named `bd_food_nutrition_dataset.csv` to the project root or `data/` folder and push it to GitHub."
    )
    st.stop()

st.markdown("<div class='section-title'>1. Nutrition Analysis</div>", unsafe_allow_html=True)
category_options = ["All"] + sorted({str(value).strip() for value in cleaned_dataset["category"].dropna().astype(str).tolist() if str(value).strip()})
selected_category = st.selectbox("Choose a food category", options=category_options, index=0)
food_names = get_food_choices(cleaned_dataset, limit=120, prefer_healthy=True, category_filter=selected_category)
if food_names:
    selected_food = st.selectbox("Choose a food from the dataset", options=food_names, index=0)
else:
    selected_food = None
    st.info("No usable food items were found in the dataset.")

if selected_food:
    exact_row, suggestions = get_best_match(selected_food, cleaned_dataset)
    if exact_row is not None:
        row = exact_row
        st.markdown(f"<div class='card'><b>{row['food_name']}</b><br>{explain_food(row)}</div>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("Calories", f"{row['calories']:.1f} kcal")
        c2.metric("Protein", f"{row['protein']:.1f} g")
        c3.metric("Carbs", f"{row['carbs']:.1f} g")
        c4.metric("Fat", f"{row['fat']:.1f} g")
        c5.metric("Fiber", f"{row['fiber']:.1f} g")
        c6.metric("Sugar", f"{row['sugar']:.1f} g")
        c7.metric("Sodium", f"{row['sodium']:.1f} mg")
    else:
        st.warning("Food not found. Here are the closest options from your dataset:")
        for suggestion in suggestions:
            st.write(f"- {suggestion['food_name']}")

st.markdown("<div class='section-title'>2. Health Recommendations</div>", unsafe_allow_html=True)
condition = st.selectbox("Choose a goal or health need", ["diabetes", "hypertension", "heart disease", "weight loss", "weight gain", "general healthy eating"])
if st.button("Show recommendations"):
    recommended = recommend_foods(condition, cleaned_dataset, limit=6) if condition != "general healthy eating" else cleaned_dataset.head(6).to_dict("records")
    if recommended:
        for item in recommended:
            st.markdown(f"<div class='card'><b>{item['food_name']}</b><br>Calories: {item['calories']:.1f} kcal · Protein: {item['protein']:.1f} g · Fat: {item['fat']:.1f} g · Sodium: {item['sodium']:.1f} mg</div>", unsafe_allow_html=True)
    else:
        st.info("No suitable foods were found for this condition in the dataset.")

st.markdown("<div class='section-title'>3. Recipe Generation</div>", unsafe_allow_html=True)
recipe_input = st.selectbox("Choose a food for a recipe", options=food_names, index=0, key="recipe_input") if food_names else None
if recipe_input and st.button("Generate recipe"):
    recipe = generate_recipe(recipe_input, cleaned_dataset)
    if recipe:
        st.text_area("Recipe", recipe, height=220)
    else:
        st.info("Food not found in the dataset. Try a nearby food name.")

st.markdown("<div class='section-title'>4. Smart Meal Planner</div>", unsafe_allow_html=True)
plan_condition = st.selectbox("Meal plan goal", ["general", "diabetes", "hypertension", "heart disease", "weight loss", "weight gain"], key="meal_plan_goal")
target_calories = st.select_slider("Daily target calories", options=[1500, 2000, 2500], value=2000)
if st.button("Create meal plan"):
    meals, total = build_meal_plan(target_calories, plan_condition, cleaned_dataset)
    if meals:
        st.write(f"Estimated daily calories: {total:.1f} kcal")
        for meal_name, meal_row in meals:
            st.markdown(f"<div class='card'><b>{meal_name}</b>: {meal_row['food_name']}<br>Calories: {meal_row['calories']:.1f} kcal · Protein: {meal_row['protein']:.1f} g · Fat: {meal_row['fat']:.1f} g</div>", unsafe_allow_html=True)
    else:
        st.info("No meal plan could be generated from the dataset.")
