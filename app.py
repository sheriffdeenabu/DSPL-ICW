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

