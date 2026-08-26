import base64
import os

import streamlit as st

from support.core.data import get_prepared_dataset
from support.core.theme import FEATURES, apply_theme, error_state

apply_theme("Dashboard", show_nav=False)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERO_IMAGE_CANDIDATES = [
    os.path.join(BASE_DIR, "assets", f"hero_food.{ext}") for ext in ("jpg", "jpeg", "png", "webp")
]


def _hero_background_style():
    for path in HERO_IMAGE_CANDIDATES:
        if os.path.exists(path):
            ext = path.rsplit(".", 1)[-1]
            mime = "jpeg" if ext == "jpg" else ext
            with open(path, "rb") as file:
                data = base64.b64encode(file.read()).decode()
            return f"background-image:url('data:image/{mime};base64,{data}');background-size:cover;background-position:center;"
    return "background:radial-gradient(circle at 35% 30%, #2b241a, #0f0d0a 70%);"


def _page_slug(page_path):
    return os.path.splitext(os.path.basename(page_path))[0]


st.markdown(
    """
    <style>
    html, body { margin: 0 !important; padding: 0 !important; overflow: hidden !important; }
    [data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {
        overflow: hidden !important;
    }
    [data-testid="stDecoration"] { display: none !important; }
    .block-container, [data-testid="stMainBlockContainer"] {
        max-width: 100% !important;
        padding: 0 !important;
    }
    .fg-hero {
        position: relative;
        background: #14110c;
        padding: 3rem 4rem;
        display: grid;
        grid-template-columns: 1.15fr 0.85fr;
        gap: 2.5rem;
        height: 100vh;
        overflow: hidden;
        box-sizing: border-box;
    }
    @media (max-width: 1000px) {
        .fg-hero { grid-template-columns: 1fr; height: auto; }
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp { overflow: auto !important; }
    }
    .fg-hero-col { display: flex; flex-direction: column; justify-content: space-between; z-index: 1; }
    .fg-hero-top { display: flex; align-items: center; }
    .fg-hero-word { font-family: 'Fraunces', Georgia, serif; font-weight: 700; font-size: 1.4rem; color: #f7f2e7; }
    .fg-hero-word span { color: #e2793f; }
    .fg-hero-title {
        font-family: 'Manrope', -apple-system, sans-serif;
        font-weight: 800;
        font-size: 4.2rem;
        line-height: 1.05;
        color: #faf6ef;
        letter-spacing: -0.02em;
        margin: 2rem 0 1.1rem;
    }
    .fg-hero-sub { color: #c9beac; font-size: 1.1rem; line-height: 1.7; max-width: 520px; }
    .fg-hero-bottom { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin-top: 2rem; }
    .fg-hero-nav { display: flex; flex-wrap: wrap; gap: 0.6rem; max-width: 540px; }
    .fg-hero-btn {
        border: 1px solid rgba(247, 242, 231, 0.22);
        background: rgba(247, 242, 231, 0.05);
        color: #f2ece0;
        padding: 0.5rem 1rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 600;
        text-decoration: none;
        white-space: nowrap;
    }
    .fg-hero-btn:hover { background: rgba(247, 242, 231, 0.14); border-color: rgba(247, 242, 231, 0.4); }
    .fg-hero-stat { color: #9b8f7b; font-size: 0.85rem; font-weight: 600; text-align: right; white-space: nowrap; }
    .fg-hero-right { position: relative; border-radius: 20px; overflow: hidden; }
    .fg-hero-right::after {
        content: ""; position: absolute; inset: 0;
        background: linear-gradient(180deg, rgba(20,17,12,0) 55%, rgba(20,17,12,0.55));
    }
    </style>
    """,
    unsafe_allow_html=True,
)

dataset = get_prepared_dataset()

if dataset.empty:
    error_state(
        "Dataset not found",
        "Add <code>bd_food_nutrition_dataset.csv</code> to the <code>data/</code> folder, then reload this page.",
    )
    st.stop()

nav_buttons_html = "".join(
    f'<a class="fg-hero-btn" href="/{_page_slug(feature["page"])}" target="_self">{feature["title"]}</a>'
    for feature in FEATURES
)

st.markdown(
    f"""
    <div class="fg-hero">
        <div class="fg-hero-col">
            <div class="fg-hero-top">
                <div class="fg-hero-word">Food<span>GPT</span></div>
            </div>
            <div>
                <div class="fg-hero-title">Eat Smarter,<br>Not Harder.</div>
                <div class="fg-hero-sub">One food dataset, eight tools: nutrition lookups, health guidance,
                recipes, meal plans, allergen checks, comparisons, and a chat assistant that knows your food
                inside out.</div>
            </div>
            <div class="fg-hero-bottom">
                <div class="fg-hero-nav">{nav_buttons_html}</div>
                <div class="fg-hero-stat">{len(dataset):,} foods<br>{dataset['category'].nunique()} categories</div>
            </div>
        </div>
        <div class="fg-hero-right" style="{_hero_background_style()}"></div>
    </div>
    """,
    unsafe_allow_html=True,
)
