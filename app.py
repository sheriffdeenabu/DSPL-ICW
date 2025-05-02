import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuration
st.set_page_config(page_title="Sri Lanka Food Security Dashboard", layout="wide")

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

df = load_data()

def create_gauge_chart(value, title, min_val, max_val):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
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
    fig.update_layout(height=300, margin=dict(t=50, b=10))
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

