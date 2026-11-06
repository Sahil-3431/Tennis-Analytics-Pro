import streamlit as st

def apply_theme():
    theme = st.session_state.get("color_theme","Ocean Blue")
    THEMES = {
        "Ocean Blue": {
            "background": "#0B1929",
            "sidebar": "#102438",
            "card": "#142D43",
            "text": "#F0F9FF",
            "secondary": "#94B8CC",
            "border": "#23445D",
            "input_bg": "#19364F",
            "accent": "#38BDF8",
            "glow": "rgba(56, 189, 248, 0.15)",
            "card_gradient": "linear-gradient(135deg, #142D43 0%, #193B55 100%)",
            "hover_shadow": "0 10px 28px rgba(56, 189, 248, 0.22)",
            "button_gradient": "linear-gradient(135deg, #0EA5E9 0%, #38BDF8 100%)"
        },
        "Pearl Light": {
            "background": "#F4F7FB",
            "sidebar": "#EAF0F7",
            "card": "#FFFFFF",
            "text": "#172B4D",
            "secondary": "#64748B",
            "border": "#DCE5F0",
            "input_bg": "#FFFFFF",
            "accent": "#2563EB",
            "glow": "rgba(37, 99, 235, 0.10)",
            "card_gradient": "linear-gradient(135deg, #FFFFFF 0%, #F1F6FD 100%)",
            "hover_shadow": "0 10px 28px rgba(37, 99, 235, 0.14)",
            "button_gradient": "linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)"
        },
        "Aurora Teal": {
            "background": "#263B40",
            "sidebar": "#30494D",
            "card": "#3B5558",
            "text": "#F0F7F5",
            "secondary": "#B5CECA",
            "border": "#587477",
            "input_bg": "#456164",
            "accent": "#65D6C2",
            "glow": "rgba(101, 214, 194, 0.16)",
            "card_gradient": "linear-gradient(135deg, #3B5558 0%, #49686A 100%)",
            "hover_shadow": "0 10px 28px rgba(101, 214, 194, 0.20)",
            "button_gradient": "linear-gradient(135deg, #238F83 0%, #65D6C2 100%)"
        },
        "Graphite Bronze": {
            "background": "#393A3A",
            "sidebar": "#454544",
            "card": "#52514E",
            "text": "#FAF7F0",
            "secondary": "#D0C4AD",
            "border": "#716B60",
            "input_bg": "#5D5A54",
            "accent": "#D6AE72",
            "glow": "rgba(214, 174, 114, 0.16)",
            "card_gradient": "linear-gradient(135deg, #52514E 0%, #625D53 100%)",
            "hover_shadow": "0 10px 28px rgba(214, 174, 114, 0.20)",
            "button_gradient": "linear-gradient(135deg, #A77A3E 0%, #D6AE72 100%)"
        },
        "Slate Mono": {
            "background": "#15191F",
            "sidebar": "#1D232B",
            "card": "#252D37",
            "text": "#F1F5F9",
            "secondary": "#A1AAB5",
            "border": "#3B4653",
            "input_bg": "#303A46",
            "accent": "#CBD5E1",
            "glow": "rgba(203, 213, 225, 0.12)",
            "card_gradient": "linear-gradient(135deg, #252D37 0%, #333F4C 100%)",
            "hover_shadow": "0 10px 28px rgba(203, 213, 225, 0.16)",
            "button_gradient": "linear-gradient(135deg, #475569 0%, #CBD5E1 100%)"
        }
    }
    colors = THEMES.get(theme,THEMES["Ocean Blue"])
    background = colors["background"]
    sidebar = colors["sidebar"]
    card = colors["card"]
    text = colors["text"]
    secondary = colors["secondary"]
    border = colors["border"]
    input_bg = colors["input_bg"]
    accent = colors["accent"]
    glow = colors["glow"]
    card_gradient = colors["card_gradient"]
    hover_shadow = colors["hover_shadow"]
    button_gradient = colors["button_gradient"]

    st.markdown(
        f"""
        <style>
        /* =========================================
        MAIN APPLICATION
        ========================================= */

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

        /* =========================================
        SIDEBAR
        ========================================= */

        [data-testid="stSidebar"] {{
            background-color: {sidebar};
            border-right: 1px solid {border};
        }}
        [data-testid="stSidebar"] * {{
            color: {text};
        }}

        /* SIDEBAR NAVIGATION BUTTONS */

        [data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            text-align: left;
            border-radius: 9px;
            border: 1px solid {border} !important;
            background: {card} !important;
            color: {text} !important;
            padding: 11px 13px;
            min-height: 42px;
            font-size: 13px;
            font-weight: 600;
            transition: all 0.25s ease !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            border-color: {accent} !important;
            background: {input_bg} !important;
            color: {accent} !important;
            transform: translateX(4px);
            box-shadow: 0 4px 15px {glow} !important;
        }}
        [data-testid="stSidebar"] .stButton > button:focus-visible {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 2px {glow} !important;
        }}

        /* =========================================
        MAIN CONTENT
        ========================================= */

        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }}
        [data-testid="stVerticalBlock"] {{
            gap: 1rem;
        }}
        [data-testid="stHorizontalBlock"] {{
            gap: 1.2rem;
        }}

        /* =========================================
        HEADINGS AND TEXT
        ========================================= */

        h1, h2, h3 {{
            color: {text} !important;
        }}
        p, label {{
            color: {text};
        }}
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

        /* =========================================
        BRANDING
        ========================================= */

        .brand-title {{
            font-size: 25px;
            font-weight: 850;
            color: {accent};
            letter-spacing: 0.5px;
            margin-bottom: 3px;
        }}
        .brand-subtitle {{
            font-size: 10px;
            font-weight: 600;
            color: {secondary};
            letter-spacing: 1.8px;
        }}

        /* =========================================
        SIDEBAR SECTION HEADERS
        ========================================= */

        .sidebar-section-title {{
            display: flex;
            align-items: center;
            gap: 9px;
            color: {accent};
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 1.2px;
            padding: 8px 2px;
            margin-bottom: 10px;
        }}
        .sidebar-section-title span {{
            font-size: 15px;
        }}

        /* SIDEBAR FILTER AND THEME CONTAINERS */

        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] {{
            background: {card_gradient};
            border: 1px solid {border};
            border-radius: 12px;
            padding: 12px;
            box-shadow: 0 4px 14px {glow};
        }}
        [data-testid="stSidebar"] [data-testid="stVerticalBlockBorderWrapper"] p {{
            color: {text} !important;
            font-weight: 600;
        }}

        /* =========================================
        PREMIUM KPI CARDS
        ========================================= */

        .kpi-card {{
            box-sizing: border-box;
            width: 100%;
            min-height: 145px;
            height: auto;
            padding: 18px 20px;
            margin-bottom: 0;
            position: relative;
            isolation: isolate;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 0;
            background:
                radial-gradient(
                    circle at 100% 0%,
                    {glow},
                    transparent 48%
                ),
                {card_gradient};
            border: 1px solid {border};
            border-radius: 17px;
            box-shadow:
                0 5px 16px rgba(0, 0, 0, 0.12),
                inset 0 1px 0 rgba(255, 255, 255, 0.035);
            transition:
                transform 0.28s ease,
                box-shadow 0.28s ease,
                border-color 0.28s ease;
        }}

        /* Accent strip */

        .kpi-card::before {{
            content: "";
            position: absolute;
            top: 18px;
            bottom: 18px;
            left: 0;
            width: 4px;
            background: {accent};
            border-radius: 0 5px 5px 0;
            box-shadow: 0 0 13px {glow};
        }}

        /* Decorative background glow */

        .kpi-card::after {{
            content: "";
            position: absolute;
            width: 125px;
            height: 125px;
            right: -48px;
            top: -55px;
            background: {accent};
            opacity: 0.055;
            border-radius: 50%;
            filter: blur(3px);
            pointer-events: none;
        }}

        .kpi-card:hover {{
            transform: translateY(-5px);
            border-color: {accent};
            box-shadow:
                {hover_shadow},
                0 8px 22px rgba(0, 0, 0, 0.12);
        }}

        /* KPI LABEL */

        .kpi-label {{
            position: relative;
            z-index: 1;
            color: {secondary};
            font-size: 11px;
            font-weight: 750;
            letter-spacing: 0.7px;
            line-height: 1.5;
            text-transform: uppercase;
        }}

        /* KPI VALUE */

        .kpi-value {{
            position: relative;
            z-index: 1;
            color: {text};
            font-size: 28px;
            font-weight: 850;
            letter-spacing: -1px;
            line-height: 1.2;
            margin-top: 9px;
            overflow-wrap: anywhere;
        }}

        /* KPI DESCRIPTION */

        .kpi-caption {{
            position: relative;
            z-index: 1;
            color: {secondary};
            font-size: 11px;
            font-weight: 500;
            line-height: 1.4;
            margin-top: 7px;
        }}

        /* RESPONSIVE KPI CARDS */

        @media (max-width: 768px) {{
            .kpi-card {{
                min-height: 145px;
                padding: 20px;
                margin-bottom: 14px;
            }}
            .kpi-value {{
                font-size: 27px;
            }}
            .kpi-label {{
                font-size: 11px;
            }}
            .kpi-caption {{
                font-size: 11px;
            }}
        }}

        /* =========================================
        SECTION HEADERS
        ========================================= */

        .section-header {{
            margin-top: 14px;
            margin-bottom: 12px;
            padding: 15px 20px;
            border-left: 4px solid {accent};
            border-radius: 8px;
            background: {card};
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

        /* =========================================
        CHART CONTAINERS
        ========================================= */

        [data-testid="stPlotlyChart"] {{
            background: {card};
            border-radius: 12px;
            padding: 5px;
            margin-top: 8px;
            margin-bottom: 12px;
        }}

        /* =========================================
        DATAFRAME STYLING
        ========================================= */

        [data-testid="stDataFrame"],
        [data-testid="stDataEditor"] {{
            background-color: {card} !important;
            border: 1px solid {border} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
            margin-top: 8px;
            margin-bottom: 14px;
        }}
        [data-testid="stDataFrame"] > div,
        [data-testid="stDataEditor"] > div {{
            background-color: {card} !important;
            border-radius: 12px !important;
        }}
        [data-testid="stDataFrame"] [data-testid="stElementToolbar"],
        [data-testid="stDataEditor"] [data-testid="stElementToolbar"] {{
            background-color: {card} !important;
            border-color: {border} !important;
        }}

        /* =========================================
        EXPANDER STYLING
        ========================================= */

        [data-testid="stExpander"] {{
            background-color: {card} !important;
            border: 1px solid {border} !important;
            border-radius: 10px !important;
            overflow: hidden !important;
            margin-bottom: 10px;
        }}
        [data-testid="stExpander"] summary {{
            background-color: {card} !important;
            color: {text} !important;
            padding: 12px 16px !important;
            font-weight: 600 !important;
        }}
        [data-testid="stExpander"] summary:hover {{
            background-color: {input_bg} !important;
        }}
        [data-testid="stExpander"] summary p,
        [data-testid="stExpander"] summary span {{
            color: {text} !important;
        }}
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {{
            background-color: {card} !important;
            border-top: 1px solid {border} !important;
            padding: 14px 16px !important;
        }}
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] p,
        [data-testid="stExpander"] [data-testid="stExpanderDetails"] label {{
            color: {text} !important;
        }}

        /* =========================================
        GLOBAL BUTTONS
        ========================================= */

        .stButton > button,
        .stDownloadButton > button,
        .stFormSubmitButton > button {{
            background: {button_gradient} !important;
            color: #FFFFFF !important;
            border: 1px solid {accent} !important;
            border-radius: 9px !important;
            font-weight: 600;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 14px {glow} !important;
        }}
        .stButton > button:hover,
        .stDownloadButton > button:hover,
        .stFormSubmitButton > button:hover {{
            background: {button_gradient} !important;
            color: #FFFFFF !important;
            border-color: {accent} !important;
            transform: translateY(-2px);
            box-shadow: {hover_shadow} !important;
            filter: brightness(1.08);
        }}

        /* SIDEBAR BUTTON OVERRIDE */
        /* Keep sidebar buttons independent from global buttons */

        [data-testid="stSidebar"] .stButton > button {{
            background: {card} !important;
            color: {text} !important;
            box-shadow: none !important;
        }}
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: {input_bg} !important;
            color: {accent} !important;
            box-shadow: 0 4px 15px {glow} !important;
        }}

        /* =========================================
        ACTIVE SIDEBAR NAVIGATION
        ========================================= */

        [data-testid="stSidebar"] .stButton > button[kind="primary"] {{
            background: {button_gradient} !important;
            color: #FFFFFF !important;
            border: 1px solid {accent} !important;
            border-left: 4px solid {accent} !important;
            font-weight: 800 !important;
            box-shadow: 0 4px 18px {glow} !important;
            transform: translateX(3px);
        }}
        [data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {{
            background: {button_gradient} !important;
            color: #FFFFFF !important;
            border-color: {accent} !important;
            box-shadow: {hover_shadow} !important;
            filter: brightness(1.12);
            transform: translateX(5px);
        }}
        [data-testid="stSidebar"] .stButton > button[kind="secondary"] {{
            background: {card} !important;
            color: {text} !important;
        }}

        /* =========================================
        INPUTS AND TEXTAREA
        ========================================= */

        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input {{
            background-color: {input_bg} !important;
            color: {text} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
        }}
        .stTextInput input::placeholder,
        .stTextArea textarea::placeholder,
        .stNumberInput input::placeholder {{
            color: {secondary} !important;
        }}

        /* =========================================
        SELECTBOX AND MULTISELECT
        ========================================= */

        [data-baseweb="select"] > div {{
            background-color: {input_bg} !important;
            border: 1px solid {border} !important;
            border-radius: 8px !important;
            color: {text} !important;
        }}
        [data-baseweb="select"] span,
        [data-baseweb="select"] input {{
            color: {text} !important;
            -webkit-text-fill-color: {text} !important;
        }}
        [data-baseweb="select"] svg {{
            fill: {text} !important;
            color: {text} !important;
        }}
        [data-baseweb="select"] > div:focus-within {{
            border-color: {accent} !important;
            box-shadow: 0 0 0 1px {accent} !important;
        }}

        /* =========================================
        DROPDOWN MENU - DEPLOYMENT FIX
        ========================================= */

        [data-baseweb="popover"] > div,
        [data-baseweb="popover"] [data-baseweb="menu"],
        [data-baseweb="menu"],
        ul[role="listbox"] {{
            background: {card} !important;
            background-color: {card} !important;
            border: 1px solid {border} !important;
            color: {text} !important;
        }}

        /* Dropdown option items */

        [data-baseweb="popover"] [role="option"],
        [data-baseweb="menu"] [role="option"],
        ul[role="listbox"] li {{
            background: {card} !important;
            background-color: {card} !important;
            color: {text} !important;
        }}

        /* Hover and selected options */

        [data-baseweb="popover"] [role="option"]:hover,
        [data-baseweb="menu"] [role="option"]:hover,
        ul[role="listbox"] li:hover,
        [data-baseweb="popover"] [role="option"][aria-selected="true"],
        [data-baseweb="menu"] [role="option"][aria-selected="true"] {{
            background: {input_bg} !important;
            background-color: {input_bg} !important;
            color: {text} !important;
        }}

        /* Dropdown option text */

        [data-baseweb="popover"] [role="option"] *,
        [data-baseweb="menu"] [role="option"] *,
        ul[role="listbox"] li * {{
            color: {text} !important;
            -webkit-text-fill-color: {text} !important;
        }}

        /* Dropdown search input */

        [data-baseweb="popover"] input {{
            background-color: {input_bg} !important;
            color: {text} !important;
            -webkit-text-fill-color: {text} !important;
        }}

        /* Dropdown scrollbar */

        [data-baseweb="popover"] ::-webkit-scrollbar {{
            width: 7px;
        }}

        [data-baseweb="popover"] ::-webkit-scrollbar-thumb {{
            background: {border};
            border-radius: 10px;
        }}

        /* =========================================
        TABS
        ========================================= */

        .stTabs [data-baseweb="tab"] {{
            color: {secondary} !important;
        }}
        .stTabs [aria-selected="true"] {{
            color: {accent} !important;
        }}

        /* =========================================
        RADIO AND CHECKBOX
        ========================================= */

        .stRadio label,
        .stCheckbox label {{
            color: {text} !important;
        }}
        [data-testid="stWidgetLabel"] p {{
            color: {text} !important;
        }}

        /* =========================================
        DIVIDERS AND FOOTER
        ========================================= */

        hr {{
            border-color: {border};
        }}
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
        footer {{
            visibility: hidden;
        }}

        /* =========================================
        RESPONSIVE CONTENT
        ========================================= */

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
    Apply active color theme to Plotly charts.
    """
    theme = st.session_state.get("color_theme","Ocean Blue")
    chart_themes = {
        "Ocean Blue": {
            "background": "#142D43",
            "text": "#F0F9FF",
            "grid": "#23445D",
            "accent": "#38BDF8",
            "palette": ["#38BDF8", "#0EA5E9", "#7DD3FC", "#2563EB", "#A5F3FC"],
        },
        "Pearl Light": {
            "background": "#FFFFFF",
            "text": "#172B4D",
            "grid": "#E2E8F0",
            "accent": "#2563EB",
            "palette": ["#2563EB","#0EA5E9","#10B981","#F59E0B","#8B5CF6","#EC4899"],
        },
        "Aurora Teal": {
            "background": "#3B5558",
            "text": "#F0F7F5",
            "grid": "#587477",
            "accent": "#65D6C2",
            "palette": ["#65D6C2","#38B2AC","#A7E3D8","#4F9DA6","#B8D8C8"],
        },
        "Graphite Bronze": {
            "background": "#52514E",
            "text": "#FAF7F0",
            "grid": "#716B60",
            "accent": "#D6AE72",
            "palette": ["#D6AE72","#C18E55","#E8C99A","#AFA18A","#F0D9B5"],
        },
        "Slate Mono": {
            "background": "#252D37",
            "text": "#F1F5F9",
            "grid": "#3B4653",
            "accent": "#CBD5E1",
            "palette": ["#CBD5E1", "#94A3B8", "#E2E8F0", "#64748B", "#F8FAFC"],
        }
    }
    colors = chart_themes.get(theme,chart_themes["Ocean Blue"])
    fig.update_layout(
        template="plotly_white" if theme == "Pearl Light" else "plotly_dark",
        paper_bgcolor=colors["background"],
        plot_bgcolor=colors["background"],
        colorway=colors["palette"],
        font=dict(
            color=colors["text"],
            family="Arial"
        ),
        title_font=dict(
            color=colors["text"]
        ),
        legend=dict(
            font=dict(color=colors["text"]),
            title_font=dict(color=colors["text"])
        ),
        hoverlabel=dict(
            bgcolor=colors["background"],
            bordercolor=colors["accent"],
            font=dict(
                color=colors["text"],
                family="Arial",
                size=13
            )
        ),
        transition=dict(
            duration=500,
            easing="cubic-in-out"
        ),
        hovermode="closest",
        xaxis=dict(
            color=colors["text"],
            title_font=dict(color=colors["text"]),
            tickfont=dict(color=colors["text"]),
            gridcolor=colors["grid"],
            linecolor=colors["grid"],
            zerolinecolor=colors["grid"]
        ),
        yaxis=dict(
            color=colors["text"],
            title_font=dict(color=colors["text"]),
            tickfont=dict(color=colors["text"]),
            gridcolor=colors["grid"],
            linecolor=colors["grid"],
            zerolinecolor=colors["grid"]
        )
    )
    return fig

def render_dataframe(df, **kwargs):
    """
    Render DataFrame using the active color theme.
    """
    theme = st.session_state.get("color_theme","Ocean Blue")
    table_themes = {
        "Ocean Blue": {
            "background": "#142D43",
            "text": "#F0F9FF",
            "header": "#19364F",
            "border": "#23445D"
        },
        "Pearl Light": {
            "background": "#FFFFFF",
            "text": "#172B4D",
            "header": "#EAF0F7",
            "border": "#DCE5F0"
        },
        "Aurora Teal": {
            "background": "#3B5558",
            "text": "#F0F7F5",
            "header": "#456164",
            "border": "#587477"
        },
        "Graphite Bronze": {
            "background": "#52514E",
            "text": "#FAF7F0",
            "header": "#5D5A54",
            "border": "#716B60"
        },
        "Slate Mono": {
            "background": "#252D37",
            "text": "#F1F5F9",
            "header": "#303A46",
            "border": "#3B4653"
        }
    }
    colors = table_themes.get(theme,table_themes["Ocean Blue"])
    styled_df = (
        df.style
        .set_properties(
            **{
                "background-color": colors["background"],
                "color": colors["text"],
                "border-color": colors["border"]
            }
        )
        .set_table_styles([
            {
                "selector": "th",
                "props": [
                    ("background-color", colors["header"]),
                    ("color", colors["text"]),
                    ("border-color", colors["border"]),
                    ("font-weight", "bold")
                ]
            },
            {
                "selector": "td",
                "props": [
                    ("border-color", colors["border"])
                ]
            }
        ])
    )
    kwargs.setdefault("use_container_width", True)
    st.dataframe(
        styled_df,
        **kwargs
    )
