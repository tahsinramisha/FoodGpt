"""Nutrient scoring, portion scaling, recipes, and meal planning.

Everything here operates on the cleaned dataframe produced by core.data.
This module never reads the CSV directly.
"""

from support.core.data import get_best_match

NUTRIENT_KEYS = ["calories", "protein", "carbs", "fat", "fiber", "sugar", "sodium"]

NUTRIENT_UNITS = {
    "calories": "kcal",
    "protein": "g",
    "carbs": "g",
    "fat": "g",
    "fiber": "g",
    "sugar": "g",
    "sodium": "mg",
}

# Reference intake for an average adult on a 2000 kcal day.
DAILY_REFERENCE = {
    "calories": 2000.0,
    "protein": 50.0,
    "carbs": 275.0,
    "fat": 70.0,
    "fiber": 28.0,
    "sugar": 50.0,
    "sodium": 2300.0,
}


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


# ---------------------------------------------------------------------------
# Portion and quantity scaling
# ---------------------------------------------------------------------------

SEASONING_WORDS = {
    "spices", "spice", "salt", "turmeric", "chili", "chilli", "pepper", "masala",
    "garam masala", "cumin", "coriander", "ginger", "garlic", "bay leaf", "cardamom",
    "cinnamon", "mustard", "sugar",
}
FAT_WORDS = {"oil", "ghee", "butter", "butter/oil", "mustard oil"}
LIQUID_WORDS = {"water", "broth", "stock", "milk", "coconut milk", "fruit/milk"}


def base_serving_grams(row):
    try:
        value = float(row.get("serving_size_g") or 0)
    except (TypeError, ValueError):
        value = 0.0
    return value if value > 0 else 100.0


def scale_row(row, grams):
    """Scale every nutrient of a food to the requested weight in grams."""
    base = base_serving_grams(row)
    factor = float(grams) / base if base else 1.0
    scaled = {}
    for key in NUTRIENT_KEYS:
        try:
            scaled[key] = float(row.get(key, 0) or 0) * factor
        except (TypeError, ValueError):
            scaled[key] = 0.0
    return scaled, factor


def daily_value_percent(scaled):
    return {
        key: (scaled.get(key, 0.0) / DAILY_REFERENCE[key] * 100.0) if DAILY_REFERENCE[key] else 0.0
        for key in NUTRIENT_KEYS
    }


def portion_advice(row, scaled, factor, grams):
    tips = [
        f"This portion is {grams:.0f} g, which is {factor:.2f}x the dataset serving of {base_serving_grams(row):.0f} g."
    ]
    if scaled["calories"] >= 700:
        tips.append("That is a large calorie load for one sitting, so keep the rest of the day lighter.")
    elif scaled["calories"] <= 150:
        tips.append("This is a light portion and works well as a snack or a side.")
    if scaled["protein"] >= 25:
        tips.append("Protein at this quantity is high and covers a solid share of a daily target.")
    elif scaled["protein"] < 7:
        tips.append("Protein is low here, so pair it with fish, egg, lentils or chicken.")
    if scaled["sodium"] > 1200:
        tips.append("Sodium is very high at this quantity, which matters for blood pressure.")
    if scaled["sugar"] > 25:
        tips.append("Sugar is high at this quantity, so treat it as an occasional portion.")
    if scaled["fiber"] >= 6:
        tips.append("Fiber is good at this portion and helps with fullness and digestion.")
    return " ".join(tips)


def estimate_ingredient_amounts(ingredients_text, grams):
    """Spread a target cooked weight across the listed ingredients."""
    items = [item.strip() for item in str(ingredients_text or "").split(",") if item.strip()]
    if not items:
        return []

    scale = max(float(grams), 1.0) / 100.0
    fixed = {}
    bulk_items = []
    for item in items:
        key = item.lower()
        if key in SEASONING_WORDS:
            fixed[item] = ("seasoning", 2.0 * scale)
        elif key in FAT_WORDS:
            fixed[item] = ("fat", 6.0 * scale)
        elif key in LIQUID_WORDS:
            fixed[item] = ("liquid", 20.0 * scale)
        else:
            bulk_items.append(item)

    used = sum(amount for _, amount in fixed.values())
    remaining = max(float(grams) - used, float(grams) * 0.2)
    weights = [2.0 if index == 0 else 1.0 for index in range(len(bulk_items))]
    total_weight = sum(weights) or 1.0

    amounts = []
    for item in items:
        if item in fixed:
            kind, amount = fixed[item]
            if kind == "seasoning":
                amounts.append((item, f"{amount:.1f} g (about {max(0.25, amount / 5.0):.2f} tsp)"))
            elif kind == "fat":
                amounts.append((item, f"{amount:.1f} g (about {max(0.25, amount / 13.5):.2f} tbsp)"))
            else:
                amounts.append((item, f"{amount:.0f} ml"))
        else:
            position = bulk_items.index(item)
            amounts.append((item, f"{remaining * (weights[position] / total_weight):.0f} g"))
    return amounts


# ---------------------------------------------------------------------------
# Recommendations, recipes, meal planning, menu analysis
# ---------------------------------------------------------------------------


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

    cooking_time = max(12, min(40, 8 + len(ingredient_list) * 2 + int(row.get("calories", 0) / 80)))
    style = "stir-fry"
    lowered = row["food_name"].lower()
    if any(word in lowered for word in ["curry", "bhuna", "masala", "korma"]):
        style = "simmer"
    elif any(word in lowered for word in ["roast", "baked", "grilled", "tandoori"]):
        style = "roast"
    elif any(word in lowered for word in ["salad", "chutney", "raita"]):
        style = "mix"
    elif any(word in lowered for word in ["soup", "shorba"]):
        style = "simmer"

    ingredient_text = ", ".join(ingredient_list[:5])
    if len(ingredient_list) > 5:
        ingredient_text += ", and more"

    steps = [
        f"1. Gather the ingredients for {row['food_name']}: {ingredient_text}.",
        "2. Prepare the ingredients by chopping, marinating, or seasoning them to suit the dish.",
        f"3. In a pan or pot, {style} the ingredients for {row['food_name']} until their aromas are released.",
        "4. Add liquid, spices, or sauce and cook until the dish has the right texture and flavor.",
        f"5. Finish the {row['food_name']} with fresh herbs or chutney and serve warm.",
    ]
    return f"Recipe for {row['food_name']}\nCooking time: {cooking_time} minutes\n\n" + "\n".join(steps)


MEAL_SHARES = {"Breakfast": 0.25, "Lunch": 0.35, "Dinner": 0.30, "Snack": 0.10}


def build_meal_plan(target_calories, condition, df, scale_portions=True):
    """Pick one food per meal and size each portion towards the calorie target."""
    if df.empty:
        return [], {key: 0.0 for key in NUTRIENT_KEYS}
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
        if meal_row.empty:
            continue
        row = meal_row.iloc[0]
        base_grams = base_serving_grams(row)
        grams = base_grams

        if scale_portions:
            meal_target = float(target_calories) * MEAL_SHARES.get(meal_name, 0.25)
            base_calories = float(row.get("calories", 0) or 0)
            if base_calories > 0:
                wanted = base_grams * (meal_target / base_calories)
                grams = min(max(wanted, base_grams * 0.4), base_grams * 3.0)

        scaled, factor = scale_row(row, grams)
        meals.append({"meal": meal_name, "row": row, "grams": grams, "factor": factor, "scaled": scaled})

    totals = {key: sum(meal["scaled"][key] for meal in meals) for key in NUTRIENT_KEYS}
    return meals, totals


def analyze_menu(menu_text, df):
    entries = []
    if df.empty or not menu_text:
        return entries
    for line in [line.strip() for line in menu_text.splitlines() if line.strip()]:
        exact, suggestions = get_best_match(line, df)
        if exact is not None:
            entries.append({
                "menu_item": line,
                "match": exact["food_name"],
                "calories": exact["calories"],
                "protein": exact["protein"],
                "fat": exact["fat"],
                "sodium": exact["sodium"],
                "confidence": "Exact match",
                "row": exact.to_dict(),
            })
        elif suggestions:
            first = suggestions[0]
            entries.append({
                "menu_item": line,
                "match": first["food_name"],
                "calories": first["calories"],
                "protein": first["protein"],
                "fat": first["fat"],
                "sodium": first["sodium"],
                "confidence": "Best guess",
                "suggestions": ", ".join(s["food_name"] for s in suggestions[:3]),
                "row": first,
            })
        else:
            entries.append({
                "menu_item": line,
                "match": "No match found",
                "calories": "-",
                "protein": "-",
                "fat": "-",
                "sodium": "-",
                "confidence": "No matching food",
            })
    return entries
