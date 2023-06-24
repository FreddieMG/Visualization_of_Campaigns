# %%
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import streamlit as st
import sys
from streamlit_extras.switch_page_button import switch_page

# print("Page names: ", st.source_util.get_pages("Campaign_Goal_Analysis.py"))
st.set_page_config(layout="wide",initial_sidebar_state="collapsed")

if st.button("Campaign Goal Analysis"):
    switch_page("Campaign_Goal_Analysis")

#os.chdir(r"C:\Users\Lior\Desktop\Information-Visualization")

df = pd.read_csv('data/processed_data.csv')
df.sort_values(by=['id', 'year'], inplace=True)
#
st.title('Campaign By Sizes and their Achievements Over Time')
st.write('''
Here we show the size of different campaigns over time.
The width represents the Relative size of the campaign compared to the population of the country in a specific year (in percents).
The the colors represent the Achievements for that Year
You can hover over the lines to see more detailed information for each data point.
''')
from Filters.Filters import filter_A

df_A, ids = filter_A(df)

A_color_dict = {
    'complete success': '#006400',  # Darker green
    'visible gains short of concessions': '#FFD700',  # YellowGreen
    'limited concession achieved': '#A2CD5A',  # Darker yellowgreen
    'status quo': 'orange',  # Gold
    'significant concessions achieved': '#6E8B3D',  # Lighter yellowgreen
    'ends in failure': '#8B0000',  # Dark red
}

color_dict = {
    'No Intervention': '#FFA07A',
    'Material Reprucussions': '#4682B4',
    'complete success': '#006400',  # Darker green
    'limited concession achieved': '#A2CD5A',  # Darker yellowgreen
    'status quo': 'orange',  # Gold
    'significant concessions achieved': '#6E8B3D',  # Lighter yellowgreen
    'ends in failure': '#8B0000',  # Dark red
    'visible gains short of concessions': '#FFD700',  # YellowGreen
    'greater autonomy': '#808080'  # Gray
}


#translate df_A['progress_names'] to colors

df_A['color'] = df_A['progress_names'].apply(lambda x: color_dict[x])


# df_A["line_width"]  = df_A["line_width"].apply(lambda x: int(x))

# fig_A = px.line(df_A, x='year', y='percent_participation', color='progress_names',
#                 line_dash='goal_names', hover_data=['camp_name', 'location'], line_group='id')

# goals_to_type = {"greater autonomy": "dash", "regime change": "solid"}

colors = list(A_color_dict.values())
progresses = list(A_color_dict.keys())


fig_A = go.Figure()

# Create a trace for each color and progress
def width_bracket(percent):
    if percent < 0.1:
        width = 1
    elif percent < 0.25:
        width = 2
    elif percent < 0.5:
        width = 3
    elif percent < 1:
        width = 4
    elif percent < 1.5:
        width = 5
    elif percent < 2:
        width = 6
    elif percent < 5:
        width = 7
    elif percent < 10:
        width = 8
    else:
        width = 9
    return width
campaign_names = []
for i, id in enumerate(ids):
    df_temp = df_A[df_A['id'] == id]
    campaign_names.append(df_temp['camp_name'].iloc[0])
    unique_years = df_temp['year'].unique()
    ## add another year that is 1 year after the last year and has the same values
    unique_years = np.append(unique_years, unique_years[-1] + 1)

    latest_year_row = df_temp[df_temp['year'] == df_temp['year'].max()]

    new_row = latest_year_row.copy()
    new_row['year'] = new_row['year'] + 1
    new_row_df = pd.DataFrame(new_row)
    df_temp = pd.concat([df_temp, new_row_df], ignore_index=True)

    for year in unique_years:
        df_years = df_temp[(df_temp['year'] == year) | (df_temp['year'] == year + 1)]

        # width = np.clip(np.log2(float(abs(df_years["percent_participation"].iloc[0]))*1000 + 0.0001), 0.05, 10)
        width = width_bracket(df_years["percent_participation"].iloc[0]) * 2

        if np.isnan(width):
            width = 0

        fig_A.add_trace(go.Scatter(
            x=df_years['year'],
            y=[i]*len(df_years),
            mode='lines',
            marker = dict(color = df_years['color'].iloc[0]),
            line=dict(color="lightslategray", width=width+1.5),
            customdata=list(zip(df_years['id'], df_years['progress_names'], df_years['percent_participation'], df_years['camp_name'])),
            # Use a list of tuples containing the id and progress names
            hovertemplate='Campaign ID: %{customdata[0]}<br>Year: %{x}<br>Progress: %{customdata[1]} <br> Relative Size: %{customdata[2]} <br> Campaign Name: %{customdata[3]}'
            # Use the first values of the custom data columns
        ))

        fig_A.add_trace(go.Scatter(
            x=df_years['year'],
            y=[i]*len(df_years),
            mode='lines',
            marker = dict(color = df_years['color'].iloc[0]),
            line=dict(color=df_years['color'].iloc[0], width=width),
            customdata=list(zip(df_years['id'], df_years['progress_names'], df_years['percent_participation'], df_years['camp_name'])),
            # Use a list of tuples containing the id and progress names
            hovertemplate='Campaign ID: %{customdata[0]}<br>Year: %{x}<br>Progress: %{customdata[1]} <br> Relative Size: %{customdata[2]} <br> Campaign Name: %{customdata[3]}'
            # Use the first values of the custom data columns
        ))

years_range = int((df_A['year'].max() - df_A['year'].min())//2)
years_grid = list(range(df_A['year'].min(), df_A['year'].max(), 2))
max_val = df_A['percent_participation'].max()
fig_A.update_layout(
    # autosize=False,  # Disable autosize
    width=1500,  # Set figure width
    height=800,  # Set figure height
    xaxis_title='Year',
    yaxis_title='Campaign Name',
    xaxis={'fixedrange': True},  # Disable dragging on x-axis
    yaxis={'fixedrange': True, 'range': [0, len(ids)],
           'tickvals': list(range(len(ids))),  # Set tick values to the index of each campaign
           'ticktext': campaign_names, 'showgrid': True  # Set tick labels to the names of the campaigns
           },
    xaxis_title_font=dict(size=20),
    yaxis_title_font=dict(size=20),

    title=dict(text='', x=0.5, xanchor='center', y=0.9),
    autosize=True,
    margin=dict(t=0),

)

fig_A.update_traces(showlegend=False)

progress_order = [
    'ends in failure',
    'status quo',
    'visible gains short of concessions',
    'limited concession achieved',
    'significant concessions achieved',
    'complete success'
]
progress_order.reverse()

color_trace = px.line(
    df_A,
    x="year",
    y=np.full(len(df_A), -1000),
    color="progress_names",
    color_discrete_map=color_dict, # Use the color_dict as the color map
    category_orders={"progress_names": progress_order} # Use the progress_order as the category order
    ).update_traces(legendgrouptitle_text="Campaign Progress", legendgroup=str("Legends"))


fig_A.add_traces(color_trace.data)

# Create a dummy trace for the width legend
width_trace = go.Scatter(
    x=[df_A['year'].min()], # Use the minimum year as the x value
    y=[-1000], # Use the same dummy y value as the color trace
    mode='markers', # Use markers instead of lines
    marker=dict(color='white', size=10, symbol='triangle-left'), # Use a triangle symbol with a constant size and color
    name='width = Relative Campaign Size', # Use the desired legend text
    showlegend=True # Show this trace in the legend
)

fig_A.add_trace(width_trace)

fig_A.update_layout(title=dict(font=dict(size=20)), legend=dict(font=dict(size = 18)))


st.plotly_chart(fig_A)

# st.title('Campaign Size Distribution')
st.title('Campaign Size Effect on Success Rate')
st.write('''
This histogram shows Chances of success by Campaign Size (Relative to Country Population).
''')
from Filters.filter_B import filter_B


df_B2, df_B1, num_bins = filter_B(df, 'Small')
#Define the number of bins and bin width
bin_width = (df_B1['stat'].max() - df_B1['stat'].min()) / num_bins

#Create the bins
bins = np.arange(0, df_B1['stat'].max(), bin_width)

#Group the data into the bins and calculate the average success percentage
df_B1['stat_bins'] = pd.cut(df_B1['stat'], bins)
grouped = df_B1.groupby('stat_bins')['success'].mean()

#Convert Interval object to string representation
x_values = [str(interval) for interval in grouped.index]

#Get the count of data points in each bin
counts = df_B1['stat_bins'].value_counts().reindex(grouped.index, fill_value=0)

#Create the hovertemplate
hovertemplate = (
    "Bin: %{x}<br>"
    "Success Percentage: %{y:.2f}%<br>"
    "Data Points: %{customdata}"
)

success_percentage = grouped * 100
rounded_percentage = round(success_percentage, 2)

#Create the bar trace with the desired color and rounded values
trace = go.Bar(
    x=x_values,
    y=grouped * 100,  # Multiply by 100 to get percentage
    marker=dict(color='rgb(128, 177, 211)'),
    text=rounded_percentage,
    customdata = counts,
    texttemplate='%{text:.0f}%',  # Format the text as rounded percentage with 2 decimal places
    hovertemplate=hovertemplate,
    hovertext=counts,  # Set the hover text to the counts
)

#Create the layout
layout = go.Layout(
    title='Small Campaigns (Up to 1.5%)',
    xaxis=dict(title=dict(text='Percent of Population Present In Campaign', font=dict(size=18))),
    yaxis=dict(title=dict(text='Success Percentage', font=dict(size=18))),
    width = 800
)


#Create the figure
fig_B1 = go.Figure(data=[trace], layout=layout)


bin_width = (df_B2['stat'].max() - df_B2['stat'].min()) / num_bins

#Create the bins
bins = np.arange(1.5, df_B2['stat'].max() + bin_width, bin_width)

#Group the data into the bins and calculate the average success percentage
df_B2['stat_bins'] = pd.cut(df_B2['stat'], bins)
grouped = df_B2.groupby('stat_bins')['success'].mean()

#Convert Interval object to string representation
x_values = [str(interval) for interval in grouped.index]

#Get the count of data points in each bin
counts = df_B2['stat_bins'].value_counts().reindex(grouped.index, fill_value=0)

#Create the hovertemplate
hovertemplate = (
    "Bin: %{x}<br>"
    "Success Percentage: %{y:.2f}%<br>"
    "Data Points: %{customdata}"
)

success_percentage = grouped * 100
rounded_percentage = round(success_percentage, 2)

#Create the bar trace with the desired color and rounded values
trace = go.Bar(
    x=x_values,
    y=grouped * 100,  # Multiply by 100 to get percentage
    marker=dict(color='rgb(128, 177, 211)'),
    text=rounded_percentage,
    customdata = counts,
    texttemplate='%{text:.0f}%',  # Format the text as rounded percentage with 2 decimal places
    hovertemplate=hovertemplate,
    hovertext=counts,  # Set the hover text to the counts
)

#Create the layout
layout = go.Layout(
    title='Large Campaigns (Larger than 1.5%)',
    xaxis=dict(title=dict(text='Percent of Population Present In Campaign', font=dict(size=18))),
    yaxis=dict(title=dict(text='Success Percentage', font=dict(size=18))),
    width = 800,
)



#Create the figure
fig_B2 = go.Figure(data=[trace], layout=layout)





col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_B1)
with col2:
    st.plotly_chart(fig_B2)

