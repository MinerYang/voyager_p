import streamlit as st
import time
import re

# --- Settings ---
LOG_FILE = 'logs/admin.log'
TAIL_LINES = 200
REFRESH_INTERVAL = 2  # seconds

st.title("🔍 Real-time Log Viewer")

# --- UI ---
filter_text = st.text_input("Filter (regex supported)", "")
highlight_errors = st.checkbox("Highlight ERROR", value=True)

# --- Read Log File ---
try:
    with open(LOG_FILE, 'r') as f:
        lines = f.readlines()[-TAIL_LINES:]
except FileNotFoundError:
    st.warning("Log file not found.")
    st.stop()
except Exception as e:
    st.error(f"Error reading log file: {e}")
    st.stop()

# --- Filter ---
if filter_text:
    try:
        lines = [line for line in lines if re.search(filter_text, line)]
    except re.error as err:
        st.error(f"Invalid regex: {err}")
        st.stop()

# --- Highlight ---
def highlight(line):
    if highlight_errors and ("ERROR" in line or "CRITICAL" in line):
        return f"<span style='color:red; font-weight:bold;'>{line}</span>"
    return f"<span style='color:gray;'>{line}</span>"

formatted = "".join([highlight(line) for line in lines])

# --- Inject JS for Auto-Scroll ---
st.markdown("""
    <script>
        window.scrollTo(0, document.body.scrollHeight);
    </script>
""", unsafe_allow_html=True)

# --- Display Log Content ---
st.markdown(
    f"<div style='font-family: monospace; white-space: pre-wrap;'>{formatted}</div>",
    unsafe_allow_html=True
)

# --- Auto Refresh ---
time.sleep(REFRESH_INTERVAL)
st.rerun()
