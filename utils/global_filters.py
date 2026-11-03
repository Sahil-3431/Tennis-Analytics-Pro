import streamlit as st


def apply_global_filters(df, include_gender=True):

    filtered_df = df.copy()

    if filtered_df.empty:
        return filtered_df

    selected_ranking = st.session_state.get(
        "global_ranking", "All"
    )

    selected_country = st.session_state.get(
        "global_country", "All"
    )

    selected_gender = st.session_state.get(
        "global_gender", "All"
    )

    if (
        selected_ranking != "All"
        and "ranking_name" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["ranking_name"] == selected_ranking
        ]

    country_column = (
        "country"
        if "country" in filtered_df.columns
        else "country_display"
    )

    if (
        selected_country != "All"
        and country_column in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df[country_column] == selected_country
        ]

    if (
        include_gender
        and selected_gender != "All"
        and "gender" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["gender"] == selected_gender
        ]

    return filtered_df.copy()