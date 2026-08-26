import streamlit as st

from support.core.data import get_prepared_dataset
from support.core.nutrition import analyze_menu
from support.core.theme import allergen_pills_html, apply_theme, empty_state, error_state, page_header

apply_theme("Menu Analyzer")
page_header(
    "Menu Analyzer",
    "One line per item, matched to the data",
    "Paste a menu, order, or grocery list with one food per line, and each item is matched to the "
    "closest thing in the dataset with its nutrition pulled in.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

menu_text = st.text_area(
    "Menu items", height=140, placeholder="Chicken curry\nBeef steak\nMixed vegetable salad"
)
run = st.button("Analyze", type="primary")

if not run:
    empty_state("Nothing analyzed yet", "Enter menu items above and click Analyze.")
    st.stop()

results = analyze_menu(menu_text, dataset)
if not results:
    empty_state("Nothing to analyze", "Enter at least one line of text above.")
    st.stop()

for entry in results:
    row = entry.get("row")
    allergen_html = f"<div class='fg-card-meta'>{allergen_pills_html(row.get('allergens'))}</div>" if row else ""
    suggestion_html = (
        f"<div class='fg-card-meta'><b>Other matches:</b> {entry['suggestions']}</div>"
        if entry.get("suggestions")
        else ""
    )
    st.markdown(
        f"""
        <div class="fg-card">
            <div class="fg-card-title">{entry['menu_item']}</div>
            <div class="fg-card-meta"><b>Match:</b> {entry['match']} ({entry['confidence']})</div>
            <div class="fg-card-meta"><b>Calories:</b> {entry['calories']} kcal · Protein: {entry['protein']} g ·
            Fat: {entry['fat']} g · Sodium: {entry['sodium']} mg</div>
            {allergen_html}{suggestion_html}
        </div>
        """,
        unsafe_allow_html=True,
    )
