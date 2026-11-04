import streamlit as st

def apply_theme():
    theme = st.session_state.get("theme", "System")

    if theme == "Dark":
        background = "#0B1120"
        sidebar = "#111827"
        card = "#172033"
        text = "#F8FAFC"
        secondary = "#94A3B8"
        border = "#263449"
        input_bg = "#1E293B"

    else:
        background = "#F1F5F9"
        sidebar = "#FFFFFF"
        card = "#FFFFFF"
        text = "#0F172A"
        secondary = "#64748B"
        border = "#E2E8F0"
        input_bg = "#F8FAFC"

    st.markdown(
        f"""
        <style>
        /* MAIN APPLICATION */

        .stApp {{
            background-color: {background};
            color: {text};
        }}
        [data-testid="stAppViewContainer"] {{
            background-color: {background};
        }}
        [data-testid="stHeader"] {{
            background-color: transparent;
        }}

        /* SIDEBAR */

        [data-testid="stSidebar"] {{
            background-color: {sidebar};
            border-right: 1px solid {border};
        }}
        [data-testid="stSidebar"] * {{
            color: {text};
        }}

        /* MAIN CONTENT */

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}

        /* DASHBOARD LAYOUT POLISH */

        [data-testid="stVerticalBlock"] {{
            gap: 1rem;
        }}
        [data-testid="stHorizontalBlock"] {{
            gap: 1.2rem;
        }}
        [data-testid="stPlotlyChart"] {{
            margin-top: 8px;
            margin-bottom: 12px;
        }}
        [data-testid="stDataFrame"] {{
            margin-top: 8px;
            margin-bottom: 14px;
        }}

        /* CONTAINER BORDER AND SPACING */

        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 12px;
        }}

        /* RESPONSIVE CONTENT */

        @media (max-width: 768px) {{
            .block-container {{
                padding-left: 1rem;
                padding-right: 1rem;
            }}
            .main-header {{
                font-size: 24px;
            }}
            .kpi-value {{
                font-size: 23px;
            }}
            .section-header h3 {{
                font-size: 17px;
            }}
        }}

        /* HEADINGS */

        h1, h2, h3 {{
            color: {text} !important;
        }}
        p, label {{
            color: {text};
        }}

        /* HEADER */

        .main-header {{
            font-size: 30px;
            font-weight: 800;
            color: {text};
            letter-spacing: -0.8px;
        }}
        .main-subtitle {{
            font-size: 14px;
            color: {secondary};
            margin-top: -10px;
        }}

        /* BRAND */

        .brand-title {{
            font-size: 25px;
            font-weight: 850;
            color: #38BDF8;
            letter-spacing: 0.5px;
            margin-bottom: 3px;
        }}
        .brand-subtitle {{
            font-size: 10px;
            font-weight: 600;
            color: {secondary};
            letter-spacing: 1.8px;
        }}

        /* KPI CARDS */

        .kpi-card {{
            background: {card};
            border: 1px solid {border};
            border-radius: 14px;
            padding: 20px;
            min-height: 125px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            position: relative;
            overflow: hidden;
            transition: transform 0.25s ease,
                        border-color 0.25s ease,
                        box-shadow 0.25s ease;
        }}
        .kpi-card:hover {{
            transform: translateY(-4px);
            border-color: #38BDF8;
            box-shadow: 0 8px 22px rgba(56, 189, 248, 0.12);
        }}
        .kpi-label {{
            color: {secondary};
            font-size: 13px;
            font-weight: 500;
            letter-spacing: 0.3px;
            text-transform: uppercase;
        }}
        .kpi-value {{
            color: {text};
            font-size: 28px;
            font-weight: 800;
            margin-top: 10px;
            line-height: 1.3;
            word-break: break-word;
        }}
        .kpi-caption {{
            color: {secondary};
            font-size: 11px;
            margin-top: 5px;
            line-height: 1.5;
        }}

        /* SECTION HEADERS */

        .section-header {{
            margin-top: 18px;
            margin-bottom: 18px;
            padding: 12px 16px;
            border-left: 4px solid #38BDF8;
            border-radius: 8px;
            background-color: {card};
        }}
        .section-header h3 {{
            font-size: 20px;
            font-weight: 750;
            margin: 0;
            color: {text} !important;
        }}
        .section-header p {{
            font-size: 12px;
            margin: 5px 0 0 0;
            color: {secondary};
        }}

        /* SIDEBAR NAVIGATION BUTTONS */

        [data-testid="stSidebar"] .stButton button {{
            width: 100%;
            text-align: left;
            border-radius: 9px;
            border: 1px solid {border};
            background: {card};
            color: {text};
            padding: 11px 13px;
            min-height: 42px;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        [data-testid="stSidebar"] .stButton button:hover {{
            border-color: #38BDF8;
            background: {input_bg};
            color: #38BDF8;
            transform: translateX(3px);
        }}
        [data-testid="stSidebar"] .stButton button:focus {{
            border-color: #38BDF8;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.15);
        }}

        /* SIDEBAR BRANDING */

        .brand-title {{
            font-size: 25px;
            font-weight: 850;
            letter-spacing: 0.5px;
            color: #38BDF8;
            margin-bottom: 3px;
        }}
        .brand-subtitle {{
            font-size: 10px;
            font-weight: 600;
            color: {secondary};
            letter-spacing: 1.8px;
        }}

        /* INPUTS */

        .stTextInput input,
        .stSelectbox div[data-baseweb="select"] {{
            background-color: {input_bg};
            color: {text};
            border-radius: 8px;
        }}

        /* DIVIDER */

        hr {{
            border-color: {border};
        }}

        /* DATAFRAME */

        [data-testid="stDataFrame"] {{
            border: 1px solid {border};
            border-radius: 10px;
        }}

        /* CHART CONTAINER */

        [data-testid="stPlotlyChart"] {{
            background: {card};
            border-radius: 12px;
            padding: 5px;
        }}

        /* SECTION HEADERS */

        .section-header {{
            margin-top: 18px;
            margin-bottom: 18px;
            padding: 12px 16px;
            border-left: 4px solid #38BDF8;
            border-radius: 8px;
            background-color: {card};
        }}
        .section-header h3 {{
            font-size: 20px;
            font-weight: 750;
            margin: 0;
            color: {text} !important;
        }}
        .section-header p {{
            font-size: 12px;
            margin: 5px 0 0 0;
            color: {secondary};
        }}

        /* DASHBOARD FOOTER */

        .dashboard-footer {{
            color: {secondary};
            font-size: 12px;
            text-align: center;
            padding: 22px 12px;
            margin-top: 25px;
            border-top: 1px solid {border};
            line-height: 1.8;
            letter-spacing: 0.3px;
        }}
        .dashboard-footer strong {{
            color: {text};
            font-weight: 700;
        }}

        
        /* =========================================
        GLOBAL DATAFRAME STYLING
        ========================================= */

        /* DATAFRAME CONTAINER */
        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"] {{
            background-color: {card} !important;
            border: 1px solid {border} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }}

        /* DATAFRAME TOOLBAR */
        [data-testid="stDataFrame"] [data-testid="stElementToolbar"],
        [data-testid="stDataEditor"] [data-testid="stElementToolbar"] {{
            background-color: {card} !important;
            border-color: {border} !important;
        }}

        /* DATAFRAME SURROUNDING AREA */
        [data-testid="stDataFrame"] > div,
        [data-testid="stDataEditor"] > div {{
            background-color: {card} !important;
            border-radius: 12px !important;
        }}

        /* =========================================
        GLOBAL EXPANDER STYLING
        ========================================= */

        /* EXPANDER MAIN CONTAINER */
        [data-testid="stExpander"] {{
            background-color: {card} !important;
            border: 1px solid {border} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            margin-bottom: 10px;
        }}

        /* EXPANDER HEADER */
        [data-testid="stExpander"] summary {{
            background-color: {card} !important;
            color: {text} !important;
            padding: 12px 16px !important;
            font-weight: 600 !important;
        }}

        /* EXPANDER HEADER HOVER */
        [data-testid="stExpander"] summary:hover {{
            background-color: {input_bg} !important;
        }}

        /* EXPANDER HEADER TEXT */
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span {{
            color: {text} !important;
        }}

        /* EXPANDER CONTENT */
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
            background-color: {card} !important;
            border-top: 1px solid {border} !important;
            padding: 14px 16px !important;
        }}

        /* EXPANDER CONTENT TEXT */
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] p,
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] label {{
            color: {text} !important;
        }}

        /* GLOBAL THEME-AWARE CONTROLS */

        /* ALL BUTTONS */
        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {{
            background-color: {card};
            color: {text};
            border: 1px solid {border};
            border-radius: 9px;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {{
            background-color: {input_bg};
            color: #38BDF8;
            border-color: #38BDF8;
        }}

        /* TEXT INPUTS AND TEXTAREA */
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {{
            background-color: {input_bg} !important;
            color: {text} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
        }}

        /* SELECTBOX AND MULTISELECT */
        [data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            color: {text} !important;
            border-color: {border} !important;
        }}

        /* DROPDOWN OPTIONS */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [role="listbox"] {{
            background-color: {card} !important;
        }}
        [role="option"] {{
            background-color: {card} !important;
            color: {text} !important;
        }}
        [role="option"]:hover {{
            background-color: {input_bg} !important;
        }}

        /* TABS */
        .stTabs [data-baseweb="tab"] {{
            color: {secondary} !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: #38BDF8 !important;
        }}

        /* RADIO AND CHECKBOX */
        .stRadio label,
        .stCheckbox label {{
            color: {text} !important;
        }}

        /* PLACEHOLDERS */
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stNumberInput input::placeholder {{
            color: {secondary} !important;
        }}

        /* HIDE DEFAULT STREAMLIT FOOTER */

        footer {{
            visibility: hidden;
        }}

        /* =========================================
        FIXED THEME-AWARE STREAMLIT CONTROLS
        ========================================= */

        /* Selectbox and Multiselect main control */
        [data-baseweb="select"] > div {{
            background-color: INPUT_BG !important;
            border: 1px solid BORDER_COLOR !important;
            border-radius: 8px !important;
            color: TEXT_COLOR !important;
        }}

        /* Selected value */
        [data-baseweb="select"] span,
        [data-baseweb="select"] input {{
            color: TEXT_COLOR !important;
            -webkit-text-fill-color: TEXT_COLOR !important;
        }}

        /* Dropdown arrow and icons */
        [data-baseweb="select"] svg {{
            fill: TEXT_COLOR !important;
            color: TEXT_COLOR !important;
        }}

        /* Dropdown menu */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        [data-baseweb="popover"] > div {{
            background-color: CARD_BG !important;
            border: 1px solid BORDER_COLOR !important;
        }}

        /* Dropdown options */
        [role="listbox"] {{
            background-color: CARD_BG !important;
        }}
        [role="option"] {{
            background-color: CARD_BG !important;
            color: TEXT_COLOR !important;
        }}

        /* Hover and selected option */
        [role="option"]:hover,
        [role="option"][aria-selected="true"] {{
            background-color: INPUT_BG !important;
            color: TEXT_COLOR !important;
        }}

        /* Text, number and textarea */
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {{
            background-color: INPUT_BG !important;
            color: TEXT_COLOR !important;
            border-color: BORDER_COLOR !important;
        }}

        /* Labels */
        [data-testid="stWidgetLabel"] p {{
            color: TEXT_COLOR !important;
        }}

        /* Buttons */
        .stButton button,
        .stDownloadButton button {{
            background-color: CARD_BG !important;
            color: TEXT_COLOR !important;
            border: 1px solid BORDER_COLOR !important;
        }}

        /* Focus state */
        [data-baseweb="select"] > div:focus-within {{
            border-color: #38BDF8 !important;
            box-shadow: 0 0 0 1px #38BDF8 !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def render_kpi(label, value, caption=""):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">
                {label}
            </div>
            <div class="kpi-value">
                {value}
            </div>
            <div class="kpi-caption">
                {caption}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_section_header(title, subtitle=None, icon=None):
    heading = f"{icon} {title}" if icon else title
    st.markdown(
        f"""
        <div class="section-header">
            <h3>{heading}</h3>
            {f'<p>{subtitle}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True
    )


def apply_chart_theme(fig):
    """
    Apply consistent Light/Dark theme to Plotly charts.
    """
    theme = st.session_state.get("theme", "Dark")

    if theme == "Light":
        background = "#FFFFFF"
        text_color = "#0F172A"
        grid_color = "#E2E8F0"
        axis_color = "#334155"
    else:
        background = "#0B1120"
        text_color = "#F8FAFC"
        grid_color = "#263449"
        axis_color = "#CBD5E1"

    fig.update_layout(
        template="plotly_white" if theme == "Light" else "plotly_dark",
        paper_bgcolor=background,
        plot_bgcolor=background,
        font=dict(
            color=text_color,
            family="Arial"
        ),
        title_font=dict(
            color=text_color
        ),
        legend=dict(
            font=dict(color=text_color),
            title_font=dict(color=text_color)
        ),
        xaxis=dict(
            color=axis_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            gridcolor=grid_color,
            linecolor=grid_color,
            zerolinecolor=grid_color
        ),
        yaxis=dict(
            color=axis_color,
            title_font=dict(color=text_color),
            tickfont=dict(color=text_color),
            gridcolor=grid_color,
            linecolor=grid_color,
            zerolinecolor=grid_color
        )
    )
    return fig

def render_dataframe(df, **kwargs):
    """
    Render a DataFrame with the active Light/Dark theme.
    """
    theme = st.session_state.get("theme", "Dark")
    if theme == "Light":
        background = "#FFFFFF"
        text_color = "#0F172A"
        header_background = "#E2E8F0"
        border_color = "#CBD5E1"
    else:
        background = "#172033"
        text_color = "#F8FAFC"
        header_background = "#1E293B"
        border_color = "#334155"
    styled_df = (
        df.style
        .set_properties(
            **{
                "background-color": background,
                "color": text_color,
                "border-color": border_color,
            }
        )
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", header_background),
                    ("color", text_color),
                    ("border-color", border_color),
                    ("font-weight", "bold"),
                ],
            },
            {
                "selector": "td",
                "props": [
                    ("border-color", border_color),
                ],
            },
        ])
    )
    kwargs.setdefault("use_container_width", True)
    st.dataframe(
        styled_df,
        **kwargs
    )
