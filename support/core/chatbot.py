import os
import re

import streamlit as st

from support.core.data import get_best_match
from support.core.nutrition import (
    build_meal_plan,
    explain_food,
    generate_recipe,
    recommend_foods,
)

GROQ_MODEL = "openai/gpt-oss-20b"

CONDITION_ALIASES = {
    "diabetes": "diabetes",
    "diabetic": "diabetes",
    "blood sugar": "diabetes",
    "high blood pressure": "hypertension",
    "hypertension": "hypertension",
    "blood pressure": "hypertension",
    "heart": "heart disease",
    "heart disease": "heart disease",
    "weight loss": "weight loss",
    "losing weight": "weight loss",
    "lose weight": "weight loss",
    "weight gain": "weight gain",
    "gaining weight": "weight gain",
    "bulking": "weight gain",
}

TRAIT_ALIASES = {
    "vegan": "vegan",
    "vegetarian": "vegetarian",
    "gluten free": "gluten_free",
    "gluten-free": "gluten_free",
    "high protein": "high_protein",
    "high-protein": "high_protein",
    "low fat": "low_fat",
    "low-fat": "low_fat",
    "heart healthy": "heart_healthy",
    "heart-healthy": "heart_healthy",
    "diabetic friendly": "diabetic_friendly",
    "diabetic-friendly": "diabetic_friendly",
    "weight loss friendly": "weight_loss_friendly",
}


def get_groq_api_key():
    try:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return key
    except Exception:
        pass
    return os.environ.get("GROQ_API_KEY")


def _clean_food_query(text):
    text = text.strip().strip("?.! ")
    text = re.sub(r"^(a|an|the)\s+", "", text, flags=re.IGNORECASE)
    return text



# Rule-based intents


def _try_calories(message, df):
    match = re.search(
        r"(?:how many\s+)?(?:calories|kcal|calorie count)\b.*?\b(?:in|of|for)\s+(.+)",
        message, re.IGNORECASE,
    )
    if not match:
        return None
    food_query = _clean_food_query(match.group(1))
    row, suggestions = get_best_match(food_query, df)
    if row is not None:
        return (
            f"**{row['food_name']}** has about **{row['calories']:.0f} kcal** per {row['serving_size_g']:.0f} g "
            f"listed serving, with {row['protein']:.1f} g protein, {row['carbs']:.1f} g carbs, {row['fat']:.1f} g fat."
        )
    if suggestions:
        names = ", ".join(s["food_name"] for s in suggestions[:4])
        return f"I couldn't find \"{food_query}\" exactly. Closest matches in the dataset: {names}."
    return None


def _try_condition_fit(message, df):
    match = re.search(
        r"is\s+(.+?)\s+(?:good|ok|okay|safe|suitable|bad)\s+for\s+(.+)", message, re.IGNORECASE
    )
    if not match:
        return None
    food_query = _clean_food_query(match.group(1))
    condition_text = match.group(2).strip().strip("?.! ").lower()
    condition = next((v for k, v in CONDITION_ALIASES.items() if k in condition_text), None)
    if not condition:
        return None
    row, suggestions = get_best_match(food_query, df)
    if row is None:
        if suggestions:
            names = ", ".join(s["food_name"] for s in suggestions[:4])
            return f"I couldn't find \"{food_query}\" exactly. Did you mean: {names}?"
        return None
    verdicts = {
        "diabetes": row["diabetic_friendly"] and row["sugar"] <= 10,
        "hypertension": row["heart_healthy"] and row["sodium"] <= 400,
        "heart disease": row["heart_healthy"] and row["fat"] <= 15 and row["sodium"] <= 400,
        "weight loss": row["weight_loss_friendly"] and row["calories"] <= 220,
        "weight gain": row["calories"] >= 220 and row["protein"] >= 15,
    }
    good = verdicts.get(condition, False)
    verb = "is a good fit" if good else "isn't the best fit"
    return (
        f"**{row['food_name']}** {verb} for {condition}. "
        f"{explain_food(row)}"
    )


def _try_recipe(message, df):
    match = re.search(
        r"(?:recipe for|how (?:do|to) (?:i |you )?(?:make|cook))\s+(.+)", message, re.IGNORECASE
    )
    if not match:
        return None
    food_query = _clean_food_query(match.group(1))
    row, suggestions = get_best_match(food_query, df)
    if row is not None:
        recipe = generate_recipe(row["food_name"], df)
        return recipe or f"I have {row['food_name']} in the dataset but no recipe steps for it yet."
    if suggestions:
        names = ", ".join(s["food_name"] for s in suggestions[:4])
        return f"I don't have \"{food_query}\" in the dataset. Closest matches: {names}."
    return None


def _try_meal_plan(message, df):
    if not re.search(r"meal plan|diet plan|plan.*meals?", message, re.IGNORECASE):
        return None
    calorie_match = re.search(r"(\d{3,5})\s*(?:kcal|cal|calories)?", message)
    target_calories = int(calorie_match.group(1)) if calorie_match else 2000
    condition = "general"
    lowered = message.lower()
    for phrase, mapped in CONDITION_ALIASES.items():
        if phrase in lowered:
            condition = mapped
            break
    meals, totals = build_meal_plan(target_calories, condition, df, scale_portions=True)
    if not meals:
        return "I couldn't build a meal plan from the current dataset. Try a different calorie target."
    lines = [f"Here's a **{target_calories} kcal** day for {condition}:"]
    for meal in meals:
        row = meal["row"]
        lines.append(f"- **{meal['meal']}**: {row['food_name']} ({meal['grams']:.0f} g, {meal['scaled']['calories']:.0f} kcal)")
    lines.append(f"\nEstimated total: {totals['calories']:.0f} kcal, {totals['protein']:.1f} g protein.")
    return "\n".join(lines)


def _try_trait_list(message, df):
    match = re.search(
        r"(?:what|which)\s+foods?\s+(?:are|is)\s+(.+)", message, re.IGNORECASE
    )
    if not match:
        return None
    trait_text = match.group(1).strip().strip("?.! ").lower()
    column = next((v for k, v in TRAIT_ALIASES.items() if k in trait_text), None)
    if not column:
        return None
    pool = df[df[column] == True]
    if pool.empty:
        return f"No foods in the dataset are marked {trait_text}."
    names = pool.sort_values("protein", ascending=False).head(8)["food_name"].tolist()
    return f"Foods marked **{trait_text}**: " + ", ".join(names) + "."


RULES = [_try_calories, _try_condition_fit, _try_recipe, _try_meal_plan, _try_trait_list]


def try_rule_based(message, df):
    for rule in RULES:
        try:
            answer = rule(message, df)
        except Exception:
            answer = None
        if answer:
            return answer
    return None


# Dataset retrieval for grounding the Groq call

def retrieve_context_rows(message, df, limit=6):
    if df.empty:
        return []
    tokens = [token for token in re.findall(r"[a-zA-Z]{3,}", message.lower())]
    if not tokens:
        return []
    haystack = (
        df["food_name"].str.lower() + " "
        + df["category"].str.lower() + " "
        + df["cuisine"].str.lower() + " "
        + df["tags"].str.lower()
    )
    scores = haystack.apply(lambda text: sum(1 for token in tokens if token in text))
    matched = df[scores > 0].copy()
    if matched.empty:
        return []
    matched["_score"] = scores[scores > 0]
    matched = matched.sort_values("_score", ascending=False)
    return matched.head(limit).to_dict("records")


def format_context_rows(rows):
    if not rows:
        return "No dataset rows matched this message. Do not invent specific foods or numbers from the dataset."
    lines = []
    for row in rows:
        lines.append(
            f"- {row['food_name']} ({row['category']}, {row['cuisine']}): "
            f"{row['calories']:.0f} kcal, {row['protein']:.1f}g protein, {row['carbs']:.1f}g carbs, "
            f"{row['fat']:.1f}g fat, {row['sodium']:.0f}mg sodium per {row['serving_size_g']:.0f}g serving. "
            f"Tags: {row['tags'] or 'none'}."
        )
    return "\n".join(lines)


SYSTEM_PROMPT = """You are the FoodGPT chat assistant, built into a food nutrition dashboard for \
Bangladeshi and international dishes. Answer conversationally, like a knowledgeable friend, not a form. \
Keep answers short and specific. Use the "Relevant dataset rows" below as your source of truth for any \
food facts. Never invent nutrition numbers or dataset entries that aren't listed there. If the dataset \
has nothing relevant, say so plainly and answer generally instead."""


def call_groq(history, context_text):
    api_key = get_groq_api_key()
    if not api_key:
        raise RuntimeError("missing_api_key")

    from groq import Groq

    client = Groq(api_key=api_key)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT + "\n\nRelevant dataset rows:\n" + context_text},
    ] + history

    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.6,
        max_tokens=500,
    )
    return completion.choices[0].message.content


def get_response(message, history, df):
    """Return (reply_text, note). note is set when we fell back from Groq."""
    rule_answer = try_rule_based(message, df)
    if rule_answer:
        return rule_answer, None

    context_rows = retrieve_context_rows(message, df)
    context_text = format_context_rows(context_rows)

    try:
        reply = call_groq(history, context_text)
        return reply, None
    except Exception as error:
        if str(error) == "missing_api_key":
            reply = (
                "I'd love to chat more freely, but the Groq API key isn't set up yet, so I'm limited "
                "to what I can answer straight from the dataset for now."
            )
            note = None
        else:
            if context_rows:
                top = context_rows[0]
                reply = (
                    "I couldn't reach Groq just now, so here's what I can tell you from the dataset: "
                    f"**{top['food_name']}** has {top['calories']:.0f} kcal and {top['protein']:.1f}g protein "
                    f"per {top['serving_size_g']:.0f}g. Ask me again in a moment for a fuller answer."
                )
            else:
                reply = (
                    "I couldn't reach Groq just now, and nothing in the dataset matches this either. "
                    "Try again in a moment, or ask about a specific food."
                )
            note = f"Groq error ({type(error).__name__}): {error}"
        return reply, note
