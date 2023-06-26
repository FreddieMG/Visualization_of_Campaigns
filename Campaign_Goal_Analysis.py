import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide",initial_sidebar_state="collapsed")




customized_button = st.markdown("""
<style>
div.stButton > button:first-child {
  background-color: #ee4466;
  color: white;
    padding-top: 10px !important;
  padding-bottom: 10px !important;
}
div.stButton > button:hover {
  background-color: darkred;
  color: white;
}
</style>""", unsafe_allow_html=True)

columns = st.columns((2, 1, 2))
button_pressed = columns[1].button('Go To Campaign Size and Success')
# Initialize a session state variable for the button state

if 'button_state' not in st.session_state:
    st.session_state.button_state = False

# Update the session state variable only when the button is clicked
if button_pressed:
    st.session_state.button_state = True

# Check the session state variable to switch page
if st.session_state.button_state:
    st.session_state.button_state = False

    switch_page("Campaign_Size_and_Success")


from Filters.Filters import filter_E, filter_F

df = pd.read_csv('data/processed_data.csv')
df.sort_values(by=['id', 'year'], inplace=True)


df_F =  filter_F(df)
df_F['progress_names'] = df_F['progress_names'].str.title()
df_F['goal_names'] = df_F['goal_names'].str.title()


df_F['progress_names'] = df_F['progress_names'].replace({'Ends In Failure': 'Failed Immediately'})
df_F = df_F.groupby(['goal_names', 'progress_names']).size().reset_index(name='counts')
df_F['percent'] = df_F.groupby(['goal_names'])['counts'].transform(lambda x: x / x.sum() * 100)
df_F['percent_str'] = df_F['percent'].round(2).astype(str) + '%'

# Create a bar plot faceted by goal and x axis
fig_F = px.bar(df_F, x="progress_names", y="percent", facet_col="goal_names",
               color="progress_names",
               color_discrete_sequence=px.colors.sequential.YlGn,
               color_discrete_map={"Failed Immediately".title(): "salmon",
                                   "status quo".title(): "#ffffe5",
                                   "limited concession achieved".title(): "#d9f0a3",
                                   "visible gains short of concessions".title(): "#addd8e",
                                   "significant concessions achieved".title(): "#41ab5d",
                                   "complete success".title(): "#006837"},
               category_orders={"progress_names": ["Failed Immediately",
                                                    "status quo".title(),
                                                   "limited concession achieved".title(),
                                                   "visible gains short of concessions".title(),
                                                   "significant concessions achieved".title(),
                                                   "complete success".title()]},
               labels={"progress_names": "Best Achievement in Campaign"},
               text="percent_str",
               facet_col_wrap=2, height=600, width=1650,

               )


#limit y axis to 0-40
fig_F.update_layout(
    coloraxis={"colorscale": px.colors.sequential.Darkmint},
    yaxis=dict(range=[0, 40]),
    legend=dict(
    title=dict(font=dict(size=20)),
    orientation="h",
    yanchor="bottom",
    y=-0.15,
    # cange legend title font size
    font=dict(size = 18,
    # change this value to move the legend lower
))   )



#remove progress names from x axis but keep the pacet titles
fig_F.update_xaxes(title_text='')
fig_F.update_xaxes(showticklabels=False)
fig_F.update_xaxes(showgrid=False)



for a in fig_F.layout.annotations:
    a.text = a.text.split("=")[1]
    #increase font size
    a.font.size = 18

fig_F.update_layout(

    yaxis_title='Percent of Total',
    yaxis_title_font=dict(size=20),
    xaxis={'fixedrange': True},  # Disable dragging on x-axis
    yaxis={'fixedrange': True, 'range': [0, 45]},    # Use log scale and disable dragging on y-axis,
)

st.title('Campaign Goal Comparison')
st.write('''
This page is dedicated to comparing the success and progress made by campaigns for increasing autonomy, compared to
 campaigns for regime change. The plots use additional criteria to delve into additional factors correlated with the progress made by the campaigns. 
''')

st.subheader('Distribution of Best Progress Achieved by Campaign Goal')
st.write('''
This bar plot, which is faceted by campaign goal, displays the distribution of progress for each campaign goal. 
The x axis represents the best progress achieved by the campaign,
 and the y axis represents the percent of campaigns from that goal that fall into this progress
  category. The color of the bars represents the progress category.

Please note that all the campaigns that don't have "complete success" as a progress category are originally cateorized
 as ending in failure, we chose to show the best status achieved for the campaigns as an indication of it's achievements.
''')
st.plotly_chart(fig_F)



st.subheader('Campaign Violence and State Reaction Effects on Success Rate')
st.write('''
This multi-faceted pie chart shows the percent of successful campaigns for each level of violence shown by the campaign 
 participants, and for each level of repression employed by the government. You can view it faceted by goal,
  or combined for both goals.
  ''')

from Filters.Filters import filter_CD

# Filter the DataFrame based on the campaign goal
CD_res = filter_CD(df)  # Replace 'Your Campaign Goal' with your filter
if CD_res[2]:
    CD_dfs = [CD_res[0], CD_res[1]]
else:
    CD_dfs = [CD_res[0]]

# Create a temporary 'count' column to use for the pie chart values

# Create a pie chart for each combination of state reaction and violence level
figs_CD = []
if len(CD_dfs) == 1:
    titles = ['']
else:
    titles = ['Regime Change', 'Greater Autonomy']
for i, df_CD in enumerate(CD_dfs):


    fig_CD = px.pie(df_CD, values='count', names='success',
                 facet_col='repression_names', facet_row='resistance method',
                 color='success',
                 color_discrete_map={'Success':'#00FF7F', 'Failure':'salmon'},
                title=titles[i],
            category_orders={"repression_names": ["extreme repression", "moderate repression", "mild repression", "none"],
                             "resistance method": ["never violent", "sometimes violent", "always violent"]})

    for a in fig_CD.layout.annotations:
        a.text = a.text.split("=")[1]

    # Customize the layout
    fig_CD.update_layout(
        autosize=False,
        width=750,
        height=500,
        title_text=titles[i],
        title_x=0.4,
    )
    if len(CD_dfs) == 2 and i == 0:
        fig_CD.update_layout(
            showlegend=False
        )

    for a in fig_CD['layout']['annotations']:
        if a['text'] in  ["always violent", "never violent", "sometimes violent"]:
            a["textangle"] = 50
            a["xref"] = "paper"
            a["yref"] = "paper"
            a["x"] -= 0.04
            # a["y"] = 1 - (i / 2)

            a['align'] = "left"
            #incrase font size
        else:
            a['y'] = a['y'] + 0.05
        if a['text'] == 'none':
            a['text'] = 'No Repression'

        a['font'] = dict(size=15)
        if i == 0 and a['text'] in ["always violent", "never violent", "sometimes violent"]:
            a['font'] = dict(size=1, color='black')
        a['text'] = a['text'].title()
    figs_CD.append(fig_CD)




df_E = filter_E(df)
# Combine goal, intervention, and progress to create unique nodes
df_E['goal_intervention'] = df_E['goal_names'] + '_' + df_E['ab_internat']
df_E['intervention_progress'] = df_E['ab_internat'] + '_' + df_E['progress_names']

# Create unique mappings for your categories
goal_intervention_mapping = {goal_intervention: i for i, goal_intervention in enumerate(df_E['goal_intervention'].unique())}
intervention_progress_mapping = {intervention_progress: i + len(goal_intervention_mapping) for i, intervention_progress in enumerate(df_E['intervention_progress'].unique())}

# Apply the mappings to your columns
df_E['goal_intervention_codes'] = df_E['goal_intervention'].map(goal_intervention_mapping)
df_E['intervention_progress_codes'] = df_E['intervention_progress'].map(intervention_progress_mapping)

# Rest of the code...



progress_order = ['Complete Success', 'Significant Concessions Achieved', 'Limited Concession Achieved',
                  'Visible Gains Short Of Concessions', 'Status Quo', 'Ends In Failure']
# Iterate over each goal
df_E = filter_E(df)
df_E['progress_names'] = df_E['progress_names'].str.title()
# Combine goal, intervention, and progress to create unique nodes
#df_E['goal_intervention'] = df_E['goal_names'] + '_' + df_E['ab_internat']
df_E['intervention_progress'] = df_E['ab_internat'] + '_' + df_E['progress_names']

# Create unique mappings for your categories
#goal_intervention_mapping = {goal_intervention: i for i, goal_intervention in enumerate(df_E['goal_intervention'].unique())}
intervention_progress_mapping = {intervention_progress: i + len(goal_intervention_mapping) for i, intervention_progress in enumerate(df_E['intervention_progress'].unique())}

# Apply the mappings to your columns
#df_E['goal_intervention_codes'] = df_E['goal_intervention'].map(goal_intervention_mapping)
df_E['intervention_progress_codes'] = df_E['intervention_progress'].map(intervention_progress_mapping)

# Rest of the code...
# Iterate over each goal
E_figs = []
color_dict = {
    'No Intervention': '#FFA07A',
    'Material Reprucussions': '#4682B4',
    'Complete Success': '#006400',  # Darker green
    'Limited Concession Achieved': '#A2CD5A',  # Darker yellowgreen
    'Status Quo': 'orange',  # Gold
    'Significant Concessions Achieved': '#6E8B3D',  # Lighter yellowgreen
    'Ends In Failure': '#8B0000',  # Dark red
    'Visible Gains Short Of Concessions': '#FFD700',  # YellowGreen
    'Greater Autonomy': '#808080'  # Gray
}
for goal, df_goal in df_E.groupby('goal_names'):
    # Create unique mappings for your categories
    intervention_mapping = {name: i for i, name in enumerate(df_goal['ab_internat'].unique())}
    progress_mapping = {name: i + len(intervention_mapping) for i, name in enumerate(df_goal['progress_names'].unique())}

    # Apply the mappings to your columns
    df_goal['intervention_codes'] = df_goal['ab_internat'].map(intervention_mapping)
    df_goal['progress_codes'] = df_goal['progress_names'].map(progress_mapping)

    # Create source, target and value lists
    source = df_goal['intervention_codes'].tolist()
    target = df_goal['progress_codes'].tolist()
    values = [1 for _ in range(len(source))]
    sankey_data = pd.DataFrame({'source': source, 'target': target, 'values': values}).sort_values(['source', 'target'])
    # Create colors for each source node
    colors = df_goal['intervention_codes'].map({code: color for code, color in enumerate(['#4682B4','#FFA07A'])}).tolist()
    node_positions = {
        'Material Reprucussions': [0.001, 0.01],
        'No Intervention': [0.001, 0.7],
        'Complete Success': [0.999, 0.001],
        'Significant Concessions Achieved': [0.999, 0.2],
        'Limited Concession Achieved': [0.999, 0.4],
        'Visible Gains Short Of Concessions': [0.999, 0.6],
        'Status Quo': [0.999, 0.8],
        'Ends In Failure': [.999, .999]
    }
    # Create the label list with counts included
    label_counts = df_goal['ab_internat'].value_counts().to_dict()
    label = [f'{name} ({label_counts[name]})' if name in label_counts else name for name in
             list(intervention_mapping.keys()) + list(progress_mapping.keys())]
    # Create a list of all unique nodes in the correct order
    #all_nodes_E = df_goal['goal_names'].unique().tolist() + df_goal['ab_internat'].unique().tolist()

    # Add progress nodes in the correct order
    all_nodes_E = df_goal['ab_internat'].unique().tolist() + df_goal['progress_names'].unique().tolist()

    # Manually order the labels based on desired_order
    ordered_labels = [label for label in all_nodes_E if label not in progress_order] + [label for label in progress_order if label in all_nodes_E]
    # Create a Sankey plot
    fig_E = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color='black', width=0.5),
            label=ordered_labels,
            color=[color_dict.get(node, '#808080') for node in ordered_labels],
            x = [node_positions.get(node, [0.01, 0.01])[0] for node in ordered_labels],
            y = [node_positions.get(node, [0.01, 0.01])[1] for node in ordered_labels]
        ),
        link=dict(
            source=source,
            target=target,
            value=values,
            color=colors,  # Add the colors
        )
    )])

    # Display the plot

    # Set the layout options
    if goal=="regime change":
        fig_E.update_layout(title_text=f'{str(goal).title()}', font_size=14, height=570, width=850, title_y=1, title_x=0.45,
                            autosize=True, margin=dict(l=50, r=50, b=100, t=100, pad=4))
    else:
        fig_E.update_layout(title_text=f'{str(goal).title()}', font_size=14, height=570, width=850, title_y=1, title_x=0.4,
                        autosize=True, margin=dict(l=50, r=50, b=100, t=100, pad=4))
    E_figs.append(fig_E)


if len(figs_CD) == 1:
    st.plotly_chart(figs_CD[0])
else:
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(figs_CD[0])
    with col2:
        st.plotly_chart(figs_CD[1])

st.subheader('International Intervention Analysis')
st.write('''
This Sankey plot shows the relationship between international intervention and success in campaigns of different goals.
 Campaigns of each goal are first split is by international intervention, and then by progress.
  The width of each tube represents the number of examples of that classification.
''')
col1, col2 = st.columns(2)

with col1:
    st.plotly_chart(E_figs[0])
with col2:
    st.plotly_chart(E_figs[1])


buttom_button = st.button('Go To Campaign Size and Success ', use_container_width=True)
if buttom_button:
    switch_page("Campaign_Size_and_Success")
