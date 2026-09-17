import json
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from dataset_profiler import DatasetProfiler

st.set_page_config(page_title="Dataset Profiling Engine", page_icon="📊", layout="wide")

st.title("📊 Dataset Profiling Engine")
st.write("Upload a dataset to automatically analyze its structure, quality, statistics and distributions.")

with st.sidebar:
    st.header("📁 Upload Dataset")
    uploaded = st.file_uploader("Choose CSV, Excel or JSON", type=["csv","xlsx","xls","json"])

if uploaded is None:
    st.info("👆 Upload a CSV, Excel, or JSON file from the sidebar to begin.")
    a,b,c,d=st.columns(4)
    a.metric("Schema","✓"); b.metric("Missing Values","✓"); c.metric("Duplicates","✓"); d.metric("Statistics","✓")
    st.stop()

try:
    name=uploaded.name.lower()
    if name.endswith(".csv"): df=pd.read_csv(uploaded)
    elif name.endswith((".xlsx",".xls")): df=pd.read_excel(uploaded)
    else: df=pd.read_json(uploaded)
    if df.empty: st.error("The dataset is empty."); st.stop()
except Exception as e:
    st.error(f"Could not read dataset: {e}"); st.stop()

p=DatasetProfiler(df); p.generate_profile()
missing=int(df.isna().sum().sum()); duplicates=p.duplicates()["Duplicate Rows"]

st.success(f"Loaded: {uploaded.name}")
m1,m2,m3,m4=st.columns(4)
m1.metric("Rows",f"{len(df):,}"); m2.metric("Columns",f"{len(df.columns):,}")
m3.metric("Missing Values",f"{missing:,}"); m4.metric("Duplicate Rows",f"{duplicates:,}")

tabs=st.tabs(["📋 Overview","👀 Preview","🧬 Schema","⚠️ Missing Values","🔁 Duplicates","🔢 Unique Values","📊 Statistics","📈 Distributions"])

with tabs[0]:
    st.subheader("Dataset Overview")
    st.write(f"**File:** {uploaded.name}")
    st.write(f"**Numeric columns:** {len(df.select_dtypes(include='number').columns)}")
    st.write(f"**Categorical columns:** {len(df.select_dtypes(include=['object','category','bool']).columns)}")
    st.write(f"**Memory usage:** {df.memory_usage(deep=True).sum()/1024:.2f} KB")

with tabs[1]:
    st.dataframe(df.head(100), use_container_width=True, height=500)

with tabs[2]:
    st.dataframe(p.schema(), use_container_width=True, hide_index=True)

with tabs[3]:
    mv=p.missing_values()
    st.dataframe(mv,use_container_width=True,hide_index=True)
    st.success("No missing values detected.") if not (mv["Missing Values"]>0).any() else st.warning("Missing values were detected.")

with tabs[4]:
    st.metric("Duplicate Rows",duplicates)
    if duplicates: st.dataframe(df[df.duplicated(keep=False)],use_container_width=True)
    else: st.success("No duplicate records detected.")

with tabs[5]:
    st.dataframe(p.unique_values(),use_container_width=True,hide_index=True)

with tabs[6]:
    st.subheader("Numerical Statistics")
    ns=p.numeric_statistics()
    st.dataframe(ns,use_container_width=True,hide_index=True) if not ns.empty else st.info("No numerical columns.")
    st.subheader("Categorical Summary")
    cs=p.categorical_summary()
    st.dataframe(cs,use_container_width=True,hide_index=True) if not cs.empty else st.info("No categorical columns.")

with tabs[7]:
    nums=df.select_dtypes(include="number").columns.tolist()
    if not nums: st.info("No numerical columns available.")
    else:
        col=st.selectbox("Select numerical column",nums)
        fig,ax=plt.subplots(figsize=(9,5))
        ax.hist(df[col].dropna(),bins=20,edgecolor="black")
        ax.set_title(f"Distribution of {col}"); ax.set_xlabel(col); ax.set_ylabel("Frequency")
        st.pyplot(fig); plt.close(fig)

st.divider()
st.subheader("📥 Export Report")
st.download_button("Download JSON Report",p.json_report(),"dataset_profile_report.json","application/json")
