import os

import streamlit as st

from support.core.theme import FEATURES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_PAGE = os.path.join("support", "pages", "Dashboard.py")


def _page_slug(page_path):
    return os.path.splitext(os.path.basename(page_path))[0]


pages = [st.Page(DASHBOARD_PAGE, title="Dashboard", default=True)]
pages += [
    st.Page(feature["page"], title=feature["title"], url_path=_page_slug(feature["page"]))
    for feature in FEATURES
]

router = st.navigation(pages, position="hidden")
router.run()
