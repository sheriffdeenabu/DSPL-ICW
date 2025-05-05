# Importing relevant libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import requests
from io import BytesIO
import base64

# Configuring initial page
st.set_page_config(page_title="Sri Lanka Food Security Dashboard", layout="wide")

# Converting image to base64
def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# Load the Sri Lankan flag with a load spinner
def load_flag_image():
    flag_url = "https://raw.githubusercontent.com/sheriffdeenabu/DSPL-ICW/main/Images/download.png"
    
    with st.spinner('Loading flag image...'):
        try:
            response = requests.get(flag_url)
            response.raise_for_status()  
            flag_image = Image.open(BytesIO(response.content))
            return flag_image
        except Exception as e:
            st.error(f"Error loading flag image: {str(e)}")
            return None

@st.cache_data
def load_data():
    with st.spinner('Loading and processing data...'):
        try:
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
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return pd.DataFrame()

def create_gauge_chart(value, title, min_val, max_val):
    with st.spinner(f'Creating {title} gauge chart...'):
        if isinstance(value, str) and 'k' in value:
            numeric_value = float(value.replace('k', '')) * 1000
        else:
            numeric_value = float(value)
            
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=numeric_value,
            title={'text': title},
            number={
                'valueformat': ",.0f",
                'suffix': "",
                'font': {'size': 24}    
            },
            gauge={
                'axis': {
                    'range': [min_val, max_val],
                    'tickformat': ",.0f"
                },
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
            margin=dict(l=20, r=20, t=50, b=10),
            autosize=True
        )
        return fig

def create_chart(data, chart_type, x=None, y=None, names=None, values=None, title=None, color=None):
    with st.spinner(f'Creating {chart_type} chart: {title or ""}'):
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

def show_dataset_info(df):
    st.title("Dataset Information")
    
    st.markdown("""
    ### Overview
    This dataset contains various food security and socioeconomic indicators for Sri Lanka from 2000-2022.
    """)
    
    st.markdown("### Dataset Summary")
    st.dataframe(df.head(10))
    
    st.markdown("### Column Descriptions")
    col_info = pd.DataFrame({
        'Column': ['Iso3', 'Item', 'Element', 'Year', 'Unit', 'Value', 'Category'],
        'Description': [
            'Country code (LKA for Sri Lanka)',
            'The specific indicator being measured',
            'Type of measurement (usually "Value")',
            'Year of measurement',
            'Unit of measurement',
            'Numerical value of the measurement',
            'Simplified category name for the indicator'
        ]
    })
    st.table(col_info)
    
def show_project_info():
    st.title("About the Sri Lanka Food Security Dashboard")
    st.markdown("""
    ### Dashboard Overview
    
    This interactive dashboard provides comprehensive insights into Sri Lanka's food security and related socioeconomic indicators. 
    The visualization tool contains:
    
    - **Trend Analysis**: Customizable multi-indicator trends over time with the option to select up to three indicators
    - **Advanced Analysis** with four specialized tabs:
      1. **Food Security**: Undernourishment trends, gender disparities in food insecurity
      2. **Economic**: GDP evolution, political stability correlations
      3. **Health**: Obesity patterns, low birthweight statistics
      4. **Progress Indicators**: Composite metrics with gauge charts and correlation matrices      
    """)

def show_student_info():
    st.title("Student Information")
    st.markdown("""
    <div style='text-align: left;'>
        <p style='font-size: 20px;'><b>Abdullah Sheriffdeen</b></p>
        <p>Student ID: 20222221 | w1985555</p>
        <p>Email: sheriffdeenabdullah@gmail.com | abdullah.20222221@iit.ac.lk</p>
        <p>University of Westminster | Informatics Institute of Technology</p>
    </div>
    """, unsafe_allow_html=True)

def show_dashboard(df):
    # Display Sri Lanka flag with loading state
    with st.spinner('Loading dashboard...'):
        flag = load_flag_image()
        if flag:
            flag_base64 = image_to_base64(flag)
            
            st.markdown(f"""
            <div style="display: flex; justify-content: center; align-items: center; flex-direction: column; width: 100%;">
                <img src="data:image/png;base64,{flag_base64}" 
                     width="250" style="margin-bottom: 10px;">
                <h1 style="text-align: center; margin: 0; padding: 0;">Sri Lanka Food Security Indicators</h1>
            </div>
            <hr style='margin: 20px 0; border: 0.5px solid #f0f2f6;'>
            """, unsafe_allow_html=True)
            
            if not df.empty:
                # Year range selector
                st.markdown("### Select the required years")
                min_year, max_year = int(df['Year'].min()), int(df['Year'].max())
                year_range = st.slider(
                    "Year range selector",
                    min_year, 
                    max_year, 
                    (min_year, max_year),
                    label_visibility="collapsed"
                )
                filtered_df = df[(df['Year'].astype(int) >= year_range[0]) & (df['Year'].astype(int) <= year_range[1])]
                
                st.subheader("Trend Analysis")
                categories = st.multiselect(
                    "Select Indicators (Max 3)", 
                    filtered_df['Category'].unique(),
                    default=None,
                    max_selections=3
                )

                if categories:
                    with st.spinner('Generating trend visualization...'):
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
                    st.info("Select up to three indicators from the dropdown to visualize and analyze")

                st.subheader("Additional Analysis")
                tab1, tab2, tab3, tab4 = st.tabs(["Food Security", "Economic", "Health", "Progress Indicators"])
                
                with tab1:
                    st.write("### Food Security Indicators")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        data = filtered_df[filtered_df['Category'] == 'Undernourishment'].copy()
                        st.plotly_chart(create_chart(data, 'line', x='Year', y='Value', 
                                                   title="Undernourishment Over Time"), 
                                      use_container_width=True)
                        
                        data = filtered_df[filtered_df['Category'].isin(['Male Food Insecurity', 'Female Food Insecurity'])].copy()
                        st.plotly_chart(create_chart(data, 'area', x='Year', y='Value', color='Category',
                                                   title="Food Insecurity by Gender"), 
                                      use_container_width=True)
                    
                    with col2:
                        data = filtered_df[filtered_df['Category'].isin(['Male Food Insecurity', 'Female Food Insecurity'])].copy()
                        st.plotly_chart(create_chart(data, 'bar', x='Year', y='Value', color='Category',
                                                   title="Gender Comparison by Year"), 
                                      use_container_width=True)
                        
                        latest_data = data[data['Year'] == data['Year'].max()].copy()
                        st.plotly_chart(create_chart(latest_data, 'pie', names='Category', values='Value',
                                                   title="Latest Gender Distribution"), 
                                      use_container_width=True)
                
                with tab2:
                    st.write("### Economic Indicators")
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        data = filtered_df[filtered_df['Category'] == 'GDP per capita'].copy()
                        st.plotly_chart(create_chart(data, 'line', x='Year', y='Value', 
                                                   title="GDP per capita Over Time"), 
                                      use_container_width=True)
                        
                        data.loc[:, 'Value'] = pd.to_numeric(data['Value'], errors='coerce')
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
                        data = filtered_df[filtered_df['Category'] == 'Political Stability'].copy()
                        st.plotly_chart(create_chart(data, 'area', x='Year', y='Value',
                                                   title="Political Stability Trends"), 
                                      use_container_width=True)
                        
                        gdp = filtered_df[filtered_df['Category'] == 'GDP per capita'].copy()
                        stability = filtered_df[filtered_df['Category'] == 'Political Stability'].copy()
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
                        data = filtered_df[filtered_df['Category'] == 'Obesity'].copy()
                        st.plotly_chart(create_chart(data, 'line', x='Year', y='Value', 
                                                   title="Obesity Trends"), 
                                      use_container_width=True)
                        
                        obesity = filtered_df[filtered_df['Category'] == 'Obesity'].copy()
                        birthweight = filtered_df[filtered_df['Category'] == 'Low Birthweight'].copy()
                        merged = pd.merge(obesity, birthweight, on='Year')
                        st.plotly_chart(create_chart(merged, 'scatter', 
                                                   x='Value_x', y='Value_y',
                                                   title="Obesity vs Birthweight"), 
                                      use_container_width=True)
                    
                    with col2:
                        data = filtered_df[filtered_df['Category'] == 'Low Birthweight'].copy()
                        st.plotly_chart(create_chart(data, 'bar', x='Year', y='Value', 
                                                   title="Low Birthweight by Year"), 
                                      use_container_width=True)
                        
                        health_data = filtered_df[filtered_df['Category'].isin(['Obesity', 'Low Birthweight'])].copy()
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
                        area_data = filtered_df[filtered_df['Category'].isin(indicators)].copy()
                        st.plotly_chart(create_chart(area_data, 'area', x='Year', y='Value', color='Category',
                                                   title="Composite Indicators"), 
                                      use_container_width=True)
                    
                    with col2:
                        water_data = filtered_df[filtered_df['Category'].isin(['Safe Water Access', 'Basic Water Access'])].copy()
                        st.plotly_chart(create_chart(water_data, 'bar', x='Year', y='Value', color='Category',
                                                   title="Water Access Comparison"), 
                                      use_container_width=True)
                        
                        progress_data = filtered_df[filtered_df['Category'].isin(
                            ['Protein Supply', 'Basic Water Access', 'Political Stability', 'GDP per capita'])].copy()
                        pivot_data = progress_data.pivot(index='Year', columns='Category', values='Value').corr()
                        fig = px.imshow(pivot_data, text_auto=True,
                                      title="Indicator Correlations")
                        st.plotly_chart(fig, use_container_width=True)

def main():
    # Load data once at the start
    df = load_data()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Select a page",
        ["Dashboard", "Project Info", "Student Info", "Dataset Info"],
        label_visibility="visible"
    )

    if page == "Dashboard":
        show_dashboard(df)
    elif page == "Project Info":
        show_project_info()
    elif page == "Student Info":
        show_student_info()
    elif page == "Dataset Info":
        if not df.empty:
            show_dataset_info(df)
        else:
            st.error("Failed to load dataset")

    st.markdown("---")
    st.caption("Developed for University of Westminster - Data Science Project Lifecycle")

if __name__ == "__main__":
    main()