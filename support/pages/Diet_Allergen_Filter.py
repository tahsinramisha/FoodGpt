import streamlit as st

from support.core.data import ALLERGEN_RULES, DIET_FILTERS, apply_food_filters, get_prepared_dataset
from support.core.nutrition import base_serving_grams
from support.core.theme import allergen_pills_html, apply_theme, diet_pills_html, empty_state, error_state, page_header

apply_theme("Diet & Allergen Filter")
page_header(
    "Diet & Allergen Filter",
    "Foods estimated safe for you",
    "Allergen labels are estimated from each food's name, ingredients, tags, and category, so always "
    "confirm with the cook or the label before eating.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

control_cols = st.columns([1, 1, 1, 0.6])
with control_cols[0]:
    selected_diets = st.multiselect(
        "Dietary preferences",
        options=list(DIET_FILTERS.keys()),
        help="\n".join(f"{name}: {desc}" for name, desc in DIET_FILTERS.items()),
    )
with control_cols[1]:
    selected_allergens = st.multiselect("Allergies to avoid", options=list(ALLERGEN_RULES.keys()))
with control_cols[2]:
    avoid_input = st.text_input("Avoid ingredients", placeholder="onion, mustard oil")
with control_cols[3]:
    strict_mode = st.checkbox("Strict mode", value=False, help="Also removes foods that only may contain an allergen.")

avoid_words = [word.strip().lower() for word in avoid_input.split(",") if word.strip()]
active_filters = bool(selected_diets or selected_allergens or avoid_words)
filtered = apply_food_filters(dataset, selected_diets, selected_allergens, avoid_words, strict_mode)

summary_cols = st.columns(2)
summary_cols[0].metric("Foods that fit", len(filtered))
summary_cols[1].metric("Total in dataset", len(dataset))

if active_filters and filtered.empty:
    empty_state(
        "Nothing matches every rule",
        "No food satisfies all selected restrictions at once. Remove a filter or turn off strict mode.",
    )
    st.stop()

if not active_filters:
    st.caption("No restrictions set. Showing a sample of the full dataset.")

display_pool = filtered if active_filters else dataset.head(40)

cols = st.columns(2)
for index, (_, row) in enumerate(display_pool.head(40).iterrows()):
    with cols[index % 2]:
        st.markdown(
            f"""
            <div class="fg-card">
                <div class="fg-card-title">{row['food_name']}</div>
                <div class="fg-card-meta">Serving {base_serving_grams(row):.0f} g ·
                {row['calories']:.0f} kcal · {row['protein']:.1f} g protein · {row['sodium']:.0f} mg sodium</div>
                <div style="margin-top:0.5rem">{allergen_pills_html(row.get('allergens'))}{diet_pills_html(row)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
