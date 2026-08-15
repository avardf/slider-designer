import streamlit as st
import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ➜  WebApp git:(main) ✗ uv run streamlit run app.py --server.runOnSave true

st.set_page_config(page_title="Slider Segment Designer", layout="wide")

# Minimal top padding
st.markdown("""
    <style>
        .block-container {padding-top: 1.5rem !important;}
        h1 {margin: 0 !important; padding: 0 !important;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center; margin:0;'>🔧 Slider Segment Designer</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#aaa; margin-top:0;'>Configure parameters below</p>", unsafe_allow_html=True)

st.markdown("""
    <style>
        section[data-testid="stSidebar"] {
            width: 380px !important;   /* Change this number as needed */
            min-width: 380px !important;
        }
    </style>
""", unsafe_allow_html=True)

# ====================== SIDEBAR ======================
with st.sidebar:
    with st.expander("Design Parameters", expanded=True):
        h = st.number_input("Slider Height (y direction) (mm)",
                            min_value=2.0, max_value=20.0, value=7.5, step=0.01, format="%.2f")
        height = h / 4

        col1, col2 = st.columns(2)
        with col1:
            Length_min = st.number_input("Length Min (mm)", min_value=5.0, max_value=100.0, value=87.9, step=0.01, format="%.2f")
        with col2:
            Length_max = st.number_input("Length Max (mm)", min_value=5.0, max_value=100.0, value=88.1, step=0.01, format="%.2f")

        col3, col4 = st.columns(2)
        with col3:
            n_min = st.number_input("Segments Min", min_value=3, max_value=50, value=9, step=1)
        with col4:
            n_max = st.number_input("Segments Max", min_value=3, max_value=50, value=15, step=1)

        col5, col6 = st.columns(2)
        with col5:
            angle_min = st.number_input("Angle Min (°)", min_value=35.0, max_value=55.0, value=40.0, step=0.1, format="%.1f")
        with col6:
            angle_max = st.number_input("Angle Max (°)", min_value=35.0, max_value=55.0, value=45.0, step=0.1, format="%.1f")

        col7, col8 = st.columns(2)
        with col7:
            gap_min = st.number_input("Air Gap Min (mm)", min_value=0.95, max_value=1.50, value=0.98, step=0.01, format="%.2f")
        with col8:
            gap_max = st.number_input("Air Gap Max (mm)", min_value=0.95, max_value=1.50, value=1.10, step=0.01, format="%.2f")

        col9, col10 = st.columns(2)
        with col9:
            Sw_min = st.number_input("Sw Min (mm)", min_value=1.0, max_value=15.0, value=3.0, step=0.1, format="%.2f")
        with col10:
            Sw_max = st.number_input("Sw Max (mm)", min_value=3.0, max_value=9.0, value=5.0, step=0.1, format="%.2f")

    st.divider()

    Double_Chevron = st.checkbox("Double Chevron Design", value=True)
    EndSensorsActive = st.checkbox("End Sensors Active", value=False)

# ====================== CALCULATIONS (cached — only reruns when an input changes) ======================
@st.cache_data
def find_candidates(height, Length_min, Length_max, n_min, n_max,
                    angle_min, angle_max, gap_min, gap_max,
                    Sw_min, Sw_max, EndSensorsActive):
    # Lists
    angle = [round(angle_min, 1)] if angle_min == angle_max else np.round(np.arange(angle_min, angle_max + 0.05, 0.1), 1).tolist()
    segments = [int(n_min)] if n_min == n_max else list(range(n_min, n_max + 1))
    gap = [round(gap_min, 2)] if gap_min == gap_max else np.round(np.arange(gap_min, gap_max + 0.005, 0.01), 2).tolist()

    horiz_gaps = [round(g / math.sin(math.radians(ang)), 4) for ang in angle for g in gap]
    horiz_gaps = sorted(set(horiz_gaps))

    # Sw
    Sw = []
    for n in segments:
        for horiz in horiz_gaps:
            for L in np.arange(Length_min, Length_max + 0.001, 0.01):
                if (n - 1) * horiz < L:
                    Sw.append(round((L - (n - 1) * horiz) / n, 2))
    Sw = sorted(set([x for x in Sw if Sw_min <= x <= Sw_max]))

    # Candidates
    candidates = []
    for n in segments:
        for ang in angle:
            for sw in Sw:
                for g in gap:
                    horiz_gap = g / math.sin(math.radians(ang))
                    pitch = sw + horiz_gap
                    tail = height / math.tan(math.radians(ang))
                    Stot = sw + tail
                    overlap = Stot - pitch
                    centr_offset = sw - Stot / 2
                    
                    MinFingerSize = 2 * (horiz_gap + centr_offset + (tail - 0.5 * overlap) * math.tan(math.radians(ang)))
                    MaxFingerSize = 3 * (horiz_gap + centr_offset + (tail - 0.5 * overlap) * math.tan(math.radians(ang)))
                    FingerRangeDiff = round(MaxFingerSize - MinFingerSize, 2)
                    
                    Ltot = pitch * n + tail - horiz_gap
                    
                    Active_Length = Ltot + Stot if EndSensorsActive else Ltot - Stot
                    
                    if Length_min < Active_Length <= Length_max:
                        candidates.append([
                            round(Active_Length, 2), round(Ltot, 2), int(n), round(sw, 2),
                            round(g, 2), round(pitch, 3), round(ang, 1), round(Stot, 2),
                            round(overlap, 2), round(tail, 2), round(MinFingerSize, 2),
                            round(MaxFingerSize, 2), FingerRangeDiff
                        ])

    df = pd.DataFrame(candidates, columns=[
        "Active_Length", "Ltot", "segments", "Sw", "gap", "pitch", "angle",
        "Stot", "overlap", "tail", "MinFingerSize", "MaxFingerSize", "FingerRangeDiff"
    ])
    return df.sort_values(by=["overlap"], ascending=False).reset_index(drop=True)


with st.spinner("Calculating all possible combinations..."):
    df = find_candidates(height, Length_min, Length_max, n_min, n_max,
                         angle_min, angle_max, gap_min, gap_max,
                         Sw_min, Sw_max, EndSensorsActive)

# ====================== MAIN AREA ======================
c1, c2, c3 = st.columns(3, gap="small")

with c1:
    st.metric("Height", f"{h:.2f} mm")
with c2:
    st.metric("Length", f"{Length_min:.2f}–{Length_max:.2f}")
with c3:
    st.metric("Angle", f"{angle_min:.1f}–{angle_max:.1f}°")

c4, c5, c6 = st.columns(3, gap="small")
with c4:
    st.metric("Segments", f"{n_min}–{n_max}")
with c5:
    st.metric("Air Gap", f"{gap_min:.2f}–{gap_max:.2f}")
with c6:
    st.metric("Sw Range", f"{Sw_min:.2f}–{Sw_max:.2f}")

st.divider()

# Results
st.subheader("Candidates")
if len(df) > 0:
    st.dataframe(df, use_container_width=True, height=300)
    st.caption(f"{len(df)} candidates found")
else:
    st.warning("No candidates. Widen ranges.")

# Plot button
if st.button("Generate Plots", type="primary"):
    with st.spinner("Plotting..."):
        
        if len(df) == 0:
            st.error("No candidates to plot.")
        else:
            df_plot = df.head(8).copy()   # limit for speed

            # ====================== FIXED SCALE CHEVRON ======================
            fig, ax = plt.subplots(nrows=len(df_plot), ncols=1, figsize=(16, 9), 
                                   sharex=True, sharey=True)
            x1 = []
            y1 = []
            label = -1
            for j in range(len(df_plot)):
                label += 1
                n = int(df_plot.at[j, 'segments'])
                a = df_plot.at[j, 'angle']
                segW = df_plot.at[j, 'Sw']
                horiz_gap = df_plot.at[j, 'gap'] / math.sin(math.radians(a))
                pitch = segW + horiz_gap
                
                x_list = [None] * n
                y_list = [None] * n
                
                for k in range(n):
                    d = pitch * k
                    
                    if not Double_Chevron:
                        ht = height * 0.8   # scaled down
                        x_list[k] = [0 + d, (ht/math.tan(math.radians(a))) + d, 0 + d, 
                                     segW + d, (ht/math.tan(math.radians(a))) + segW + d, segW + d]
                        y_list[k] = [0, ht, ht*2, ht*2, ht, 0]
                    else:
                        # x plot values
                        x_list[k] = [0 + d, (height/math.tan(math.radians(a))) + d, 0 + d, segW + d,(height/math.tan(math.radians(a))) + segW + d, segW + d,
                                (height/math.tan(math.radians(a))) + segW + d, segW + d, 0 + d, (height/math.tan(math.radians(a))) + d, 0 + d]
                        # y plot values
                        y_list[k] = [0, height, height*2, height*2, height, 0, -height, -height*2, -height*2, -height, 0]
                    
                    poly = mpatches.Polygon(np.stack((x_list[k], y_list[k]), axis=1), closed=True, ec='black', lw=1, 
                                            color='#4A90E2', alpha=0.8)
                    ax[j].add_patch(poly)
                
                ax[j].set_aspect('equal')
                ax[j].axis('off')
                ax[j].set_xlim(0, pitch * n + 10)
                ax[j].set_ylim(-height*2, height*2)
                #ax[j].set_title(f"Candidate {j} | Active_Length = {df_plot.at[j, 'Active_Length']:.2f} mm", fontsize=11)
                ax[j].set_title(label, x=-0.1, y=0)

            st.pyplot(fig, use_container_width=True)