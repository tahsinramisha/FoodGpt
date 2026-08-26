import streamlit as st

from support.core.data import get_prepared_dataset
from support.core.nutrition import base_serving_grams, recommend_foods
from support.core.theme import apply_theme, empty_state, error_state, page_header

apply_theme("Health Recommendations")
page_header(
    "Health Recommendations",
    "Eat for the goal you actually have",
    "Choose a condition or goal and see the dataset foods that fit it best, sorted by calories, "
    "then protein.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

CONDITIONS = ["diabetes", "hypertension", "heart disease", "weight loss", "weight gain", "general healthy eating"]

condition = st.selectbox("Goal or health need", CONDITIONS)

results = (
    recommend_foods(condition, dataset, limit=8)
    if condition != "general healthy eating"
    else dataset.sort_values(["calories", "protein"], ascending=[True, False]).head(8).to_dict("records")
)

if not results:
    empty_state(
        "No matches for this goal",
        "No foods in the dataset satisfy this condition's rules right now. Try a different goal.",
    )
    st.stop()

cols = st.columns(2)
for index, item in enumerate(results):
    with cols[index % 2]:
        st.markdown(
            f"""
            <div class="fg-card">
                <div class="fg-card-title">{item['food_name']}</div>
                <div class="fg-card-meta">Serving {base_serving_grams(item):.0f} g ·
                {item['calories']:.0f} kcal · {item['protein']:.1f} g protein ·
                {item['fat']:.1f} g fat · {item['sodium']:.0f} mg sodium</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
