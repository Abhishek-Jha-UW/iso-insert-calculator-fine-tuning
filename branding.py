"""Compact styling for the insert calculator."""

from html import escape

import streamlit as st

def render_header(title, description):
    st.markdown(
        f"""
        <style>
        [data-testid="stMain"] {{
            background-image: linear-gradient(165deg, rgba(0, 111, 176, .075), transparent 27rem);
        }}
        [data-testid="stMainBlockContainer"] {{padding-top: clamp(3.5rem, 5vw, 4.5rem);}}
        .insert-header {{
            display:flex; align-items:center; justify-content:space-between; gap:.75rem 1.5rem;
            flex-wrap:wrap; border-bottom:1px solid rgba(0, 104, 164, .23); padding-bottom:.75rem;
        }}
        .insert-header h1 {{padding:0; margin:0; font-size:clamp(1.45rem, 2.8vw, 2rem); line-height:1.15;}}
        .insert-header p {{margin:.2rem 0 0; font-size:.88rem; opacity:.84;}}
        [data-testid="stMetric"] {{
            padding:.5rem .75rem; border:1px solid rgba(0, 104, 164, .18);
            border-radius:.45rem; background:rgba(0, 111, 176, .035);
        }}
        </style>
        <header class="insert-header">
          <div>
            <h1>{escape(title)}</h1>
            <p>{escape(description)}</p>
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )
