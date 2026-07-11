# FoodGPT

A simple dataset-driven food assistant built with Streamlit.

## Features

- Nutrition analysis for foods in the dataset
- Health recommendations for diabetes, hypertension, heart health, weight loss, and weight gain
- Recipe generation using dataset ingredients
- Smart meal planning based on calorie goals

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install streamlit pandas
streamlit run app.py
```

## Dataset file

Place your dataset file in one of these locations:

- `bd_food_nutrition_dataset.csv`
- `data/bd_food_nutrition_dataset.csv`

The app will load the dataset from the repository, so make sure the file is committed before deploying.

## Deployment

This project is ready to deploy as a Streamlit app using Streamlit Community Cloud or any platform that supports Python apps.

1. Add `bd_food_nutrition_dataset.csv` to the repository.
2. Push the repository to GitHub.
3. Connect the GitHub repo to Streamlit Cloud.
4. Set `app.py` as the entry point.
