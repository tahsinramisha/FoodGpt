import streamlit as st

from support.core.data import get_best_match, get_food_choices, get_prepared_dataset
from support.core.nutrition import base_serving_grams, estimate_ingredient_amounts, generate_recipe, scale_row
from support.core.theme import apply_theme, empty_state, error_state, page_header

apply_theme("Recipe Generator")
page_header(
    "Recipe Generator",
    "From dataset entry to cooking steps",
    "Pick a food and a batch size, and you'll get cooking steps plus ingredient amounts and nutrition "
    "scaled to how many people you're feeding.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

food_names = get_food_choices(dataset, limit=200, prefer_healthy=False)
if not food_names:
    empty_state("No foods available", "The dataset has no usable food names to build a recipe from.")
    st.stop()

form_cols = st.columns([2, 1])
with form_cols[0]:
    selected_food = st.selectbox("Food", options=food_names, index=0)
with form_cols[1]:
    servings = st.number_input("Cook for how many people?", min_value=1, max_value=20, value=2, step=1)

generate = st.button("Generate recipe", type="primary")

if not generate:
    st.stop()

recipe_row, _ = get_best_match(selected_food, dataset)
recipe_text = generate_recipe(selected_food, dataset)

if recipe_row is None or recipe_text is None:
    empty_state("Recipe unavailable", "This food couldn't be matched to a dataset row.")
    st.stop()

base_grams = base_serving_grams(recipe_row)
batch_grams = base_grams * servings
batch_scaled, _ = scale_row(recipe_row, batch_grams)

st.text_area("Steps", recipe_text, height=220)

amounts = estimate_ingredient_amounts(recipe_row.get("ingredients"), batch_grams)
amounts_html = "".join(f"<div class='fg-card-meta'>{name}: {amount}</div>" for name, amount in amounts)
st.markdown(
    f"<div class='fg-card'><div class='fg-card-title'>Ingredients for {servings} serving(s) · about {batch_grams:.0f} g cooked</div>{amounts_html}</div>",
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
metric_cols[0].metric("Batch calories", f"{batch_scaled['calories']:.0f} kcal")
metric_cols[1].metric("Per serving", f"{batch_scaled['calories'] / servings:.0f} kcal")
metric_cols[2].metric("Batch protein", f"{batch_scaled['protein']:.1f} g")
metric_cols[3].metric("Batch sodium", f"{batch_scaled['sodium']:.0f} mg")
st.caption("Ingredient amounts are estimates spread across the listed ingredients, so adjust to taste.")
