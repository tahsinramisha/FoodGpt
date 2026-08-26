import os

import streamlit as st

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_BLANK_FAVICON = os.path.join(_BASE_DIR, "assets", "favicon.png")

# ---------------------------------------------------------------------------
# The feature registry: the single source of truth for what pages exist.
# support/pages/Dashboard.py builds its hero nav from this list, and every
# page's top nav bar is built from it too, so a new feature only has to be
# added here.
# ---------------------------------------------------------------------------

FEATURES = [
    {
        "key": "nutrition",
        "title": "Nutrition Analysis",
        "description": "Look up a food and see its full nutrient breakdown against reference guidelines.",
        "page": "support/pages/Nutrition_Analysis.py",
    },
    {
        "key": "health",
        "title": "Health Recommendations",
        "description": "Foods matched to a condition or goal: diabetes, hypertension, weight loss, and more.",
        "page": "support/pages/Health_Recommendations.py",
    },
    {
        "key": "recipe",
        "title": "Recipe Generator",
        "description": "Turn any dataset food into step by step cooking instructions, scaled to your batch size.",
        "page": "support/pages/Recipe_Generator.py",
    },
    {
        "key": "planner",
        "title": "Meal Planner",
        "description": "A full day of meals sized to hit a calorie target, built around a health goal.",
        "page": "support/pages/Meal_Planner.py",
    },
    {
        "key": "menu",
        "title": "Menu Analyzer",
        "description": "Paste a menu or grocery list and match each line to the closest dataset food.",
        "page": "support/pages/Menu_Analyzer.py",
    },
    {
        "key": "filter",
        "title": "Diet & Allergen Filter",
        "description": "Set allergies and dietary rules once, then browse only the foods that fit.",
        "page": "support/pages/Diet_Allergen_Filter.py",
    },
    {
        "key": "compare",
        "title": "Compare Foods",
        "description": "Two foods, side by side, with a nutrient by nutrient verdict on which wins.",
        "page": "support/pages/Compare_Foods.py",
    },
    {
        "key": "chat",
        "title": "Chat Assistant",
        "description": "Ask questions in plain language and get answers grounded in the food dataset.",
        "page": "support/pages/Chat_Assistant.py",
    },
]

WORDMARK = "FoodGPT"

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Manrope:wght@400;500;600;700;800&display=swap');

:root {
    --fg-ink: #f5efe4;
    --fg-ink-soft: #b3a892;
    --fg-paper: #14110c;
    --fg-card: #1d1911;
    --fg-border: #33291b;
    --fg-rust: #e2793f;
    --fg-rust-dark: #c96a34;
    --fg-forest: #6cb98c;
    --fg-forest-soft: #1e2c22;
    --fg-warn: #e2793f;
    --fg-warn-soft: #2e2015;
    --fg-radius: 14px;
    --fg-radius-lg: 20px;
}

html, body, [class*="css"] { font-family: 'Manrope', -apple-system, sans-serif; }

.stApp, body { background: var(--fg-paper); color: var(--fg-ink); }

#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.6rem; max-width: 1180px; }

h1, h2, h3 { font-family: 'Fraunces', Georgia, serif; color: var(--fg-ink); letter-spacing: -0.01em; }

/* ---- top nav ---- */
.fg-nav {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    border-bottom: 1px solid var(--fg-border);
    padding-bottom: 0.9rem;
    margin-bottom: 1.6rem;
}
.fg-wordmark {
    font-family: 'Fraunces', Georgia, serif;
    font-weight: 700;
    font-size: 1.5rem;
    color: var(--fg-ink);
    text-decoration: none;
    letter-spacing: -0.02em;
}
.fg-wordmark span { color: var(--fg-rust); }
.fg-nav-tag {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--fg-ink-soft);
    font-weight: 600;
}

/* ---- page header ---- */
.fg-kicker {
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 700;
    color: var(--fg-rust);
    margin-bottom: 0.3rem;
}
.fg-page-title {
    font-family: 'Fraunces', Georgia, serif;
    font-size: 2.1rem;
    font-weight: 600;
    color: var(--fg-ink);
    margin-bottom: 0.35rem;
    line-height: 1.15;
}
.fg-page-sub {
    font-size: 1rem;
    color: var(--fg-ink-soft);
    max-width: 640px;
    line-height: 1.6;
    margin-bottom: 1.4rem;
}

/* ---- generic surfaces ---- */
.fg-card {
    background: var(--fg-card);
    border: 1px solid var(--fg-border);
    border-radius: var(--fg-radius);
    padding: 1.1rem 1.25rem;
    margin-bottom: 0.9rem;
}
.fg-card-title { font-weight: 700; color: var(--fg-ink); margin-bottom: 0.25rem; font-size: 1.02rem; }
.fg-card-meta { color: var(--fg-ink-soft); font-size: 0.9rem; line-height: 1.6; }

.fg-pill {
    display: inline-block;
    background: var(--fg-forest-soft);
    color: var(--fg-forest);
    border-radius: 999px;
    padding: 0.3rem 0.75rem;
    margin: 0.15rem 0.35rem 0.15rem 0;
    font-size: 0.8rem;
    font-weight: 700;
}
.fg-pill.warn { background: var(--fg-warn-soft); color: var(--fg-warn); }
.fg-pill.neutral { background: var(--fg-border); color: var(--fg-ink-soft); }

.fg-state {
    border: 1px dashed var(--fg-border);
    border-radius: var(--fg-radius);
    padding: 1.4rem;
    text-align: left;
    color: var(--fg-ink-soft);
    background: var(--fg-card);
}
.fg-state.error { border-color: var(--fg-rust-dark); background: var(--fg-warn-soft); color: var(--fg-warn); }
.fg-state-title { font-weight: 700; color: var(--fg-ink); margin-bottom: 0.25rem; }

/* ---- dashboard grid ---- */
.fg-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 1.6rem; }
@media (max-width: 1100px) { .fg-grid { grid-template-columns: repeat(2, 1fr); } }
.fg-tile {
    background: var(--fg-card);
    border: 1px solid var(--fg-border);
    border-radius: var(--fg-radius-lg);
    padding: 1.3rem 1.3rem 1rem;
    display: flex;
    flex-direction: column;
    gap: 0.55rem;
    min-height: 168px;
}
.fg-tile-title { font-weight: 700; font-size: 1.05rem; color: var(--fg-ink); }
.fg-tile-desc { font-size: 0.87rem; color: var(--fg-ink-soft); line-height: 1.5; flex-grow: 1; }

/* ---- daily value bars ---- */
.fg-dv-row { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.5rem; }
.fg-dv-label { width: 88px; font-size: 0.83rem; font-weight: 700; color: var(--fg-ink-soft); }
.fg-dv-track { flex: 1; height: 9px; border-radius: 999px; background: var(--fg-border); overflow: hidden; }
.fg-dv-fill { height: 100%; border-radius: 999px; background: var(--fg-forest); }
.fg-dv-fill.over { background: var(--fg-warn); }
.fg-dv-value { width: 150px; text-align: right; font-size: 0.82rem; color: var(--fg-ink-soft); font-weight: 700; }

/* Streamlit widget polish */
div[data-testid="stButton"] button, div[data-testid="stFormSubmitButton"] button {
    border-radius: 10px;
    font-weight: 700;
    border: 1px solid var(--fg-rust);
    color: var(--fg-ink);
    background: var(--fg-card);
}
div[data-testid="stPageLink"] a {
    border-radius: 10px;
    border: 1px solid var(--fg-border);
    font-weight: 600;
    color: var(--fg-ink);
}
div[data-testid="stPageLink"] a p { color: var(--fg-ink); }
</style>
"""


def apply_theme(page_title, show_nav=True):
    icon = _BLANK_FAVICON if os.path.exists(_BLANK_FAVICON) else None
    st.set_page_config(page_title=f"{page_title} - FoodGPT", page_icon=icon, layout="wide")
    st.markdown(_CSS, unsafe_allow_html=True)
    if show_nav:
        _top_nav()


def _top_nav():
    st.markdown(
        f"""
        <div class="fg-nav">
            <div class="fg-wordmark">Food<span>GPT</span></div>
            <div class="fg-nav-tag">Bangladeshi and international food data</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("support/pages/Dashboard.py", label="Dashboard")
    cols = st.columns(4)
    for index, feature in enumerate(FEATURES):
        with cols[index % 4]:
            st.page_link(feature["page"], label=feature["title"])
    st.write("")


def page_header(kicker, title, subtitle):
    st.markdown(
        f"""
        <div class="fg-kicker">{kicker}</div>
        <div class="fg-page-title">{title}</div>
        <div class="fg-page-sub">{subtitle}</div>
        """,
        unsafe_allow_html=True,
    )


def pill(text, kind="default"):
    css = "fg-pill" if kind == "default" else f"fg-pill {kind}"
    return f"<span class='{css}'>{text}</span>"


def allergen_pills_html(allergens):
    if not allergens:
        return pill("No common allergens detected")
    parts = []
    for name in sorted(allergens, key=lambda item: (allergens[item] != "contains", item)):
        level = allergens[name]
        kind = "warn" if level == "contains" else "neutral"
        label = name if level == "contains" else name + "?"
        parts.append(f"<span class='fg-pill {kind}' title='{level}'>{label}</span>")
    return "".join(parts)


def diet_pills_html(row):
    labels = []
    if bool(row.get("vegan")):
        labels.append("Vegan")
    elif bool(row.get("vegetarian")):
        labels.append("Vegetarian")
    if bool(row.get("gluten_free")):
        labels.append("Gluten free")
    if bool(row.get("diabetic_friendly")):
        labels.append("Diabetic friendly")
    if bool(row.get("heart_healthy")):
        labels.append("Heart healthy")
    return "".join(pill(label) for label in labels)


def daily_value_html(scaled, percents, units, title="Share of a 2000 kcal reference day"):
    rows_html = []
    for key, percent in percents.items():
        width = max(2.0, min(percent, 100.0))
        css_class = "fg-dv-fill over" if percent > 100 else "fg-dv-fill"
        rows_html.append(
            f"<div class='fg-dv-row'><div class='fg-dv-label'>{key.title()}</div>"
            f"<div class='fg-dv-track'><div class='{css_class}' style='width:{width:.1f}%'></div></div>"
            f"<div class='fg-dv-value'>{scaled[key]:.1f} {units[key]} · {percent:.0f}%</div></div>"
        )
    return f"<div class='fg-card'><div class='fg-card-title'>{title}</div>" + "".join(rows_html) + "</div>"


def empty_state(title, body):
    st.markdown(
        f"<div class='fg-state'><div class='fg-state-title'>{title}</div>{body}</div>",
        unsafe_allow_html=True,
    )


def error_state(title, body):
    st.markdown(
        f"<div class='fg-state error'><div class='fg-state-title'>{title}</div>{body}</div>",
        unsafe_allow_html=True,
    )
