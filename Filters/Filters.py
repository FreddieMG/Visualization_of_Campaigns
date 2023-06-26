
import pandas as pd
import streamlit as st

def filter_A(df: pd.DataFrame):
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    # modify = st.checkbox("Add filters")

    # if not modify:
    #     left, right = st.columns((1, 20))
    #
    #     column = 'year'
    #     _min = int(df[column].min())
    #     _max = int(df[column].max())
    #     step = (_max - _min) // 60
    #     user_num_input = right.slider(
    #         f"Values for {column}",
    #         min_value=int(_min),
    #         max_value=int(_max),
    #         value=(int(1983), int(1993)),  # Set the default range
    #         step=int(step),
    #     )
    #     df = df[df[column].between(*user_num_input)]
    #     df.sort_values(by=['year'], inplace=True)
    #     cy0id = df[df["cyear"] == 0]["id"]
    #     cy1id = df[df["cyear"] == 1]["id"]
    #
    #     ids = set(cy0id).intersection(set(cy1id))
    #     df = df[df["id"].isin(ids)]
    #
    #     return df, df["id"].unique()

    df = df[df['percent_participation'] < 12]
    df = df.copy()

    modification_container = st.container()

    with modification_container:
        # to_filter_columns = st.multiselect("Filter dataframe on", ['Year', 'Goal'])
        # ['year', 'campaign_goal']
        # for column in to_filter_columns:
        left, right = st.columns((1, 20))
        # Treat columns with < 10 unique values as categorical
        # if column == 'Goal':
        column = 'goal_names'
        user_cat_input = right.multiselect(
            f"Filter campaign goals",
            df[column].unique(),
            default=list(df[column].unique()),
        )
        df = df[df[column].isin(user_cat_input)]
        if len(df) == 0:
            return df, 0
    # elif column == 'Year':
        column = 'year'
        _min = int(df[column].min())
        _max = int(df[column].max())
        step = (_max - _min) // 60
        user_num_input = right.slider(
            f"Select a range of years to inspect",
            min_value=int(_min),
            max_value=int(_max),
            value=(int(2006), int(2013)),  # Set the default range
            step=int(step),
        )
        df = df[df[column].between(*user_num_input)]
        df.sort_values(by=['year'], inplace=True)
        cy0id = df[df["cyear"] == 0]["id"]
        cy1id = df[df["cyear"] == 1]["id"]

        ids = set(cy0id).intersection(set(cy1id))
        df = df[df["id"].isin(ids)]
        if len(df) == 0:
            return df, 0

        return df, df["id"].unique()



def filter_CD(df: pd.DataFrame):
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    df = df.copy()
    df['count'] = 1

    success_values = {0: 'Failure', 1: 'Success'}
    df['success'] = df['success'].map(success_values)
    df = df[df["repression_names"] != "unknown"]

    separate = st.checkbox("Combine Goals")

    if separate:
        return df, None, False


    modification_container = st.container()

    left, right = st.columns((1, 20))
    # Treat columns with < 10 unique values as categorical
    df_regime = df[df['goal_names'] == 'regime change']
    df_auto = df[df['goal_names'] == 'greater autonomy']
    return df_regime, df_auto, True


def filter_E(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    df = df.copy()
    progress_values = {0: "status quo", 1: "visible gains short of concessions", 2: "limited concession achieved",
                       3: "significant concessions achieved", 4: "complete success", -1: "ends in failure",
                       -99: "unknown"}

    df = df[df['ab_internat'] != -99]
    new_df = {'goal_names': [], 'ab_internat': [], 'progress_names': []}
    for id in df['id'].unique():
        cur_df = df[df['id'] == id]
        max_progress = cur_df['progress'].max()
        new_df['progress_names'].append(progress_values[max_progress])
        new_df['goal_names'].append(cur_df['goal_names'].iloc[0])
        if 1 in cur_df['ab_internat'].unique():
            new_df['ab_internat'].append('Material Reprucussions')
        else:
            new_df['ab_internat'].append('No Intervention')

    return pd.DataFrame(new_df)


def filter_F(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """

    df = df.copy()
    progress_values = {0: "status quo", 1: "visible gains short of concessions", 2: "limited concession achieved",
                       3: "significant concessions achieved", 4: "complete success", -1: "ends in failure",
                       -99: "unknown"}



    df = df[df['ab_internat'] != -99]
    new_df = {'goal_names': [], 'progress_names': []}
    for id in df['id'].unique():
        cur_df = df[df['id'] == id]
        max_progress = cur_df['progress'].max()
        new_df['progress_names'].append(progress_values[max_progress])
        new_df['goal_names'].append(cur_df['goal_names'].iloc[0])

    return pd.DataFrame(new_df)