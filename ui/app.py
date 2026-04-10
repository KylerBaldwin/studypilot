import streamlit as st
from auth.google_oauth import exchange_code, get_userinfo
from auth.session import set_user
import api.client as api

st.set_page_config(page_title="StudyPilot", page_icon="📚")

params = st.query_params

if "code" in params:
    code = params["code"]
    tokens = exchange_code(code)
    userinfo = get_userinfo(tokens["access_token"])
    api.store_refresh_token(tokens["refresh_token"], tokens["id_token"])
    set_user(
        id_token=tokens["id_token"],
        access_token=tokens["access_token"],
        email=userinfo["email"],
        name=userinfo["name"],
    )
    st.query_params.clear()

st.switch_page("pages/1_landing.py")
