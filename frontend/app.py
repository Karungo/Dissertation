import os
import requests
import streamlit as st

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
# When the API runs as a separate Docker container (docker-compose),
# use the service name as the hostname, e.g. http://api:8080
# When running the API directly on the same VM, use http://localhost:8080
API_URL = os.getenv("API_URL", "http://localhost:8080")

st.set_page_config(
    page_title="Maasai Mara Wildlife Guide",
    page_icon="🦁",
    layout="centered",
)

st.title("🦁 Maasai Mara Wildlife Guide")
st.write(
    "Upload a photo of an animal you spotted on safari, ask a question, "
    "and get an AI-powered identification plus a grounded answer."
)

# ----------------------------------------------------------------------
# Sidebar: backend health check
# ----------------------------------------------------------------------
with st.sidebar:
    st.subheader("Backend status")
    if st.button("Check API health"):
        try:
            resp = requests.get(f"{API_URL}/health", timeout=10)
            data = resp.json()
            if resp.status_code == 200:
                st.success(f"API healthy: {data}")
            else:
                st.warning(f"API degraded: {data}")
        except requests.RequestException as e:
            st.error(f"Could not reach API at {API_URL}: {e}")
    st.caption(f"API URL: {API_URL}")

# ----------------------------------------------------------------------
# Main form
# ----------------------------------------------------------------------
uploaded_image = st.file_uploader(
    "Upload a wildlife photo", type=["jpg", "jpeg", "png"]
)
question = st.text_input(
    "Your question", placeholder="e.g. What does this animal eat?"
)

if uploaded_image is not None:
    st.image(uploaded_image, caption="Uploaded photo", use_container_width=True)

submit = st.button("Analyze", type="primary", disabled=uploaded_image is None)

if submit:
    if not question.strip():
        st.error("Please enter a question before submitting.")
    else:
        with st.spinner("Identifying species and generating an answer..."):
            try:
                files = {
                    "image": (
                        uploaded_image.name,
                        uploaded_image.getvalue(),
                        uploaded_image.type or "image/jpeg",
                    )
                }
                data = {"question": question}
                resp = requests.post(
                    f"{API_URL}/analyze", files=files, data=data, timeout=120
                )
            except requests.RequestException as e:
                st.error(f"Request to API failed: {e}")
                resp = None

        if resp is not None:
            if resp.status_code == 200:
                result = resp.json()

                st.subheader("Top predictions")
                for p in result.get("predictions", []):
                    st.write(f"- **{p['species']}** — {p['confidence'] * 100:.1f}% confidence")

                st.subheader("Answer")
                st.write(result.get("answer", "No answer returned."))
            else:
                try:
                    detail = resp.json().get("detail", resp.text)
                except ValueError:
                    detail = resp.text
                st.error(f"API error ({resp.status_code}): {detail}")
