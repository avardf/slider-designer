import streamlit as st
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go
from datetime import datetime

# ➜  WebApp git:(main) ✗ uv run streamlit run app.py --server.runOnSave true

st.set_page_config(page_title="Slider Designer", layout="wide")


def chevron_icon(n=5, ht=10.0, segW=14.0, hz=3.0, ang=45.0, px=26):
    """Inline SVG of a single-chevron slider, drawn with the same vertex
    formula the app uses for the single-chevron plots."""
    T = ht / math.tan(math.radians(ang))
    pitch = segW + hz
    polys = []
    for k in range(n):
        d = pitch * k
        xs = [0 + d, T + d, 0 + d, segW + d, T + segW + d, segW + d]
        ys = [0, ht, ht * 2, ht * 2, ht, 0]
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in zip(xs, ys))
        polys.append(f'<polygon points="{pts}"/>')
    w = pitch * (n - 1) + T + segW
    return (f'<svg viewBox="-1 -1 {w + 2:.2f} {ht * 2 + 2:.2f}" height="{px}" '
            f'xmlns="http://www.w3.org/2000/svg" fill="#4A90E2" '
            f'stroke="#0e1117" stroke-width="0.9" '
            f'style="vertical-align:middle;margin:0 0.5rem;">'
            + "".join(polys) + '</svg>')

# Minimal top padding
st.markdown("""
    <style>
        .block-container {padding-top: 1.5rem !important;}
        h1 {margin: 0 !important; padding: 0 !important;}
    </style>
""", unsafe_allow_html=True)

_icon = chevron_icon()
st.markdown(f"<h2 style='text-align:center; margin:0;'>{_icon}Slider Designer{_icon}</h2>",
            unsafe_allow_html=True)
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
            gap_min = st.number_input("Air Gap Min (mm)", min_value=0.95, max_value=1.50, value=1.00, step=0.01, format="%.2f")
        with col8:
            gap_max = st.number_input("Air Gap Max (mm)", min_value=0.95, max_value=1.50, value=1.00, step=0.01, format="%.2f")

        col9, col10 = st.columns(2)
        with col9:
            Sw_min = st.number_input("Seg Width (SW) Min (mm)", min_value=1.0, max_value=15.0, value=3.0, step=0.1, format="%.2f")
        with col10:
            Sw_max = st.number_input("Seg Width (SW) Max (mm)", min_value=3.0, max_value=9.0, value=5.0, step=0.1, format="%.2f")

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

    # For each (n, angle, gap) combination, solve directly for the segment
    # widths that put Active_Length inside the target window, instead of
    # searching a single pool of Sw values shared across every n.
    #
    # Substituting Ltot = pitch*n + tail - horiz_gap and Stot = sw + tail:
    #     end sensors off:  Active_Length = (n - 1) * (sw + horiz_gap)
    #     end sensors on:   Active_Length = (n + 1) * sw + (n - 1) * horiz_gap + 2 * tail
    # Both invert cleanly for sw, giving the exact valid interval per
    # combination. Widths are still stepped on the same 0.01 mm grid, and every
    # hit is re-checked against the window after rounding.
    candidates = []
    for n in segments:
        for ang in angle:
            tail = height / math.tan(math.radians(ang))
            for g in gap:
                horiz_gap = g / math.sin(math.radians(ang))

                if EndSensorsActive:
                    lo = (Length_min - (n - 1) * horiz_gap - 2 * tail) / (n + 1)
                    hi = (Length_max - (n - 1) * horiz_gap - 2 * tail) / (n + 1)
                else:
                    lo = Length_min / (n - 1) - horiz_gap
                    hi = Length_max / (n - 1) - horiz_gap

                # Clip to the user's Sw limits, then walk the 0.01 grid. The
                # one-step padding keeps widths whose rounded value still lands
                # inside the window.
                lo = max(lo, Sw_min)
                hi = min(hi, Sw_max)
                if hi < lo:
                    continue

                for step in range(int(math.floor(lo * 100)) - 1,
                                  int(math.ceil(hi * 100)) + 2):
                    sw = round(step / 100, 2)
                    if not (Sw_min <= sw <= Sw_max):
                        continue

                    pitch = sw + horiz_gap
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
        "Active_Length", "Ltot", "segments", "SW", "gap", "pitch", "angle",
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
    st.metric("Seg Width (SW)", f"{Sw_min:.2f}–{Sw_max:.2f}")

st.divider()

# Results
st.subheader("Candidates")
if len(df) > 0:
    st.dataframe(df, width='stretch', height=300)
    st.caption(f"{len(df)} candidates found")
else:
    st.warning("No candidates. Widen ranges.")

# ====================== DRAWING HELPERS ======================
def chevron_xy(n, a, segW, gap_v, height, double_chevron):
    """Vertex lists for one candidate's full chevron row.

    Geometry is unchanged from the original matplotlib implementation; the
    per-segment polygons are separated by None so they draw as a single trace.
    Returns (xs, ys, x_extent).
    """
    horiz_gap = gap_v / math.sin(math.radians(a))
    pitch = segW + horiz_gap
    xs, ys = [], []
    for k in range(n):
        d = pitch * k

        if not double_chevron:
            ht = height * 0.8   # scaled down
            x_pts = [0 + d, (ht/math.tan(math.radians(a))) + d, 0 + d,
                     segW + d, (ht/math.tan(math.radians(a))) + segW + d, segW + d]
            y_pts = [0, ht, ht*2, ht*2, ht, 0]
        else:
            x_pts = [0 + d, (height/math.tan(math.radians(a))) + d, 0 + d, segW + d, (height/math.tan(math.radians(a))) + segW + d, segW + d,
                     (height/math.tan(math.radians(a))) + segW + d, segW + d, 0 + d, (height/math.tan(math.radians(a))) + d, 0 + d]
            y_pts = [0, height, height*2, height*2, height, 0, -height, -height*2, -height*2, -height, 0]

        xs += x_pts + [x_pts[0], None]
        ys += y_pts + [y_pts[0], None]

    return xs, ys, pitch * n + 10


def param_summary(p):
    return (f"n={int(p['segments'])}   SW={p['SW']:.2f}   gap={p['gap']:.2f}   "
            f"angle={p['angle']:.1f}°   pitch={p['pitch']:.3f}   "
            f"overlap={p['overlap']:.2f}   Active_L={p['Active_Length']:.2f} mm")


def candidate_figure(p, height, double_chevron, x_range=None, tag=None):
    """One candidate as its own figure, with its parameters drawn into the
    header so a downloaded PNG carries the settings that produced it."""
    xs, ys, extent = chevron_xy(int(p['segments']), p['angle'], p['SW'], p['gap'],
                                height, double_chevron)
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode='lines', fill='toself',
                               line=dict(color='black', width=1),
                               fillcolor='rgba(74, 144, 226, 0.8)',
                               hoverinfo='skip', showlegend=False))

    # One left-aligned line below the drawing: the hover toolbar sits top-right
    # and a second right-aligned annotation would collide with it at narrow widths.
    caption = param_summary(p)
    if tag:
        caption = f"<b>{tag}</b>   {caption}"
    fig.add_annotation(text=caption, xref='paper', yref='paper',
                       x=0, y=0, showarrow=False, xanchor='left', yanchor='top',
                       yshift=-6,
                       font=dict(color='#333333', size=11, family='monospace'))

    # constrain='domain' shrinks the plot box to satisfy the 1:1 aspect lock.
    # The default ('range') instead inflates the axis ranges, which zooms the
    # drawing down to a sliver.
    fig.update_xaxes(visible=False, range=[0, x_range or extent],
                     constrain='domain')
    fig.update_yaxes(visible=False, range=[-height*2, height*2],
                     scaleanchor='x', scaleratio=1, constrain='domain')
    fig.update_layout(height=150, margin=dict(l=10, r=10, t=10, b=38),
                      paper_bgcolor='white', plot_bgcolor='white', showlegend=False)
    return fig


def chart_config(p):
    """Hover-toolbar setup: the camera icon exports a high-res PNG whose
    filename encodes the design parameters."""
    fname = (f"slider_n{int(p['segments'])}_SW{p['SW']:.2f}"
             f"_gap{p['gap']:.2f}_ang{p['angle']:.1f}")
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
        'toImageButtonOptions': {'format': 'png', 'filename': fname, 'scale': 3},
    }


def plot_x_max(rows, height, double_chevron):
    """Shared x extent so every candidate is drawn at the same scale."""
    return max(chevron_xy(int(p['segments']), p['angle'], p['SW'], p['gap'],
                          height, double_chevron)[2] for p in rows)


# ====================== SESSION STATE ======================
if 'saved_designs' not in st.session_state:
    st.session_state.saved_designs = []
if 'show_plots' not in st.session_state:
    st.session_state.show_plots = False
if 'view_saved' not in st.session_state:
    st.session_state.view_saved = False

# ====================== CONTROLS ======================
if st.button("Generate Plots", type="primary"):
    st.session_state.show_plots = True
    st.session_state.view_saved = False

n_saved = len(st.session_state.saved_designs)

if st.session_state.view_saved:
    if st.button("▶️ Resume Design Activity", type="secondary"):
        st.session_state.view_saved = False
        st.rerun()
else:
    if st.button(f"📌 Show saved Designs ({n_saved})", type="secondary",
                 disabled=(n_saved == 0)):
        st.session_state.view_saved = True
        st.rerun()

st.divider()

# ====================== SAVED VIEW ======================
if st.session_state.view_saved:
    st.subheader("Saved Designs")
    st.caption("Design activity is paused. These are frozen snapshots — "
               "changing the sidebar will not alter them.")

    saved_df = pd.DataFrame([s['params'] for s in st.session_state.saved_designs])
    b1, b2 = st.columns([1, 1])
    with b1:
        st.download_button("⬇️ Download parameters (CSV)",
                           saved_df.to_csv(index=False),
                           "saved_designs.csv", "text/csv", width='stretch')
    with b2:
        if st.button("🗑️ Clear all saved", width='stretch'):
            st.session_state.saved_designs = []
            st.session_state.view_saved = False
            st.rerun()

    x_max_saved = plot_x_max([s['params'] for s in st.session_state.saved_designs],
                             height, Double_Chevron)

    for i, s in enumerate(st.session_state.saved_designs):
        p = s['params']
        c_plot, c_btn = st.columns([10, 3], vertical_alignment="center")
        with c_plot:
            # Redrawn with the height/chevron mode captured at save time.
            fig = candidate_figure(p, s['height'], s['double_chevron'],
                                   x_range=x_max_saved,
                                   tag=f"saved {s['saved_at']}")
            st.plotly_chart(fig, width='stretch', key=f"saved_{i}",
                            config=chart_config(p))
        with c_btn:
            if st.button("🗑️ Remove", key=f"rm_{i}", width='stretch'):
                st.session_state.saved_designs.pop(i)
                if not st.session_state.saved_designs:
                    st.session_state.view_saved = False
                st.rerun()

# ====================== CURRENT VIEW ======================
elif st.session_state.show_plots:
    if len(df) == 0:
        st.error("No candidates to plot.")
    else:
        st.subheader("Current Design")
        st.caption("Hover a drawing for the toolbar — the camera icon saves a PNG "
                   "with its parameters. 💾 Save pins it to the saved set.")

        df_plot = df.head(8).copy()   # limit for speed
        rows = [df_plot.loc[j] for j in range(len(df_plot))]
        x_max = plot_x_max(rows, height, Double_Chevron)

        for j, p in enumerate(rows):
            c_plot, c_btn = st.columns([10, 3], vertical_alignment="center")
            with c_plot:
                fig = candidate_figure(p, height, Double_Chevron,
                                       x_range=x_max, tag=f"candidate {j}")
                st.plotly_chart(fig, width='stretch', key=f"cur_{j}",
                                config=chart_config(p))
            with c_btn:
                if st.button("💾 Save", key=f"save_{j}", width='stretch'):
                    st.session_state.saved_designs.append({
                        'saved_at': datetime.now().strftime("%H:%M:%S"),
                        'height': height,
                        'double_chevron': Double_Chevron,
                        'end_sensors': EndSensorsActive,
                        'params': p.to_dict(),
                    })
                    st.toast(f"Saved candidate {j}")
                    st.rerun()