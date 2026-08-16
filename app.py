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

# Tight header + compact read-only parameter chips, so the candidates table is
# visible without scrolling when the app opens.
st.markdown("""
    <style>
        /* Streamlit's fixed toolbar is 60px tall; less top padding than this
           slides the title underneath it. The space saved on this screen comes
           from the compact chips below, not from crowding the header. */
        .block-container {padding-top: 4rem !important;}
        h1 {margin: 0 !important; padding: 0 !important;}

        /* Trim the gap Streamlit leaves between stacked blocks. */
        .block-container [data-testid="stVerticalBlock"] {gap: 0.45rem;}

        /* Pull the Candidates heading up against the chips above it. */
        .block-container h3 {margin-top: 0.3rem !important;
                             margin-bottom: 0.2rem !important;}

        /* Candidate and saved-design rows flow into as many columns as fit.
           Each row needs ~500px (415px life-size drawing + button + gap), so
           this gives two columns on a wide screen and cleanly falls back to
           one on a narrow window instead of overflowing. */
        .st-key-cand-grid,
        .st-key-saved-grid {
            display: grid !important;
            grid-template-columns: repeat(auto-fit, minmax(470px, 1fr));
            gap: 0.4rem 1rem;
            align-items: start;
        }

        .param-chip {
            border: 1px solid rgba(250,250,250,0.14);
            border-radius: 6px;
            padding: 0.28rem 0.55rem;
            line-height: 1.25;
        }
        .param-chip .k {
            display: block;
            font-size: 0.68rem;
            letter-spacing: 0.02em;
            text-transform: uppercase;
            color: #9aa0a6;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .param-chip .v {
            display: block;
            font-size: 0.95rem;
            font-weight: 600;
            white-space: nowrap;
        }
    </style>
""", unsafe_allow_html=True)

_icon = chevron_icon(px=22)
st.markdown(
    f"<h2 style='text-align:center; margin:0 0 0.4rem 0; font-size:1.6rem;'>"
    f"{_icon}Slider Designer{_icon}</h2>",
    unsafe_allow_html=True)

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
        # Design type first — it decides which height box below is live.
        Double_Chevron = st.checkbox("Double Chevron Design", value=True)

        # One height box per design type, with the inactive one greyed out.
        # Each keeps its own value, so switching design type does not silently
        # reinterpret a height entered for the other one — the editable box is
        # always the height actually driving the drawing and the maths.
        colh1, colh2 = st.columns(2)
        with colh1:
            h_double = st.number_input("Double Chevron h (mm)",
                                       min_value=2.0, max_value=20.0, value=7.5,
                                       step=0.01, format="%.2f",
                                       disabled=not Double_Chevron)
        with colh2:
            h_single = st.number_input("Single Chevron h (mm)",
                                       min_value=2.0, max_value=20.0, value=7.5,
                                       step=0.01, format="%.2f",
                                       disabled=Double_Chevron)

        h = h_double if Double_Chevron else h_single
        height = h / 4
        st.caption(f"Using **{h:.2f} mm** total slider height "
                   f"({'double' if Double_Chevron else 'single'} chevron). "
                   f"Drawings render at approximately life size.")

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

    EndSensorsActive = st.checkbox("End Sensors Active", value=False)

# ====================== CALCULATIONS (cached — only reruns when an input changes) ======================
@st.cache_data
def find_candidates(height, Length_min, Length_max, n_min, n_max,
                    angle_min, angle_max, gap_min, gap_max,
                    Sw_min, Sw_max, EndSensorsActive, Double_Chevron):
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
    #
    # tail is the horizontal run of a segment's slanted end, set by how far one
    # diagonal edge climbs. A double chevron stacks four quarter-heights, so its
    # diagonal rises h/4 (= height). A single chevron has one diagonal rising
    # h/2, so it reaches twice as far sideways. Using the double-chevron value
    # for both is what made the single-chevron table disagree with its drawing.
    rise = height if Double_Chevron else height * 2

    candidates = []
    for n in segments:
        for ang in angle:
            tail = rise / math.tan(math.radians(ang))
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
                         Sw_min, Sw_max, EndSensorsActive, Double_Chevron)

# ====================== MAIN AREA ======================
# One compact row instead of two tall ones. Streamlit's default metric type is
# display-sized (~2.25rem); at six read-only summary values that pushed the
# candidates table below the fold on open.
summary = [
    ("Height", f"{h:.2f} mm"),
    ("Length", f"{Length_min:.2f}–{Length_max:.2f}"),
    ("Angle", f"{angle_min:.1f}–{angle_max:.1f}°"),
    ("Segments", f"{n_min}–{n_max}"),
    ("Air Gap", f"{gap_min:.2f}–{gap_max:.2f}"),
    ("Seg Width (SW)", f"{Sw_min:.2f}–{Sw_max:.2f}"),
]
for col, (label, value) in zip(st.columns(6, gap="small"), summary):
    col.markdown(
        f"<div class='param-chip'><span class='k'>{label}</span>"
        f"<span class='v'>{value}</span></div>",
        unsafe_allow_html=True)

# Results
st.subheader("Candidates")
if len(df) > 0:
    # Taller than before: the compact header row freed the vertical space, and
    # showing more rows on open was the point of tightening it.
    st.dataframe(df, width='stretch', height=380)
    st.caption(f"{len(df)} candidates found")
else:
    st.warning("No candidates. Widen ranges.")

# ====================== DRAWING HELPERS ======================
# A CSS pixel is defined as 1/96 inch, so this renders millimetres at close to
# life size on a display at 100% zoom. Browser zoom and display scaling still
# shift the true physical size, so treat it as approximate, not a substitute
# for a dimensioned drawing.
PX_PER_MM = 96 / 25.4


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
            # ht = height * 2 comes straight from slider_dimensions_copy.ipynb.
            # It makes the single chevron span ht*2 = 4*height = h, the full
            # slider height the user entered — same total as the double.
            # Vertices are centred on y=0 so both modes share one viewport.
            ht = height * 2
            x_pts = [0 + d, (ht/math.tan(math.radians(a))) + d, 0 + d,
                     segW + d, (ht/math.tan(math.radians(a))) + segW + d, segW + d]
            y_pts = [-ht, 0, ht, ht, 0, -ht]
        else:
            x_pts = [0 + d, (height/math.tan(math.radians(a))) + d, 0 + d, segW + d, (height/math.tan(math.radians(a))) + segW + d, segW + d,
                     (height/math.tan(math.radians(a))) + segW + d, segW + d, 0 + d, (height/math.tan(math.radians(a))) + d, 0 + d]
            y_pts = [0, height, height*2, height*2, height, 0, -height, -height*2, -height*2, -height, 0]

        xs += x_pts + [x_pts[0], None]
        ys += y_pts + [y_pts[0], None]

    return xs, ys, pitch * n + 10


def param_summary(p):
    """Two short lines rather than one long one — at life-size the figure is
    only ~415 px wide and a single line runs off the edge."""
    return (f"n={int(p['segments'])}   SW={p['SW']:.2f}   gap={p['gap']:.2f}   "
            f"angle={p['angle']:.1f}°<br>"
            f"pitch={p['pitch']:.3f}   overlap={p['overlap']:.2f}   "
            f"Active_L={p['Active_Length']:.2f} mm")


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
                       yshift=-6, align='left',
                       font=dict(color='#333333', size=10, family='monospace'))

    # Size the figure from the millimetre extents so the drawing prints at
    # roughly life size, the way the original matplotlib output did. A CSS
    # pixel is 1/96 inch by definition, so 1 mm = 96/25.4 px at 100% browser
    # zoom. These sliders are small parts; drawing an 88 mm slider a metre
    # wide made the proportions hard to judge.
    x_span = x_range or extent
    y_span = height * 4                      # full slider height h
    # Top margin gives the hover toolbar its own band; at life size the drawing
    # is only ~28 px tall and the toolbar would sit right on top of it.
    # Bottom margin holds the two caption lines.
    m_l, m_r, m_t, m_b = 10, 10, 26, 46
    plot_w = x_span * PX_PER_MM
    plot_h = y_span * PX_PER_MM

    # constrain='domain' shrinks the plot box to satisfy the 1:1 aspect lock.
    # The default ('range') instead inflates the axis ranges, which zooms the
    # drawing down to a sliver.
    fig.update_xaxes(visible=False, range=[0, x_span], constrain='domain')
    fig.update_yaxes(visible=False, range=[-y_span / 2, y_span / 2],
                     scaleanchor='x', scaleratio=1, constrain='domain')
    fig.update_layout(width=round(plot_w + m_l + m_r),
                      height=round(plot_h + m_t + m_b),
                      margin=dict(l=m_l, r=m_r, t=m_t, b=m_b),
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

    saved_grid = st.container(key="saved-grid")
    for i, s in enumerate(st.session_state.saved_designs):
        p = s['params']
        # Horizontal container rather than st.columns: the figure is a fixed
        # pixel width now, so proportional columns would strand the button far
        # to the right. This sizes to content and keeps them adjacent.
        row = saved_grid.container(horizontal=True, vertical_alignment="center")
        with row:
            # Redrawn with the height/chevron mode captured at save time.
            fig = candidate_figure(p, s['height'], s['double_chevron'],
                                   x_range=x_max_saved,
                                   tag=f"saved {s['saved_at']}")
            st.plotly_chart(fig, width='content', key=f"saved_{i}",
                            config=chart_config(p))
            if st.button("🗑️", key=f"rm_{i}", help="Remove this saved design"):
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

        df_plot = df.head(14).copy()   # limit for speed
        rows = [df_plot.loc[j] for j in range(len(df_plot))]
        x_max = plot_x_max(rows, height, Double_Chevron)

        # Keyed container so CSS can lay the rows out as a responsive grid:
        # two columns on a wide screen, one when there is not room. See the
        # .st-key-cand-grid rule in the stylesheet at the top.
        grid = st.container(key="cand-grid")
        for j, p in enumerate(rows):
            row = grid.container(horizontal=True, vertical_alignment="center")
            with row:
                fig = candidate_figure(p, height, Double_Chevron,
                                       x_range=x_max, tag=f"candidate {j}")
                st.plotly_chart(fig, width='content', key=f"cur_{j}",
                                config=chart_config(p))
                if st.button("💾", key=f"save_{j}", help="Save this design"):
                    st.session_state.saved_designs.append({
                        'saved_at': datetime.now().strftime("%H:%M:%S"),
                        'height': height,
                        'double_chevron': Double_Chevron,
                        'end_sensors': EndSensorsActive,
                        'params': p.to_dict(),
                    })
                    st.toast(f"Saved candidate {j}")
                    st.rerun()