import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from models.predict import EnergyPredictor
from models.anomaly import AnomalyDetector
from models.optimizer import EnergyOptimizer
from models.utils import DataProcessor, ReportGenerator
from models.real_time_data import RealTimeDataGenerator
from models.auth import Auth
import json
import os

# Custom CSS for light theme
LIGHT_THEME = """
<style>
    .login-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    .stTextInput input {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        color: #333333;
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    .stTab {
        background-color: #ffffff;
    }
</style>
"""

# Page configuration
st.set_page_config(
    page_title="Smart Energy Management System",
    page_icon="⚡",
    layout="wide"
)

# Initialize authentication
auth = Auth()

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'real_time_data' not in st.session_state:
    st.session_state.real_time_data = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

def login_page():
    # Apply light theme CSS
    st.markdown(LIGHT_THEME, unsafe_allow_html=True)
    
    # Main container with styling
    st.markdown(
        """
        <div class="login-container">
            <h1 style="text-align: center; margin-bottom: 2rem;">🔐 Smart Energy Management System</h1>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Login", key="login_button", use_container_width=True):
                success, result = auth.login(email, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_info = {
                        "email": email,
                        "name": result["name"]
                    }
                    st.rerun()
                else:
                    st.error(result)
    
    with tab2:
        st.subheader("Register")
        name = st.text_input("Name", key="register_name")
        email = st.text_input("Email", key="register_email")
        password = st.text_input("Password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Register", key="register_button", use_container_width=True):
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = auth.register(email, password, name)
                    if success:
                        st.success(message)
                        st.info("Please login with your credentials")
                    else:
                        st.error(message)

def show_user_profile():
    if 'user_info' in st.session_state:
        with st.sidebar:
            st.write("---")
            st.write(f"👤 Logged in as: {st.session_state.user_info.get('name', 'User')}")
            if st.button("Logout"):
                auth.logout()
                st.session_state.authenticated = False
                st.rerun()

def main_dashboard():
    show_user_profile()
    
    # Sidebar
    st.sidebar.title("⚡ Smart Energy Dashboard")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigation",
        ["📊 Overview", "🔮 Predictions", "🚨 Anomalies", "💡 Optimization", "📈 Reports"]
    )
    
    # Data source selection
    data_source = st.sidebar.radio(
        "Select Data Source",
        ["📊 Real-time Data", "📁 Upload CSV"]
    )
    
    df = None
    
    if data_source == "📊 Real-time Data":
        df = get_real_time_data()
        st.sidebar.info("Using real-time generated data for the last 7 days")
        
        # Add auto-refresh button
        if st.sidebar.button("🔄 Refresh Data"):
            st.session_state.real_time_data = None
            st.rerun()
            
    else:
        # File uploader
        uploaded_file = st.sidebar.file_uploader("Upload Energy Data (CSV)", type=["csv"])
        if uploaded_file:
            try:
                # Process data
                data_processor = DataProcessor()
                df = data_processor.process_uploaded_file(uploaded_file)
            except Exception as e:
                st.error(f"Error processing data: {str(e)}")
    
    if df is not None:
        if page == "📊 Overview":
            show_overview(df)
        elif page == "🔮 Predictions":
            show_predictions(df)
        elif page == "🚨 Anomalies":
            show_anomalies(df)
        elif page == "💡 Optimization":
            show_optimization(df)
        elif page == "📈 Reports":
            show_reports(df)
    else:
        if data_source == "📁 Upload CSV":
            st.info("Please upload a CSV file to view the dashboard")

def show_overview(df):
    st.title("📊 Energy Consumption Overview")
    
    # Real-time metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Consumption", f"{df['consumption'].iloc[-1]:.2f} kWh")
    with col2:
        st.metric("Daily Average", f"{df['consumption'].mean():.2f} kWh")
    with col3:
        st.metric("Peak Consumption", f"{df['consumption'].max():.2f} kWh")
    
    # Interactive consumption chart
    fig = px.line(df, x='timestamp', y='consumption', 
                  title='Energy Consumption Over Time')
    st.plotly_chart(fig, use_container_width=True)
    
    # Consumption by hour
    df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
    hourly_avg = df.groupby('hour')['consumption'].mean()
    fig = px.bar(x=hourly_avg.index, y=hourly_avg.values,
                 title='Average Consumption by Hour')
    st.plotly_chart(fig, use_container_width=True)

def show_predictions(df):
    st.title("🔮 Energy Consumption Predictions")
    
    predictor = EnergyPredictor()
    forecast = predictor.predict_consumption(df)
    
    # Plot actual vs predicted
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['consumption'],
                            name='Actual', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=forecast['timestamp'], y=forecast['prediction'],
                            name='Predicted', line=dict(color='red')))
    fig.update_layout(title='Actual vs Predicted Consumption')
    st.plotly_chart(fig, use_container_width=True)
    
    # Show prediction metrics
    st.subheader("Prediction Metrics")
    metrics = predictor.evaluate_predictions(df, forecast)
    st.json(metrics)

def show_anomalies(df):
    st.title("🚨 Anomaly Detection")
    
    detector = AnomalyDetector()
    anomalies = detector.detect_anomalies(df)
    
    # Plot anomalies
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['consumption'],
                            name='Normal', mode='lines'))
    fig.add_trace(go.Scatter(x=anomalies['timestamp'], y=anomalies['consumption'],
                            name='Anomaly', mode='markers', marker=dict(color='red')))
    fig.update_layout(title='Detected Anomalies')
    st.plotly_chart(fig, use_container_width=True)
    
    # Show anomaly details
    st.subheader("Anomaly Details")
    st.dataframe(anomalies)

def show_optimization(df):
    st.title("💡 Energy Optimization")
    
    optimizer = EnergyOptimizer()
    recommendations = optimizer.get_recommendations(df)
    
    st.subheader("Optimization Recommendations")
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")
    
    # Show potential savings
    savings = optimizer.calculate_potential_savings(df)
    st.subheader("Potential Savings")
    st.metric("Monthly Savings", f"₹{savings['monthly']:.2f}")
    st.metric("Annual Savings", f"₹{savings['annual']:.2f}")

def show_reports(df):
    st.title("📈 Energy Reports")
    
    report_generator = ReportGenerator()
    
    # Generate different types of reports
    report_type = st.selectbox(
        "Select Report Type",
        ["Daily Report", "Weekly Report", "Monthly Report", "Custom Period"]
    )
    
    try:
        if report_type == "Custom Period":
            start_date = st.date_input("Start Date")
            end_date = st.date_input("End Date")
            if start_date > end_date:
                st.error("End date must be after start date")
                return
            report = report_generator.generate_custom_report(df, start_date, end_date)
        else:
            report = report_generator.generate_report(df, report_type)
        
        # Display report
        st.subheader("Report Summary")
        
        # Display statistics
        stats = report['statistics']
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Consumption", f"{stats['total_consumption']:.2f} kWh")
        with col2:
            st.metric("Average Consumption", f"{stats['average_consumption']:.2f} kWh")
        with col3:
            st.metric("Peak Consumption", f"{stats['peak_consumption']:.2f} kWh")
        with col4:
            st.metric("Min Consumption", f"{stats['min_consumption']:.2f} kWh")
        
        # Display time period
        st.write(f"Time Period: {stats['time_period']['start']} to {stats['time_period']['end']}")
        
        # Create tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Charts", "📋 Detailed Data", "📈 Analysis", "💡 Insights"])
        
        with tab1:
            st.subheader("Consumption Patterns")
            
            # Hourly consumption chart with trend line
            hourly_data = df.copy()
            hourly_data['hour'] = pd.to_datetime(hourly_data['timestamp']).dt.hour
            hourly_avg = hourly_data.groupby('hour')['consumption'].agg(['mean', 'min', 'max']).reset_index()
            
            fig1 = go.Figure()
            fig1.add_trace(go.Bar(
                x=hourly_avg['hour'],
                y=hourly_avg['mean'],
                name='Average Consumption',
                marker_color='rgb(55, 83, 109)'
            ))
            fig1.add_trace(go.Scatter(
                x=hourly_avg['hour'],
                y=hourly_avg['max'],
                name='Maximum',
                line=dict(color='firebrick', width=1, dash='dash'),
                mode='lines'
            ))
            fig1.add_trace(go.Scatter(
                x=hourly_avg['hour'],
                y=hourly_avg['min'],
                name='Minimum',
                line=dict(color='royalblue', width=1, dash='dash'),
                mode='lines'
            ))
            fig1.update_layout(
                title='Hourly Consumption Pattern with Min/Max Range',
                xaxis_title='Hour of Day',
                yaxis_title='Consumption (kWh)',
                xaxis=dict(tickmode='linear', tick0=0, dtick=1),
                hovermode='x unified'
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Daily consumption trend with moving average
            daily_data = df.copy()
            daily_data['date'] = pd.to_datetime(daily_data['timestamp']).dt.date
            daily_consumption = daily_data.groupby('date')['consumption'].sum().reset_index()
            daily_consumption['moving_avg'] = daily_consumption['consumption'].rolling(window=3, min_periods=1).mean()
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=daily_consumption['date'],
                y=daily_consumption['consumption'],
                name='Daily Consumption',
                line=dict(color='rgb(55, 83, 109)')
            ))
            fig2.add_trace(go.Scatter(
                x=daily_consumption['date'],
                y=daily_consumption['moving_avg'],
                name='3-Day Moving Average',
                line=dict(color='firebrick', width=2, dash='dash')
            ))
            fig2.update_layout(
                title='Daily Consumption Trend with Moving Average',
                xaxis_title='Date',
                yaxis_title='Total Consumption (kWh)',
                hovermode='x unified'
            )
            st.plotly_chart(fig2, use_container_width=True)
            
            # Heatmap of consumption by hour and day
            df['day'] = pd.to_datetime(df['timestamp']).dt.date
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
            heatmap_data = df.pivot_table(values='consumption', index='hour', columns='day', aggfunc='mean')
            
            fig3 = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Viridis',
                colorbar=dict(title='Consumption (kWh)')
            ))
            fig3.update_layout(
                title='Consumption Heatmap by Hour and Day',
                xaxis_title='Date',
                yaxis_title='Hour of Day'
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        with tab2:
            st.subheader("Detailed Consumption Data")
            
            # Show raw data with formatting
            st.write("Hourly Consumption Data")
            df_display = df.copy()
            df_display['timestamp'] = pd.to_datetime(df_display['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(
                df_display.style.format({'consumption': '{:.2f}'})
            )
            
            # Summary statistics
            st.subheader("Summary Statistics")
            summary_stats = df['consumption'].describe()
            st.dataframe(
                summary_stats.to_frame()
                .style.format('{:.2f}')
            )
        
        with tab3:
            st.subheader("Consumption Analysis")
            
            # Peak hours analysis
            peak_hours = df[df['consumption'] > df['consumption'].mean() + df['consumption'].std()]
            st.write(f"Number of peak consumption hours: {len(peak_hours)}")
            
            # Efficiency analysis
            avg_consumption = df['consumption'].mean()
            efficiency = (1 - (df['consumption'] - avg_consumption).abs() / avg_consumption) * 100
            st.write(f"Average efficiency: {efficiency.mean():.2f}%")
            
            # Cost analysis
            cost_per_kwh = 10
            total_cost = df['consumption'].sum() * cost_per_kwh
            st.write(f"Estimated total cost: Rs. {total_cost:.2f}")
            
            # Load factor analysis
            load_factor = (df['consumption'].mean() / df['consumption'].max()) * 100
            st.write(f"Load factor: {load_factor:.2f}%")
            
            # Daily variation analysis
            daily_variation = ((df['consumption'].max() - df['consumption'].min()) / df['consumption'].mean()) * 100
            st.write(f"Daily variation: {daily_variation:.2f}%")
        
        with tab4:
            st.subheader("Energy Insights")
            
            # Peak demand insights
            peak_time = df.loc[df['consumption'].idxmax(), 'timestamp']
            st.write(f"📊 Peak demand occurred at: {peak_time}")
            
            # Cost-saving opportunities
            off_peak_hours = df[df['consumption'] < df['consumption'].mean() - df['consumption'].std()]
            potential_savings = (df['consumption'].mean() - off_peak_hours['consumption'].mean()) * cost_per_kwh
            st.write(f"💰 Potential cost savings by shifting load to off-peak hours: Rs. {potential_savings:.2f} per hour")
            
            # Efficiency recommendations
            if load_factor < 60:
                st.write("⚠️ Low load factor detected. Consider implementing load management strategies.")
            if daily_variation > 50:
                st.write("⚠️ High daily variation detected. Consider implementing demand response programs.")
            
            # Sustainability insights
            co2_per_kwh = 0.82  # kg CO2 per kWh (India average)
            total_co2 = df['consumption'].sum() * co2_per_kwh
            st.write(f"🌱 Estimated CO2 emissions: {total_co2:.2f} kg")
        
        # Generate PDF report
        pdf_path = report_generator.generate_pdf_report(report, f"energy_report_{datetime.now().strftime('%Y%m%d')}.pdf")
        
        # Generate text report
        text_report = f"""ENERGY CONSUMPTION REPORT
===========================

1. Report Details
----------------
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Report Type: {report_type}

2. Summary Statistics
-------------------
Total Consumption: {stats['total_consumption']:.2f} kWh
Average Consumption: {stats['average_consumption']:.2f} kWh
Peak Consumption: {stats['peak_consumption']:.2f} kWh
Minimum Consumption: {stats['min_consumption']:.2f} kWh
Time Period: {stats['time_period']['start']} to {stats['time_period']['end']}

3. Hourly Analysis
----------------
"""
        # Add hourly data
        hourly_data = df.copy()
        hourly_data['hour'] = pd.to_datetime(hourly_data['timestamp']).dt.hour
        hourly_summary = hourly_data.groupby('hour')['consumption'].agg(['mean', 'sum']).reset_index()
        for _, row in hourly_summary.iterrows():
            text_report += f"Hour {row['hour']}: {row['mean']:.2f} kWh (avg), {row['sum']:.2f} kWh (total)\n"

        text_report += f"""
4. Consumption Patterns
---------------------
Number of peak consumption hours: {len(peak_hours)}
Average efficiency: {efficiency.mean():.2f}%
Load factor: {load_factor:.2f}%
Daily variation: {daily_variation:.2f}%

5. Cost Analysis
---------------
Estimated total cost: Rs. {total_cost:.2f}
Potential cost savings: Rs. {potential_savings:.2f} per hour

6. Environmental Impact
---------------------
Estimated CO2 emissions: {total_co2:.2f} kg

7. Detailed Analysis
------------------
Peak Demand:
- Time: {peak_time}
- Value: {df['consumption'].max():.2f} kWh

Off-Peak Analysis:
- Average off-peak consumption: {off_peak_hours['consumption'].mean():.2f} kWh
- Number of off-peak hours: {len(off_peak_hours)}
- Potential savings per hour: Rs. {potential_savings:.2f}

8. Recommendations
----------------
"""
        if load_factor < 60:
            text_report += "• Implement load management strategies to improve load factor\n"
        if daily_variation > 50:
            text_report += "• Consider implementing demand response programs to reduce daily variation\n"
        if potential_savings > 0:
            text_report += "• Shift load to off-peak hours to reduce costs\n"
        if total_co2 > 0:
            text_report += "• Consider implementing energy efficiency measures\n"
        
        text_report += """
9. Additional Insights
--------------------
"""
        # Add trend analysis
        daily_data = df.copy()
        daily_data['date'] = pd.to_datetime(daily_data['timestamp']).dt.date
        daily_consumption = daily_data.groupby('date')['consumption'].sum()
        trend = daily_consumption.pct_change().mean() * 100
        text_report += f"• Daily consumption trend: {trend:.2f}%\n"
        
        # Add peak hour analysis
        peak_hour = hourly_summary.loc[hourly_summary['mean'].idxmax()]
        text_report += f"• Peak consumption hour: {peak_hour['hour']} ({peak_hour['mean']:.2f} kWh)\n"
        
        # Add efficiency analysis
        text_report += f"• System efficiency: {efficiency.mean():.2f}%\n"
        
        # Add cost analysis
        text_report += f"• Cost per kWh: Rs. {cost_per_kwh}\n"
        text_report += f"• Total potential savings: Rs. {potential_savings * len(off_peak_hours):.2f}\n"
        
        # Create download buttons
        col1, col2 = st.columns(2)
        with col1:
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_file,
                    file_name=f"energy_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
        with col2:
            st.download_button(
                label="📥 Download Text Report",
                data=text_report,
                file_name=f"energy_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")

def get_real_time_data():
    """Get or update real-time data"""
    current_time = datetime.now()
    
    # Initialize or update data every hour
    if (st.session_state.real_time_data is None or 
        st.session_state.last_update is None or 
        (current_time - st.session_state.last_update).total_seconds() > 3600):
        
        generator = RealTimeDataGenerator()
        st.session_state.real_time_data = generator.generate_real_time_data()
        st.session_state.last_update = current_time
    
    return st.session_state.real_time_data

def main():
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Check authentication state
    if not st.session_state.authenticated:
        login_page()
    else:
        main_dashboard()

if __name__ == "__main__":
    main()
