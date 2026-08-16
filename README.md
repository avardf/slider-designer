# Slider Designer

Streamlit app for exploring CapSense slider chevron segment geometry.

## Running it

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) once, then:

- **macOS** — double-click `Slider Designer.command`
- **Windows** — double-click `Slider Designer.bat`
- **Any platform, from a terminal** — `uv run streamlit run app.py`

The first launch takes a minute while uv downloads Python (3.12 or newer) and
the dependencies; after that it starts in a couple of seconds. Your browser
opens automatically.

### Without uv, using pip

`requirements.txt` is provided for environments where uv is not an option. The
versions in it are exported from `uv.lock`, so they are exactly the ones the app
was built and tested against.

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

**Check `python3 --version` first — this needs 3.12 or newer.** On an older
Python, pip fails with a misleading `Could not find a version that satisfies the
requirement altair==...` instead of saying the Python is too old. macOS ships
3.9, so the system Python will not work.

`requirements.txt` omits matplotlib, which only the frozen
`app_matplotlib.bak.py` fallback needs. Regenerate the file after any dependency
change with:

```bash
uv export --format requirements-txt --no-hashes --no-dev --no-emit-project -o requirements.txt
```

## Running it on a managed / corporate machine

The app runs entirely on your own machine and binds to `localhost` only. It is
never reachable from the network, opens no ports to anyone else, and needs no
admin rights. That avoids firewall prompts and keeps endpoint security software
uninterested in it.

The one thing it does need is a **one-time download** of Python and the
dependencies (~200 MB), and that is where locked-down networks get in the way.
Everything below is a fix for that download.

### If the launcher reports it could not download dependencies

Run these in the same window before launching again. Ask IT for whichever value
applies:

| Situation | Fix |
| --- | --- |
| Traffic goes through a proxy | `set HTTP_PROXY=http://your.proxy:port`<br>`set HTTPS_PROXY=http://your.proxy:port` |
| Company does TLS inspection (certificate errors) | `set SSL_CERT_FILE=C:\path\to\corporate-root.pem` |
| Company runs an internal PyPI mirror | `set UV_INDEX_URL=https://your.internal.mirror/simple` |

On macOS/Linux use `export` instead of `set`.

### Other things that bite on Windows

- **The file is blocked after unzipping.** Files from an emailed or downloaded
  zip carry a "mark of the web". Right-click `Slider Designer.bat` →
  Properties → tick **Unblock** → OK. Or unblock the whole folder in
  PowerShell: `Get-ChildItem -Recurse | Unblock-File`
- **SmartScreen warns.** Click *More info* → *Run anyway*.
- **uv installs but the launcher still says it is missing.** The installer adds
  it to PATH, which only new windows pick up. Close the window and reopen it.
- **No admin rights.** None are needed. The uv installer writes to your user
  profile, not Program Files.

### If the machine cannot reach the internet at all

Ask for an offline bundle instead — the dependencies can be pre-downloaded and
shipped alongside the app so nothing is fetched at run time.

## The drawings

The top 14 candidates are drawn, each as its own chart with its parameters
printed underneath so any exported image is self-describing.

Drawings render at **approximately life size** — millimetres are converted at
96/25.4 px per mm, a CSS pixel being 1/96 inch. Browser zoom and display scaling
shift the true physical size, so treat it as a proportion check rather than a
dimensioned drawing.

They flow into as many columns as the window allows: two on a wide screen
(roughly 1400 px or more), one below that. Nothing is squashed either way.

## Saving designs

- **Hover a drawing** to reveal the Plotly toolbar. The camera icon downloads a
  3× resolution PNG; the filename encodes the design, e.g.
  `slider_n15_SW4.73_gap1.00_ang40.0.png`. The toolbar also gives zoom and pan.
- **💾** pins that candidate to the saved set — the drawing plus the full
  parameter row, frozen at the moment you clicked. **🗑️** removes a saved one.
- **📌 Show saved Designs** pauses design activity and displays the saved
  snapshots instead. Sidebar changes do not affect them; each is redrawn with the
  slider height and chevron mode captured at save time. The count in the button
  is how many you have saved; it is greyed out until you save one.
- **▶️ Resume Design Activity** returns to the live view. Saved designs are kept.
- **⬇️ Download parameters (CSV)** exports every saved design's parameters.

Saved designs live in the browser session. Reloading the page or restarting the
server clears them — use the CSV export or the PNG downloads for anything you
need to keep.

## Sending this to someone else

Zip the folder **without** `.venv` — that directory is ~470 MB of
platform-specific binaries with absolute paths baked in, and it will not work on
another machine. uv rebuilds it from `uv.lock` on the recipient's side, pinned to
the exact same package versions. Everything else totals well under 1 MB.

macOS/Linux:

```bash
zip -r SliderDesigner.zip WebApp -x '*/.venv/*' '*/.idea/*' '*/.DS_Store' '*/__pycache__/*'
```

The recipient needs `app.py`, `pyproject.toml`, `uv.lock`, `requirements.txt`,
`.streamlit/`, and whichever launcher matches their platform. Make sure `.streamlit/` survives the
zip — some GUI tools skip dotfolders, and without it the app loses its dark
theme, its auto-reload, and its localhost-only binding.

## Files

| File | Purpose |
| --- | --- |
| `app.py` | The application. |
| `pyproject.toml` / `uv.lock` | Dependencies, version-pinned. Used by uv. |
| `requirements.txt` | Same pins, exported for plain `pip`. Not used by uv. |
| `.streamlit/config.toml` | Dark theme, auto-reload on save, localhost-only binding. |
| `Slider Designer.command` | macOS launcher (double-click). |
| `Slider Designer.bat` | Windows launcher (double-click), with proxy diagnostics. |
| `README.md` | This file. |
| `app_matplotlib.bak.py` | Pre-Plotly version, kept as a frozen fallback. Needs the `dev` group: `uv run --group dev streamlit run app_matplotlib.bak.py` |

## Parameter names

`SW` is the segment width. It appears as **Seg Width (SW)** in the sidebar and
the summary metrics, and as the `SW` column in the candidates table and the CSV
export.

For a given segment count `n`, air gap and angle, the active length reduces to a
closed form — `(n-1) × pitch` with end sensors off — which the app inverts to
find every valid segment width directly, stepping a 0.01 mm grid. The search is
exhaustive on that grid, so a result of zero candidates means the constraints
genuinely exclude that combination rather than the search having missed it. If a
segment count returns nothing, the usual cause is the **Seg Width (SW)** limits
being too narrow for the width that count requires.

## Single vs double chevron

`h` is the total slider height in both modes, and the drawing spans it in both.
What differs is how far one diagonal edge climbs, which sets `tail`, the
horizontal run of a segment's slanted end:

| | one diagonal rises | `tail` |
| --- | --- | --- |
| Double chevron | `h/4` | `(h/4) / tan(angle)` |
| Single chevron | `h/2` | `(h/2) / tan(angle)` |

`tail` feeds `Stot`, `overlap`, `Ltot` and `Active_Length`, so the two modes
report different numbers for the same slider height — as they should.

One consequence that looks odd but is correct: with **end sensors off** both
modes find the *same* candidate count, because `Active_Length` reduces to
`(n-1) × (SW + horiz_gap)` and `tail` cancels out. With **end sensors on** it
does not cancel, and the candidate sets genuinely differ.

The reference implementation is `slider_dimensions_copy.ipynb`, which uses
`ht = height * 2` for the single-chevron drawing.
