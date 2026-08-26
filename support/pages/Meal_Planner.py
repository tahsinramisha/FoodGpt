import streamlit as st

from support.core.data import get_prepared_dataset
from support.core.nutrition import NUTRIENT_UNITS, base_serving_grams, build_meal_plan, daily_value_percent
from support.core.theme import apply_theme, daily_value_html, empty_state, error_state, page_header

apply_theme("Meal Planner")
page_header(
    "Meal Planner",
    "A day's worth of meals, sized to fit",
    "Pick a goal and a calorie target, and each meal slot is filled with a matching dataset food and "
    "resized so the day lands close to your number.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

form_cols = st.columns([1, 1, 1])
with form_cols[0]:
    condition = st.selectbox(
        "Goal", ["general", "diabetes", "hypertension", "heart disease", "weight loss", "weight gain"]
    )
with form_cols[1]:
    target_calories = st.select_slider(
        "Daily target", options=[1200, 1500, 1800, 2000, 2200, 2500, 3000], value=2000
    )
with form_cols[2]:
    scale_portions = st.checkbox("Scale portions to hit the target", value=True)

if not st.button("Build plan", type="primary"):
    st.stop()

meals, totals = build_meal_plan(target_calories, condition, dataset, scale_portions)

if not meals:
    empty_state("No plan available", "No dataset foods fit this goal well enough to build a full day.")
    st.stop()

difference = totals["calories"] - float(target_calories)
st.markdown(
    f"<div class='fg-card'><div class='fg-card-title'>Estimated daily total</div>"
    f"<div class='fg-card-meta'>{totals['calories']:.0f} kcal ({difference:+.0f} vs your {target_calories} kcal target) · "
    f"{totals['protein']:.1f} g protein · {totals['carbs']:.1f} g carbs · {totals['fat']:.1f} g fat · "
    f"{totals['sodium']:.0f} mg sodium</div></div>",
    unsafe_allow_html=True,
)

meal_cols = st.columns(len(meals))
for col, meal in zip(meal_cols, meals):
    row = meal["row"]
    scaled = meal["scaled"]
    with col:
        st.markdown(
            f"""
            <div class="fg-card">
                <div class="fg-card-title">{meal['meal']} · {meal['grams']:.0f} g</div>
                <div class="fg-card-meta">{row['food_name']}<br>
                {scaled['calories']:.0f} kcal · {scaled['protein']:.1f} g protein · {scaled['fat']:.1f} g fat<br>
                {meal['factor']:.2f}x the listed {base_serving_grams(row):.0f} g serving</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown(
    daily_value_html(totals, daily_value_percent(totals), NUTRIENT_UNITS, title="Whole day vs a 2000 kcal reference"),
    unsafe_allow_html=True,
)

if len(meals) < 4:
    st.caption("Some meal slots stayed empty because too few dataset foods fit this goal tightly.")
if abs(difference) > float(target_calories) * 0.15:
    st.caption("Portions are capped between 0.4x and 3x the listed serving, so the total can drift from the target.")
