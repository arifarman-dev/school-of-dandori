import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="School of Dandori", page_icon="🌘")
st.title("🌘 School of Dandori — Course Finder")
st.write("Find your next whimsical adventure")

def load_data():
    if not os.path.exists("XXX.csv"):
        return pd.DataFrame()
    return pd.read_csv("XXX.csv")

df = load_data()