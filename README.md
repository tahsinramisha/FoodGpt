# FoodGPT

FoodGPT is a Streamlit dashboard built around a single food nutrition dataset covering Bangladeshi
and international dishes. Instead of one big form, it's split into eight focused tools (nutrition
lookup, health guidance, recipes, meal planning, menu matching, allergen filtering, food
comparison, and a chat assistant) that all read from the same cleaned dataset, so a number you see
in one tool always matches what you'd see in another.

The project's goal is to make a raw CSV of food data actually useful day to day: "is this safe for
me to eat", "what should I cook tonight", "what does a day of meals look like for my calorie
target", answered from real numbers instead of guesses.

## The dataset

`data/bd_food_nutrition_dataset.csv` has one row per food, with:

- Identity: `food_id`, `food_name`, `category`, `cuisine`, `meal_type`
- Nutrition per listed serving: `serving_size_g`, `calories_kcal`, `protein_g`, `carbs_g`,
  `fat_g`, `fiber_g`, `sugar_g`, `sodium_mg`
- Dietary flags: `vegetarian`, `vegan`, `gluten_free`, `diabetic_friendly`, `high_protein`,
  `low_fat`, `heart_healthy`, `weight_loss_friendly`
- Free text: `main_ingredients`, `tags`

`support/core/data.py` is the only place that reads and cleans this file. It normalizes column
names, coerces nutrient columns to numbers, fills in missing dietary flags, and estimates common
allergens (dairy, egg, fish, shellfish, gluten, peanut, tree nuts, soy, sesame, mustard) from each
food's name, ingredients, tags, and category using keyword rules. Every other module works off of
that one cleaned table, so there's no duplicated parsing logic anywhere else in the app.

## Features

- **Dashboard**: a full-screen hero landing page linking to every feature below.
- **Nutrition Analysis**: look up a food and see its full nutrient breakdown, then rescale every
  number to any portion size.
- **Health Recommendations**: foods matched to a condition or goal such as diabetes, hypertension,
  heart disease, weight loss, or weight gain.
- **Recipe Generator**: turn any dataset food into step by step cooking instructions, with
  ingredient amounts and nutrition scaled to your batch size.
- **Meal Planner**: a full day of meals sized to hit a calorie target, built around a health goal.
- **Menu Analyzer**: paste a menu or grocery list and match each line to the closest dataset food.
- **Diet & Allergen Filter**: set allergy and dietary rules once, then browse only the foods that
  fit, with allergens estimated from each food's name, ingredients, tags, and category.
- **Compare Foods**: two foods side by side with a nutrient by nutrient verdict on which wins.
- **Chat Assistant**: a normal back-and-forth chat, not a form, for asking about the data in plain
  language (see below for how it decides when to answer itself versus call an LLM).

## How the Chat Assistant works

The chat is a two-stage pipeline, in `support/core/chatbot.py`:

1. **Rule-based first.** Every message is checked against a small set of regex intents:
   calories lookups, "is X good for [condition]", recipe requests, meal plan requests, and
   "what foods are [vegan/gluten-free/high-protein/...]". If one matches and resolves to a real
   dataset row, the answer comes straight from the cleaned dataframe: instant, deterministic, and
   impossible to hallucinate.
2. **Groq fallback for everything else.** If no rule matches, the app pulls a handful of dataset
   rows relevant to the message (simple keyword matching against food name, category, cuisine, and
   tags) and sends them to Groq as grounding context alongside the conversation history, so
   open-ended or multi-turn questions still get answered using this app's actual data rather than
   the model's general knowledge. If the Groq call fails (missing key, network issue, decommissioned
   model, etc.), the assistant falls back to a best-effort answer built from whatever dataset rows
   it did retrieve, with a plain-language note instead of crashing.

## Project layout

```
main.py                    Entry point: registers pages and hands off to the router
data/
  bd_food_nutrition_dataset.csv
support/
  core/
    data.py                  Dataset loading, cleaning, allergen and diet-filter logic
    nutrition.py              Nutrient scoring, portion scaling, recipes, meal planning
    theme.py                  Shared page config, styling, header, and navigation
    chatbot.py                Rule-based intent matching plus the Groq fallback
  pages/
    Dashboard.py               The hero landing page
    Nutrition_Analysis.py
    Health_Recommendations.py
    Recipe_Generator.py
    Meal_Planner.py
    Menu_Analyzer.py
    Diet_Allergen_Filter.py
    Compare_Foods.py
    Chat_Assistant.py
others/                    Presentation, report, and demo video deliverables 
assets/                    Favicon and hero image
.streamlit/
  config.toml                App theme
  secrets.toml                GROQ_API_KEY (not committed, see below)
requirements.txt
```

Every page under `support/pages/` only imports what it needs from `support/core/`, calls the
shared `apply_theme()` for a consistent look, and can be read on its own without needing the rest
of the app for context.

## Tech stack

- **Streamlit** for the UI and multi-page routing (`st.navigation`/`st.Page`, driven from `main.py`)
- **pandas** for loading and cleaning the dataset
- **Groq** (`openai/gpt-oss-20b`) as the LLM backend for the chat assistant's fallback path

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

The app opens at `http://localhost:8501`. Every feature is reachable from a button on the
dashboard's hero, and from the top nav bar on every other page.

## Groq API key

The Chat Assistant's fallback for open-ended questions calls the Groq API. Set your key in
`.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-key-here"
```

or as an environment variable named `GROQ_API_KEY`. If no key is set, the chat still works: it
just falls back to a best-effort, dataset-only answer instead of calling Groq. `secrets.toml` is
git-ignored, so the key never gets committed.