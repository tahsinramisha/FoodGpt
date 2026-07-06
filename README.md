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

## Deployment

This project is ready to deploy as a Streamlit app using GitHub Pages + Streamlit sharing, or any platform that supports Python apps.

1. Push the repository to GitHub.
2. Connect the GitHub repo to Streamlit Cloud.
3. Set `app.py` as the entry point.
