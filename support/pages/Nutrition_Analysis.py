import streamlit as st

from support.core.data import get_best_match, get_food_choices, get_prepared_dataset
from support.core.nutrition import (
    base_serving_grams,
    daily_value_percent,
    explain_food,
    NUTRIENT_UNITS,
    portion_advice,
    scale_row,
)
from support.core.theme import apply_theme, daily_value_html, empty_state, error_state, page_header

apply_theme("Nutrition Analysis")
page_header(
    "Nutrition Analysis",
    "What's actually in it",
    "Pick a food from the dataset and see its calories, macros, and a plain-language read on each "
    "number, then rescale everything to the portion you're actually eating.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

left, right = st.columns([2, 1])
with left:
    category_options = ["All"] + sorted(
        {str(v).strip() for v in dataset["category"].dropna().astype(str) if str(v).strip()}
    )
    selected_category = st.selectbox("Category", options=category_options, index=0)
    food_names = get_food_choices(dataset, limit=150, prefer_healthy=True, category_filter=selected_category)
    selected_food = st.selectbox("Food", options=food_names, index=0) if food_names else None
with right:
    st.metric("Foods in this category", len(food_names))

if not selected_food:
    empty_state("Nothing to show yet", "No foods matched this category.")
    st.stop()

row, suggestions = get_best_match(selected_food, dataset)
if row is None:
    empty_state(
        "No exact match",
        "Closest options: " + ", ".join(s["food_name"] for s in suggestions) if suggestions else "No close matches found.",
    )
    st.stop()

base_grams = base_serving_grams(row)
st.markdown(
    f"<div class='fg-card'><div class='fg-card-title'>{row['food_name']}</div>"
    f"<div class='fg-card-meta'>{row['category']} · {row['cuisine']} · listed serving {base_grams:.0f} g</div></div>",
    unsafe_allow_html=True,
)

metric_cols = st.columns(7)
for col, (label, key, unit) in zip(
    metric_cols,
    [
        ("Calories", "calories", "kcal"), ("Protein", "protein", "g"), ("Carbs", "carbs", "g"),
        ("Fat", "fat", "g"), ("Fiber", "fiber", "g"), ("Sugar", "sugar", "g"), ("Sodium", "sodium", "mg"),
    ],
):
    col.metric(label, f"{row[key]:.1f} {unit}")

st.markdown(f"<div class='fg-card'><div class='fg-card-title'>Reading these numbers</div><div class='fg-card-meta'>{explain_food(row)}</div></div>", unsafe_allow_html=True)

st.subheader("Rescale to your portion")
scale_cols = st.columns(3)
with scale_cols[0]:
    portion_grams = st.number_input("Portion size (g)", min_value=10.0, max_value=2000.0, value=float(base_grams), step=10.0)
with scale_cols[1]:
    servings = st.number_input("Servings", min_value=0.5, max_value=12.0, value=1.0, step=0.5)
with scale_cols[2]:
    preset = st.radio("Quick size", options=["Custom", "Half plate", "One plate", "Two plates"], index=0)

preset_factors = {"Half plate": 0.5, "One plate": 1.0, "Two plates": 2.0}
total_grams = base_grams * preset_factors[preset] * servings if preset in preset_factors else portion_grams * servings

scaled, factor = scale_row(row, total_grams)
st.metric("Total quantity on the plate", f"{total_grams:.0f} g")

scaled_cols = st.columns(7)
for col, (label, key, unit) in zip(
    scaled_cols,
    [
        ("Calories", "calories", "kcal"), ("Protein", "protein", "g"), ("Carbs", "carbs", "g"),
        ("Fat", "fat", "g"), ("Fiber", "fiber", "g"), ("Sugar", "sugar", "g"), ("Sodium", "sodium", "mg"),
    ],
):
    col.metric(label, f"{scaled[key]:.1f} {unit}", delta=f"{scaled[key] - float(row[key]):+.1f}")

st.markdown(daily_value_html(scaled, daily_value_percent(scaled), NUTRIENT_UNITS), unsafe_allow_html=True)
st.markdown(
    f"<div class='fg-card'><div class='fg-card-title'>Portion guidance</div><div class='fg-card-meta'>{portion_advice(row, scaled, factor, total_grams)}</div></div>",
    unsafe_allow_html=True,
)
