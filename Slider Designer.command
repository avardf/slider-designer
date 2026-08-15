#!/bin/zsh
# Double-click this file in Finder to launch the Slider Designer.
# Streamlit opens your browser automatically once the server is up.
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  print ""
  print "  uv is not installed (or not on PATH)."
  print ""
  print "  Install it — no admin rights needed:"
  print "    curl -LsSf https://astral.sh/uv/install.sh | sh"
  print ""
  print "  Then close this window and double-click this file again."
  print ""
  read -k 1 "?Press any key to close..."
  exit 1
fi

# --server.address=localhost keeps a local run off the network. It lives here
# rather than in .streamlit/config.toml so cloud deployments still bind 0.0.0.0.
exec uv run streamlit run app.py --server.address=localhost
