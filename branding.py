"""Shared TMS Carbide identity for Streamlit tools."""

from base64 import b64encode
from html import escape
from pathlib import Path

import streamlit as st

LOGO = Path(__file__).parent / "assets" / "hyperion-logo.png"


def render_header(title, description):
    logo = b64encode(LOGO.read_bytes()).decode("ascii")
    st.markdown(
        f"""
        <style>
        [data-testid="stMain"] {{
            background-image: linear-gradient(165deg, rgba(0, 111, 176, .075), transparent 27rem);
        }}
        [data-testid="stMainBlockContainer"] {{padding-top: clamp(3.5rem, 5vw, 4.5rem);}}
        .tms-header {{
            display:flex; align-items:center; justify-content:space-between; gap:.75rem 1.5rem;
            flex-wrap:wrap; border-bottom:1px solid rgba(0, 104, 164, .23); padding-bottom:.75rem;
        }}
        .tms-header h1 {{padding:0; margin:0; font-size:clamp(1.45rem, 2.8vw, 2rem); line-height:1.15;}}
        .tms-header p {{margin:.2rem 0 0; font-size:.88rem; opacity:.84;}}
        .tms-brand {{display:flex; align-items:center; gap:.75rem; font-size:.83rem; font-weight:650;}}
        .tms-brand img {{display:block; width:150px; height:auto; border-radius:.3rem;}}
        [data-testid="stMetric"] {{
            padding:.5rem .75rem; border:1px solid rgba(0, 104, 164, .18);
            border-radius:.45rem; background:rgba(0, 111, 176, .035);
        }}
        </style>
        <header class="tms-header">
          <div>
            <h1>{escape(title)}</h1>
            <p>{escape(description)}</p>
          </div>
          <div class="tms-brand">
            <span>TMS Carbide Team</span>
            <img src="data:image/png;base64,{logo}" alt="Hyperion Materials &amp; Technologies">
          </div>
        </header>
        """,
        unsafe_allow_html=True,
    )


def render_credit():
    st.divider()
    st.caption(
        "Built for TMS Carbide by [AB](mailto:abhishek.jha@hyperionmt.com) "
        "· Product Analyst, Toolmaker Solutions"
    )
