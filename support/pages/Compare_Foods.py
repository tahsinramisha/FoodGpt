import streamlit as st

from support.core.data import get_prepared_dataset
from support.core.theme import allergen_pills_html, apply_theme, diet_pills_html, empty_state, error_state, page_header

apply_theme("Compare Foods")
page_header(
    "Compare Foods",
    "Put two foods head to head",
    "Pick two dataset foods and see which one wins each nutrient category. Lower calories, fat, "
    "sugar and sodium count as wins, along with higher protein and fiber.",
)

dataset = get_prepared_dataset()
if dataset.empty:
    error_state("Dataset not found", "Add <code>bd_food_nutrition_dataset.csv</code> to the project root.")
    st.stop()

food_names = sorted(dataset["food_name"].dropna().unique().tolist())
if len(food_names) < 2:
    empty_state("Not enough foods", "Need at least two distinct foods in the dataset to compare.")
    st.stop()

pick_a, pick_vs, pick_b = st.columns([2, 0.4, 2])
with pick_a:
    food_a_name = st.selectbox("Food A", options=food_names, index=0)
with pick_vs:
    st.markdown("<div style='text-align:center;padding-top:1.9rem;font-weight:800;color:var(--fg-rust)'>VS</div>", unsafe_allow_html=True)
with pick_b:
    default_b = 1 if len(food_names) > 1 else 0
    food_b_name = st.selectbox("Food B", options=food_names, index=default_b)

row_a = dataset[dataset["food_name"] == food_a_name].iloc[0]
row_b = dataset[dataset["food_name"] == food_b_name].iloc[0]

NUTRIENT_FIELDS = [
    ("calories", "Calories", "kcal", "lower"),
    ("protein", "Protein", "g", "higher"),
    ("carbs", "Carbs", "g", "neutral"),
    ("fat", "Fat", "g", "lower"),
    ("fiber", "Fiber", "g", "higher"),
    ("sugar", "Sugar", "g", "lower"),
    ("sodium", "Sodium", "mg", "lower"),
]


def decide_winner(value_a, value_b, direction):
    if value_a == value_b or direction == "neutral":
        return None
    if direction == "lower":
        return "a" if value_a < value_b else "b"
    return "a" if value_a > value_b else "b"


card_a, card_b = st.columns(2)
for col, row, side in [(card_a, row_a, "A"), (card_b, row_b, "B")]:
    with col:
        st.markdown(
            f"""
            <div class="fg-card">
                <div class="fg-card-title">{row['food_name']} <span style="color:var(--fg-ink-soft);font-weight:500">· {side}</span></div>
                <div class="fg-card-meta">{row['category']} · {row['cuisine']} · {row['meal_type']}</div>
                <div style="margin-top:0.5rem">{diet_pills_html(row)}{allergen_pills_html(row.get('allergens'))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

score_a, score_b = 0, 0
rows_html = []
for key, label, unit, direction in NUTRIENT_FIELDS:
    value_a = float(row_a.get(key, 0))
    value_b = float(row_b.get(key, 0))
    winner = decide_winner(value_a, value_b, direction)
    if winner == "a":
        score_a += 1
    elif winner == "b":
        score_b += 1
    a_style = "color:var(--fg-forest);font-weight:800" if winner == "a" else "font-weight:700"
    b_style = "color:var(--fg-forest);font-weight:800" if winner == "b" else "font-weight:700"
    rows_html.append(
        '<div style="display:flex;align-items:center;padding:0.5rem 0;border-bottom:1px solid var(--fg-border)">'
        f'<div style="width:37%;text-align:center;{a_style}">{value_a:.1f} {unit}</div>'
        f'<div style="width:26%;text-align:center;color:var(--fg-ink-soft);font-size:0.85rem">{label}</div>'
        f'<div style="width:37%;text-align:center;{b_style}">{value_b:.1f} {unit}</div>'
        "</div>"
    )

st.markdown(f"<div class='fg-card'>{''.join(rows_html)}</div>", unsafe_allow_html=True)

if score_a == score_b:
    verdict = f"It's a tie. {row_a['food_name']} and {row_b['food_name']} split the nutrient categories evenly."
elif score_a > score_b:
    verdict = f"{row_a['food_name']} wins {score_a} to {score_b} against {row_b['food_name']} on nutrient categories."
else:
    verdict = f"{row_b['food_name']} wins {score_b} to {score_a} against {row_a['food_name']} on nutrient categories."

st.markdown(f"<div class='fg-card'><div class='fg-card-title'>Verdict</div><div class='fg-card-meta'>{verdict}</div></div>", unsafe_allow_html=True)
