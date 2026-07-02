import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()
GROQ_SECRET_KEY = os.getenv("GROQ_API_KEY")

# Page Setup
st.set_page_config(
    page_title="AI-Powered Analytics Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Style Rules for High Visibility and Modern Look
st.markdown("""
    <style>
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; }
    h1 { color: #1E3A8A; font-weight: 700; }
    
    /* Fixed Tab Visibility Issues */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1F2937 !important; /* Dark neutral base */
        color: #E5E7EB !important; /* Light text */
        border-radius: 6px 6px 0px 0px;
        padding: 10px 20px;
        border: 1px solid #374151;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #2563EB !important; /* Vivid Blue active tab */
        color: white !important; 
        font-weight: bold;
    }
    
    /* Clean status indicators */
    .status-connected { color: #10B981; font-weight: 600; font-size: 1.1rem; }
    .status-disconnected { color: #EF4444; font-weight: 600; font-size: 1.1rem; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Advanced AI Data & Trend Analytics Dashboard")
st.write("---")

# Sidebar - Credentials Status & Uploads
st.sidebar.header("📁 Credentials & Data")

# Validate Key Status Behind the Scenes (No Input Field Visible)
groq_valid = False
if GROQ_SECRET_KEY:
    try:
        test_client = Groq(api_key=GROQ_SECRET_KEY)
        test_client.chat.completions.create(
            messages=[{"role": "user", "content": "ping"}],
            model="llama-3.3-70b-versatile",
            max_tokens=5
        )
        st.sidebar.markdown('<p class="status-connected">🟢 Connected to AI</p>', unsafe_allow_html=True)
        groq_valid = True
    except Exception:
        st.sidebar.markdown('<p class="status-disconnected">🔴 Not Connected to AI / Token Expired</p>', unsafe_allow_html=True)
else:
    st.sidebar.markdown('<p class="status-disconnected">🔴 Not Connected to AI (Missing Key)</p>', unsafe_allow_html=True)

st.sidebar.write("---")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Load Dataset
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        all_cols = df.columns.tolist()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        # UI Selection Controls
        st.sidebar.subheader("📊 Visualization Properties")
        graph_type = st.sidebar.selectbox(
            "Choose Graph Type",
            ["Scatter Plot with Trendline", "Line Chart", "Bar Chart", "Pie Chart", "Histogram", "Box Plot"]
        )
        
        # Restored Structural Axis Selectors 
        if graph_type in ["Scatter Plot with Trendline", "Line Chart", "Bar Chart"]:
            x_axis = st.sidebar.selectbox("Select X-Axis Data", all_cols)
            y_axis = st.sidebar.selectbox("Select Y-Axis (Metrics)", numeric_cols)
            color_by = st.sidebar.selectbox("Color Segment (Optional)", [None] + all_cols)
        elif graph_type == "Pie Chart":
            names_col = st.sidebar.selectbox("Select Category Labels", all_cols)
            values_col = st.sidebar.selectbox("Select Values", numeric_cols)
        elif graph_type in ["Histogram", "Box Plot"]:
            x_axis = st.sidebar.selectbox("Select X-Axis Data", all_cols)
            val_col = st.sidebar.selectbox("Target Metric", numeric_cols)
            color_by = st.sidebar.selectbox("Group Color (Optional)", [None] + all_cols)

        # Focus Range (Data Slicing)
        st.sidebar.subheader("🔍 Focus Range (Data Slicing)")
        use_range = st.sidebar.checkbox("Enable Strict Window Slicing")
        
        df_filtered = df.copy()
        if use_range:
            max_rows = len(df)
            start_row, end_row = st.sidebar.slider(
                "Select Index Range Window", 
                0, max_rows, (0, min(max_rows, int(max_rows * 0.25)))
            )
            df_filtered = df.iloc[start_row:end_row]
            st.sidebar.caption(f"Showing rows {start_row} to {end_row} ({len(df_filtered)} records total)")

        # Main Layout Tabs
        tab1, tab2, tab3 = st.tabs(["📈 Visualization Framework", "📋 Data Sheet Preview", "🤖 AI Insight Assistant"])

        # TAB 1: GRAPH VIEW WITH TRENDS
        with tab1:
            st.subheader(f"Visual Trend Analysis ({graph_type})")
            st.info("💡 Pro-Tip: You can use your mouse to highlight and drag directly over any section of the chart to instantly zoom in and research that specific range.")
            
            fig = None
            title_text = f"Distribution mapping of {graph_type} across selected attributes"
            
            if graph_type == "Scatter Plot with Trendline":
                fig = px.scatter(df_filtered, x=x_axis, y=y_axis, color=color_by, 
                                 trendline="ols", template="plotly_white", title=title_text)
            elif graph_type == "Line Chart":
                fig = px.line(df_filtered, x=x_axis, y=y_axis, color=color_by, template="plotly_white", title=title_text)
            elif graph_type == "Bar Chart":
                fig = px.bar(df_filtered, x=x_axis, y=y_axis, color=color_by, barmode="group", template="plotly_white", title=title_text)
            elif graph_type == "Pie Chart":
                fig = px.pie(df_filtered, names=names_col, values=values_col, hole=0.4, template="plotly_white", title=title_text)
            elif graph_type == "Histogram":
                fig = px.histogram(df_filtered, x=x_axis, y=val_col, color=color_by, barmode="overlay", template="plotly_white", title=title_text)
            elif graph_type == "Box Plot":
                fig = px.box(df_filtered, x=x_axis, y=val_col, color=color_by, template="plotly_white", title=title_text)
            
            if fig:
                if graph_type in ["Scatter Plot with Trendline", "Line Chart", "Bar Chart"]:
                    fig.update_layout(xaxis_rangeslider_visible=True)
                fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig, use_container_width=True)

        # TAB 2: TABULAR STRUCTURAL VIEWER
        with tab2:
            st.subheader("📋 Active Tabular Frame Inspector")
            m1, m2, m3 = st.columns(3)
            m1.metric("Active Window Rows", df_filtered.shape[0])
            m2.metric("Dataset Columns", df_filtered.shape[1])
            m3.metric("Null Target Records", df_filtered.isna().sum().sum())
            st.dataframe(df_filtered, use_container_width=True)

        # TAB 3: GROQ AI INSIGHT PANEL
        with tab3:
            st.subheader("🤖 Automated Insight Generator")
            if not groq_valid:
                st.warning("AI features are inactive. Ensure a valid key is assigned to GROQ_API_KEY inside your local .env file.")
            else:
                data_summary = f"""
                Dataset Row Sample Shape: {df.shape}
                Columns Present: {list(df.columns)}
                Numerical Description Snippet:
                {df.describe().to_string()}
                """
                
                @st.cache_data(show_spinner=False)
                def get_suggested_questions(summary):
                    try:
                        client = Groq(api_key=GROQ_SECRET_KEY)
                        prompt = f"Based on this structural summary of a dataset, suggest exactly 3 short analytic research questions that a business owner could ask:\n{summary}\nProvide only the 3 questions as a plain list without introductory sentences."
                        response = client.chat.completions.create(
                            messages=[{"role": "user", "content": prompt}],
                            model="llama-3.3-70b-versatile",
                            max_tokens=150
                        )
                        return response.choices[0].message.content
                    except:
                        return "1. What are the key anomalies?\n2. What is the overall primary category correlation?\n3. What is the primary metric growth trajectory?"

                with st.spinner("Generating automated smart query suggestions..."):
                    suggestions = get_suggested_questions(data_summary)
                
                st.write("💡 **Recommended Analytical Questions for this Dataset:**")
                st.info(suggestions)
                
                user_query = st.text_input("💬 Ask the AI Assistant anything about your dataset:", placeholder="e.g., Explain the core trends hidden in this data matrix.")
                
                if user_query:
                    with st.spinner("Processing with Groq Engine..."):
                        try:
                            client = Groq(api_key=GROQ_SECRET_KEY)
                            full_system_context = f"You are a Senior Data Analytics Expert. You have access to a data overview summary: {data_summary}. Answer the user accurately, comprehensively, and format your conclusions with bullet points and modern stylistic elements."
                            
                            chat_res = client.chat.completions.create(
                                messages=[
                                    {"role": "system", "content": full_system_context},
                                    {"role": "user", "content": user_query}
                                ],
                                model="llama-3.3-70b-versatile",
                                temperature=0.3
                            )
                            st.markdown("### 📝 Analysis Output")
                            st.write(chat_res.choices[0].message.content)
                        except Exception as ai_err:
                            st.error(f"Groq API Processing error: {ai_err}")

    except Exception as parse_err:
        st.error(f"Error structuring file: {parse_err}")
else:
    st.info("ℹ️ Please upload a dataset in the panel on the left to activate visual graphing systems and AI context modules.")