
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import re

# Add backend directory to sys.path to import analyzer
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
try:
    from analyzer import run_residue_pca
except ImportError:
    st.error("Backend analyzer module not found. Check directory structure.")

st.set_page_config(page_title="NMR PCA - Picked Analysis", page_icon="📊", layout="wide")

# Styling
st.markdown("""
<style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: white;
    }
    .stTextArea > div > div > textarea {
        background-color: #1e293b;
        color: white;
        font-family: monospace;
    }
    h1, h2, h3 {
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 NMR PCA Analysis - Picked Intensities")
st.markdown("Upload your Peak Intensity table (Rows: Residues, Cols: Samples) or paste data directly.")

# --- INPUT SECTION ---
with st.container():
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("File Upload")
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'])
        
    with col2:
        st.subheader("Paste Data")
        paste_data = st.text_area("Paste text (Space/Tab/Comma separated)", height=150,
                                  placeholder="ResID  Int1  Int2  Int3 ...\n10     100   90    80\n...")

# --- PARSING ---
data_to_analyze = None
feature_names = None

if st.button("Run Analysis", type="primary"):
    residue_data = []
    
    # 1. Handle File Upload
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Assume 1st col is ID, rest are features
            # data_to_analyze = df.values.tolist() # This might be mixed types
            # Convert to list of lists [id, val, val...]
            # Treat all columns as string for ID first, then convert features
            
            # Extract headers
            feature_names = df.columns[1:].tolist()
            
            for idx, row in df.iterrows():
                res_id = str(row.iloc[0])
                try:
                    vals = [float(x) for x in row.iloc[1:]]
                    residue_data.append([res_id] + vals)
                except ValueError:
                    continue
                    
        except Exception as e:
            st.error(f"Error parsing file: {e}")

    # 2. Handle Paste Data (Priority if both exists? Or Append? Let's use Paste if File not present, or override)
    # Actually let's check paste_data first if file is None
    if paste_data and not residue_data:
        lines = paste_data.strip().split('\n')
        # Check header
        first_line = lines[0].strip()
        parts = re.split(r'[,\s]+', first_line)
        is_header = False
        if len(parts) >= 2:
            try:
                [float(v) for v in parts[1:]]
            except ValueError:
                is_header = True
                feature_names = parts[1:]
        
        start_idx = 1 if is_header else 0
        for line in lines[start_idx:]:
            if not line.strip(): continue
            parts = re.split(r'[,\s]+', line.strip())
            if len(parts) < 2: continue
            
            res_id = parts[0]
            try:
                vals = [float(v) for v in parts[1:]]
                residue_data.append([res_id] + vals)
                
                if feature_names is None:
                    feature_names = [f"Feature_{i+1}" for i in range(len(vals))]
            except ValueError:
                continue

    if not residue_data:
        st.warning("No valid data found. Please upload a file or paste text.")
    else:
        # Run PCA
        try:
            result = run_residue_pca(residue_data, feature_names=feature_names)
            
            if "error" in result:
                st.error(result["error"])
            else:
                # --- RESULTS ---
                st.session_state['pca_result'] = result
                st.success("Analysis Complete!")
                
        except Exception as e:
            st.error(f"Analysis Failed: {e}")

# --- DISPLAY RESULTS ---
if 'pca_result' in st.session_state:
    res = st.session_state['pca_result']
    
    # 1. Explained Variance
    st.divider()
    st.subheader("Explained Variance")
    
    var_df = pd.DataFrame({
        "PC": [f"PC{i+1}" for i in range(len(res['variance_ratio']))],
        "Variance": [v * 100 for v in res['variance_ratio']]
    })
    
    fig_var = px.bar(var_df, x='PC', y='Variance', text_auto='.1f', 
                     color='PC', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_var.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_var, use_container_width=True)
    
    # 2. 3D Plot & Outliers
    if len(res['results']) >= 3:
        st.divider()
        col3, col4 = st.columns([2, 1])
        
        with col3:
            st.subheader("3D Residue Space (PC1-PC2-PC3)")
            
            scores1 = res['results'][0]['scores']
            scores2 = res['results'][1]['scores']
            scores3 = res['results'][2]['scores']
            ids = res['residue_nos']
            
            # Calculate Distance and Outliers
            dists = [np.sqrt(s1**2 + s2**2 + s3**2) for s1, s2, s3 in zip(scores1, scores2, scores3)]
            threshold = 3.0
            colors = ['red' if d > threshold else 'cyan' for d in dists]
            
            df_3d = pd.DataFrame({
                'PC1': scores1, 'PC2': scores2, 'PC3': scores3, 'Residue': ids, 'Distance': dists, 'Color': colors
            })
            
            fig_3d = go.Figure(data=[go.Scatter3d(
                x=df_3d['PC1'], y=df_3d['PC2'], z=df_3d['PC3'],
                mode='markers+text',
                text=[f"Res {r}" if c == 'red' else '' for r, c in zip(ids, colors)],
                textposition='top center',
                marker=dict(size=5, color=colors, opacity=0.8)
            )])
            fig_3d.update_layout(
                scene=dict(xaxis_title='PC1', yaxis_title='PC2', zaxis_title='PC3', bgcolor='rgba(0,0,0,0)'),
                paper_bgcolor='rgba(0,0,0,0)', font_color="white", margin=dict(l=0, r=0, b=0, t=0)
            )
            st.plotly_chart(fig_3d, use_container_width=True)
            
        with col4:
            st.subheader("🚨 Outliers (Dist > 3.0)")
            outliers = df_3d[df_3d['Distance'] > threshold].copy()
            if outliers.empty:
                st.info("No significant outliers detected.")
            else:
                outliers = outliers[['Residue', 'PC1', 'PC2', 'Distance']].sort_values('Distance', ascending=False)
                st.dataframe(outliers.style.format("{:.2f}", subset=['PC1', 'PC2', 'Distance']), hide_index=True)

    # 3. Loadings (Feature Contribution)
    st.divider()
    st.subheader("📊 Feature Contributions (Loadings)")
    
    cols = st.columns(3)
    for i in range(min(3, len(res['results']))):
        with cols[i]:
            pc_idx = res['results'][i]['pc_index']
            loadings = res['results'][i]['loadings'] # Dict
            
            # To DataFrame
            l_df = pd.DataFrame(list(loadings.items()), columns=['Feature', 'Weight'])
            l_df['AbsWeight'] = l_df['Weight'].abs()
            l_df = l_df.sort_values('AbsWeight', ascending=False)
            
            fig_load = px.bar(l_df, x='Feature', y='Weight', 
                              title=f"PC{pc_idx} Loadings",
                              color='Weight', color_continuous_scale='RdBu')
            fig_load.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=False)
            st.plotly_chart(fig_load, use_container_width=True)

