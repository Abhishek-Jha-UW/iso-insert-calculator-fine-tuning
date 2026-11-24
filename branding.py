"""Shared TMS Carbide identity for Streamlit tools."""

from html import escape

import streamlit as st


def render_header(title, description):
    st.markdown(
        f"""
        <style>
        .tms-hero {{
            background: linear-gradient(115deg, #122c43, #174d72);
            padding: clamp(1.25rem, 3vw, 2.4rem);
            border-radius: 0.9rem;
            color: #fff;
            margin-bottom: 1.4rem;
        }}
        .tms-lockup {{display:flex; align-items:center; gap:.8rem; margin-bottom:1rem;}}
        .tms-mark {{
            display:inline-grid; place-items:center; min-width:3.4rem; height:2.7rem;
            background:#d9f1ff; color:#15324b; font-weight:800; border-radius:.45rem;
        }}
        .tms-team {{font-weight:700; line-height:1.25;}}
        .tms-company {{font-size:.82rem; color:#d5e9f6;}}
        .tms-hero h1 {{color:#fff; padding:0; font-size:clamp(1.8rem, 4vw, 2.8rem);}}
        .tms-hero p {{color:#e0eff8; margin:.45rem 0 0;}}
        </style>
        <section class="tms-hero">
          <div class="tms-lockup">
            <span class="tms-mark" aria-hidden="true">TMS</span>
            <div><div class="tms-team">TMS Carbide Team</div>
              <div class="tms-company">Hyperion Materials &amp; Technologies</div></div>
          </div>
          <h1>{escape(title)}</h1>
          <p>{escape(description)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_credit():
    st.divider()
    st.caption(
        "Built for TMS Carbide by [Abhishek Jha](mailto:abhishek.jha@hyperionmt.com) "
        "· Product Analyst, Toolmaker Solutions"
    )
