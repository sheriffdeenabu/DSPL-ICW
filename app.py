import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import requests
from io import BytesIO

# Configuration
st.set_page_config(page_title="Sri Lanka Food Security Dashboard", layout="wide")

# Load Sri Lanka flag image
def load_flag_image():
    flag_url = "https://raw.githubusercontent.com/sheriffdeenabu/DSPL-ICW/main/Images/download.png"

    response = requests.get(flag_url)
    flag_image = Image.open(BytesIO(response.content))
    return flag_image

@st.cache_data
def load_data():
    df = pd.read_csv('suite-of-food-security-indicators_lka-cleaned.csv')
    categories = {
        'Average protein supply': 'Protein Supply',
        'Gross domestic product per capita, PPP,': 'GDP per capita',
        'Number of people undernourished': 'Undernourishment',
        'Prevalence of severe food insecurity in the male adult population': 'Male Food Insecurity',
        'Prevalence of severe food insecurity in the female adult population': 'Female Food Insecurity',
        'Number of severely food insecure people': 'Severe Food Insecurity count',
        'Political stability and absence of violence/terrorism': 'Political Stability',
        'Percentage of population using safely managed drinking water services': 'Safe Water Access',
        'Percentage of population using at least basic drinking water services': 'Basic Water Access',
        'Number of obese adults': 'Obesity',
        'Prevalence of low birthweight': 'Low Birthweight',
        'Number of newborns with low birthweight': 'Low Birthweight Count'
    }
    df['Category'] = df['Item'].str.split('(').str[0].str.strip().replace(categories)
    df['Unit'] = df['Unit'].str.replace('million No', 'in millions')
    df['Year'] = df['Year'].astype(str)
    return df

def create_gauge_chart(value, title, min_val, max_val):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        number={'suffix': "k" if min_val > 1000 else ""},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "#1f77b4"},
            'steps': [
                {'range': [min_val, min_val + (max_val - min_val)*0.5], 'color': "lightgray"},
                {'range': [min_val + (max_val - min_val)*0.5, max_val], 'color': "gray"}],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': min_val + (max_val - min_val)*0.8}
        }
    ))
    fig.update_layout(
        height=300,
        margin=dict(t=50, b=10),
        autosize=True
    )
    return fig

def create_chart(data, chart_type, x=None, y=None, names=None, values=None, title=None, color=None):
    if chart_type == 'line':
        fig = px.line(data, x=x, y=y, title=title, color=color)
    elif chart_type == 'bar':
        fig = px.bar(data, x=x, y=y, title=title, color=color)
    elif chart_type == 'scatter':
        fig = px.scatter(data, x=x, y=y, title=title, color=color, trendline="lowess")
    elif chart_type == 'pie':
        fig = px.pie(data, names=names, values=values, title=title)
    elif chart_type == 'area':
        fig = px.area(data, x=x, y=y, title=title, color=color)
    elif chart_type == 'box':
        fig = px.box(data, x=x, y=y, title=title, color=color)
    elif chart_type == 'histogram':
        fig = px.histogram(data, x=x, title=title, color=color)
    else:
        raise ValueError("Unsupported chart type")
    
    if x == 'Year' or (isinstance(x, list) and 'Year' in x):
        fig.update_xaxes(type='category')
    return fig

# Sidebar navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "About", "Student Info"])

if page == "About":
    st.title("About the Sri Lanka Food Security Dashboard")
    st.markdown("""
    ### Dashboard Overview
    
    This interactive dashboard provides comprehensive insights into Sri Lanka's food security and related socioeconomic indicators. 
    The visualization tool contains:
    
    - **Trend Analysis**: Customizable multi-indicator trends over time (select up to 3 indicators)
    - **Advanced Analysis** with four specialized tabs:
      1. **Food Security**: Undernourishment trends, gender disparities in food insecurity
      2. **Economic**: GDP evolution, political stability correlations
      3. **Health**: Obesity patterns, low birthweight statistics
      4. **Progress Indicators**: Composite metrics with gauge charts and correlation matrices
    
    All visualizations are interactive with:
    - Year range filtering (2009-2022)
    - Multiple chart types (line, bar, pie, scatter, box, and gauge charts)
    - Real-time metric displays
    - Responsive design for all screen sizes
    """)
    
elif page == "Student Info":
    st.title("Student Information")
    st.markdown("""
    <div style='text-align: left;'>
        <p style='font-size: 20px;'><b>Abdullah Sheriffdeen</b></p>
        <p>Student ID: 20222221</p>
        <p>Email: sheriffdeenabdullah@gmail.com | abdullah.20222221@iit.ac.lk</p>
        <p>University of Westminster</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display Sri Lanka flag only on Dashboard page
    flag = load_flag_image()
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(flag, width=300)  # Well-proportioned size (300px width)
        st.markdown("<h1 style='text-align: center;'>Sri Lanka Food Security Indicators</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    df = load_data()
    min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
    year_range = st.slider("Select Year Range", min_year, max_year, (min_year, max_year))
    filtered_df = df[(df['Year'].astype(int) >= year_range[0]) & (df['Year'].astype(int) <= year_range[1])]
    
    st.subheader("Trend Analysis")
    categories = st.multiselect(
        "Select Indicators (Max 3)", 
        filtered_df['Category'].unique(),
        default=None,
        max_selections=3
    )

    if categories:
        fig = go.Figure()
        for cat in categories:
            cat_df = filtered_df[filtered_df['Category'] == cat]
            fig.add_trace(go.Scatter(
                x=cat_df['Year'], 
                y=cat_df['Value'], 
                name=cat,
                mode='lines+markers'
            ))
        fig.update_layout(
            xaxis_title='Year', 
            yaxis_title='Value', 
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        cols = st.columns(len(categories))
        for idx, cat in enumerate(categories):
            latest = filtered_df[filtered_df['Category'] == cat].iloc[-1]
            cols[idx].metric(cat, f"{float(latest['Value']):.1f} {latest['Unit']}")
    else:
        st.info("Select 1-3 indicators from the dropdown to visualize trends")

    st.subheader("Advanced Analysis")
    tab1, tab2, tab3, tab4 = st.tabs(["Food Security", "Economic", "Health", "Progress Indicators"])
    
    with tab1:
        st.write("### Food Security Indicators")
        col1, col2 = st.columns(2)
        
        with col1:
            data = filtered_df[filtered_df['Category'] == 'Undernourishment']
            st.plotly_chart(create_chart(data, 'line', x='Year', y='Value', 
                                       title="Undernourishment Over Time"), 
                          use_container_width=True)
            
            data = filtered_df[filtered_df['Category'].isin(['Male Food Insecurity', 'Female Food Insecurity'])]
            st.plotly_chart(create_chart(data, 'area', x='Year', y='Value', color='Category',
                                       title="Food Insecurity by Gender"), 
                          use_container_width=True)
        
        with col2:
            data = filtered_df[filtered_df['Category'].isin(['Male Food Insecurity', 'Female Food Insecurity'])]
            st.plotly_chart(create_chart(data, 'bar', x='Year', y='Value', color='Category',
                                       title="Gender Comparison by Year"), 
                          use_container_width=True)
            
            latest_data = data[data['Year'] == data['Year'].max()]
            st.plotly_chart(create_chart(latest_data, 'pie', names='Category', values='Value',
                                       title="Latest Gender Distribution"), 
                          use_container_width=True)
    
    with tab2:
        st.write("### Economic Indicators")
        col1, col2 = st.columns(2)
        
        with col1:
            data = filtered_df[filtered_df['Category'] == 'GDP per capita']
            st.plotly_chart(create_chart(data, 'line', x='Year', y='Value', 
                                       title="GDP per capita Over Time"), 
                          use_container_width=True)
            
            data['Value'] = pd.to_numeric(data['Value'], errors='coerce')
            gdp_growth = data['Value'].pct_change().mean() * 100
            st.metric(
                label="Average Annual GDP Growth Rate",
                value=f"{gdp_growth:.2f}%",
                help="Calculated as the mean percentage change in GDP per capita across all years"
            )
            
            gdp_volatility = data['Value'].pct_change().std() * 100
            st.metric(
                label="GDP Growth Volatility",
                value=f"{gdp_volatility:.2f}%",
                help="Standard deviation of annual GDP growth rates"
            )
        
        with col2:
            data = filtered_df[filtered_df['Category'] == 'Political Stability']
            st.plotly_chart(create_chart(data, 'area', x='Year', y='Value',
                                       title="Political Stability Trends"), 
                          use_container_width=True)
            
            gdp = filtered_df[filtered_df['Category'] == 'GDP per capita']
            stability = filtered_df[filtered_df['Category'] == 'Political Stability']
            merged = pd.merge(gdp, stability, on='Year', suffixes=('_GDP', '_Stability'))
            fig = px.scatter(merged, x='Value_GDP', y='Value_Stability',
                           title="GDP vs Political Stability",
                           trendline="lowess")
            correlation = merged['Value_GDP'].corr(merged['Value_Stability'])
            fig.add_annotation(text=f"Correlation: {correlation:.2f}", 
                             xref="paper", yref="paper",
                             x=0.05, y=0.95, showarrow=False)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.write("### Health Indicators")
        col1, col2 = st.columns(2)
        
        with col1:
            data = filtered_df[filtered_df['Category'] == 'Obesity']
            st.plotly_chart(create_chart(data, 'line', x='Year', y='Value', 
                                       title="Obesity Trends"), 
                          use_container_width=True)
            
            obesity = filtered_df[filtered_df['Category'] == 'Obesity']
            birthweight = filtered_df[filtered_df['Category'] == 'Low Birthweight']
            merged = pd.merge(obesity, birthweight, on='Year')
            st.plotly_chart(create_chart(merged, 'scatter', 
                                       x='Value_x', y='Value_y',
                                       title="Obesity vs Birthweight"), 
                          use_container_width=True)
        
        with col2:
            data = filtered_df[filtered_df['Category'] == 'Low Birthweight']
            st.plotly_chart(create_chart(data, 'bar', x='Year', y='Value', 
                                       title="Low Birthweight by Year"), 
                          use_container_width=True)
            
            health_data = filtered_df[filtered_df['Category'].isin(['Obesity', 'Low Birthweight'])]
            st.plotly_chart(create_chart(health_data, 'box', x='Category', y='Value',
                                       title="Health Indicators Distribution"), 
                          use_container_width=True)
    
    with tab4:
        st.write("### Progress Indicators")
        col1, col2 = st.columns(2)
        
        with col1:
            latest_gdp = filtered_df[filtered_df['Category'] == 'GDP per capita'].iloc[-1]['Value']
            st.plotly_chart(create_gauge_chart(
                value=float(latest_gdp),
                title="GDP Progress",
                min_val=6000,
                max_val=15000
            ), use_container_width=True)
            
            indicators = ['Protein Supply', 'Basic Water Access', 'Political Stability']
            area_data = filtered_df[filtered_df['Category'].isin(indicators)]
            st.plotly_chart(create_chart(area_data, 'area', x='Year', y='Value', color='Category',
                                       title="Composite Indicators"), 
                          use_container_width=True)
        
        with col2:
            water_data = filtered_df[filtered_df['Category'].isin(['Safe Water Access', 'Basic Water Access'])]
            st.plotly_chart(create_chart(water_data, 'bar', x='Year', y='Value', color='Category',
                                       title="Water Access Comparison"), 
                          use_container_width=True)
            
            progress_data = filtered_df[filtered_df['Category'].isin(
                ['Protein Supply', 'Basic Water Access', 'Political Stability', 'GDP per capita'])]
            pivot_data = progress_data.pivot(index='Year', columns='Category', values='Value').corr()
            fig = px.imshow(pivot_data, text_auto=True,
                          title="Indicator Correlations")
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Developed for University of Westminster - Data Science Project Lifecycle")