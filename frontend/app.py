"""
Maasai Mara Wildlife Guide — Streamlit Frontend
Connects to the FastAPI backend at API_URL.
"""

import io
import requests
import streamlit as st
from PIL import Image, ImageDraw

# ── Configuration ─────────────────────────────────────────────────────────────
API_URL = "http://localhost:8080"   # Change to Cloud Run URL in production

# ── Page setup ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Maasai Mara Wildlife Guide",
    page_icon="🦁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0f0a05; }
    .block-container { padding-top: 2rem; max-width: 900px; }
    h1 { color: #C8803A; font-family: Georgia, serif; font-weight: 300; }
    h2, h3 { color: #F5EDD8; font-family: Georgia, serif; font-weight: 300; }
    .stButton > button {
        background-color: #C8803A; color: #0f0a05;
        border: none; font-weight: 600; padding: 0.6rem 2rem;
        width: 100%;
    }
    .stButton > button:hover { background-color: #7B3F1E; color: #F5EDD8; }
    .answer-box {
        background: rgba(200,128,58,0.08);
        border-left: 3px solid #C8803A;
        padding: 1.2rem 1.5rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    .source-box {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(200,128,58,0.2);
        padding: 0.8rem 1rem;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #aaa;
    }
    .metric-box {
        background: rgba(200,128,58,0.06);
        border: 1px solid rgba(200,128,58,0.2);
        padding: 0.6rem 1rem;
        border-radius: 4px;
        text-align: center;
    }
    .species-chip {
        display: inline-block;
        background: rgba(200,128,58,0.15);
        border: 1px solid rgba(200,128,58,0.4);
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        margin: 0.2rem;
        font-size: 0.85rem;
        color: #C8803A;
    }
</style>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🦁 Maasai Mara Wildlife Guide")
st.markdown(
    "<p style='color:#aaa; font-style:italic;'>"
    "Photograph any animal · Ask anything · Get expert answers"
    "</p>",
    unsafe_allow_html=True
)
st.divider()


# ── API health check ──────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def check_health():
    try:
        r = requests.get(f"{API_URL}/health", timeout=5)
        return r.json()
    except Exception:
        return {"status": "unreachable"}

health = check_health()
if health.get("status") == "ok":
    st.success("✓ API connected — CNN, YOLOv8, and RAG pipeline ready")
elif health.get("status") == "unreachable":
    st.error("✗ Cannot reach API. Ensure the backend is running.")
    st.stop()
else:
    st.warning(f"⚠ API degraded: {health}")


# ── Suggested questions ───────────────────────────────────────────────────────
SUGGESTED = [
    "Is this animal dangerous to tourists?",
    "What does this animal eat?",
    "When is the best time to see this animal?",
    "What is the conservation status of this species?",
    "What interesting facts should I know?",
    "Where in Maasai Mara can I see this animal?",
]


# ── Layout ────────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### 📷 Upload Wildlife Photo")
    uploaded = st.file_uploader(
        "Upload a camera trap or safari image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed"
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", use_column_width=True)

with col_right:
    st.markdown("### ❓ Ask a Question")

    # Suggested question chips
    st.markdown("**Quick questions:**")
    cols = st.columns(2)
    if "question" not in st.session_state:
        st.session_state.question = ""

    for i, q in enumerate(SUGGESTED):
        with cols[i % 2]:
            if st.button(q[:40] + "…" if len(q) > 40 else q,
                         key=f"chip_{i}", use_container_width=True):
                st.session_state.question = q

    question = st.text_input(
        "Or type your own question:",
        value=st.session_state.question,
        placeholder="Is this animal dangerous? What does it eat?",
        key="question_input"
    )

    ask_pressed = st.button("🔍 Ask the Guide", use_container_width=True)


# ── Query ─────────────────────────────────────────────────────────────────────
if ask_pressed:
    if not uploaded:
        st.error("Please upload a wildlife image first.")
    elif not question.strip():
        st.error("Please enter a question.")
    else:
        with st.spinner("Analysing image and generating answer …"):
            try:
                uploaded.seek(0)
                response = requests.post(
                    f"{API_URL}/analyze",
                    files={"image": (uploaded.name, uploaded.read(), uploaded.type)},
                    data={"question": question},
                    timeout=60
                )

                if response.status_code != 200:
                    st.error(f"API error {response.status_code}: {response.text}")
                else:
                    data = response.json()

                    st.divider()
                    st.markdown("## 🔬 Analysis Results")

                    # ── Vision results ────────────────────────────────────────
                    det_col, hab_col = st.columns(2)

                    with det_col:
                        st.markdown("#### Animals Detected")
                        dets = data.get("detections", [])
                        if dets:
                            for d in dets:
                                st.markdown(
                                    f"<span class='species-chip'>"
                                    f"🦁 {d['species'].title()} "
                                    f"({d['species_conf']:.0%})</span>",
                                    unsafe_allow_html=True
                                )
                            # Top-3 breakdown for first animal
                            st.markdown("**Top-3 predictions (primary animal):**")
                            for p in dets[0]["top3"]:
                                st.progress(
                                    p["confidence"],
                                    text=f"{p['species'].title()} — {p['confidence']:.1%}"
                                )
                        else:
                            st.info("No animals detected.")

                    with hab_col:
                        st.markdown("#### Scene Analysis")
                        hab = data.get("habitat", {})
                        st.markdown(f"**Habitat:** {hab.get('habitat','—').title()}")
                        st.markdown(f"**Time of day:** {hab.get('time_of_day','—').title()}")
                        st.progress(
                            hab.get("vegetation_ratio", 0),
                            text=f"Vegetation: {hab.get('vegetation_ratio',0):.1%}"
                        )
                        st.progress(
                            hab.get("water_ratio", 0),
                            text=f"Water: {hab.get('water_ratio',0):.1%}"
                        )
                        st.progress(
                            min(hab.get("dry_ratio", 0), 1.0),
                            text=f"Dry grass: {hab.get('dry_ratio',0):.1%}"
                        )

                    # ── Annotated image with bounding boxes ───────────────────
                    if dets and any(d["bbox"] is not None for d in dets):
                        st.markdown("#### Detected Animals")
                        draw_img = image.copy()
                        draw     = ImageDraw.Draw(draw_img)
                        colours  = [
                            "#C8803A", "#5BA35B", "#5B8DC8",
                            "#C85B8D", "#C8C85B", "#8D5BC8"
                        ]
                        for i, d in enumerate(dets):
                            if d["bbox"] is None:
                                continue
                            x1, y1, x2, y2 = d["bbox"]
                            col = colours[i % len(colours)]
                            draw.rectangle([x1, y1, x2, y2], outline=col, width=3)
                            draw.rectangle([x1, y1-22, x1+200, y1], fill=col)
                            draw.text(
                                (x1+4, y1-20),
                                f"{d['species'].title()} {d['species_conf']:.0%}",
                                fill="white"
                            )
                        st.image(draw_img, use_column_width=True)

                    # ── RAG Answer ────────────────────────────────────────────
                    st.markdown("#### 💬 Wildlife Guide Answer")
                    st.markdown(
                        f"<div class='answer-box'>{data.get('answer','No answer returned.')}</div>",
                        unsafe_allow_html=True
                    )

                    # ── Sources ───────────────────────────────────────────────
                    sources = data.get("sources", [])
                    if sources:
                        with st.expander(f"📚 Sources ({len(sources)} cited)"):
                            st.markdown(
                                "<div class='source-box'>" +
                                "<br>".join(sources) +
                                "</div>",
                                unsafe_allow_html=True
                            )

                    # ── Metadata ──────────────────────────────────────────────
                    m1, m2 = st.columns(2)
                    with m1:
                        st.markdown(
                            f"<div class='metric-box'>"
                            f"<b>{data.get('num_animals',0)}</b><br>"
                            f"<small>Animals detected</small></div>",
                            unsafe_allow_html=True
                        )
                    with m2:
                        st.markdown(
                            f"<div class='metric-box'>"
                            f"<b>{data.get('sources_used',0)}</b><br>"
                            f"<small>KB chunks retrieved</small></div>",
                            unsafe_allow_html=True
                        )

            except requests.exceptions.Timeout:
                st.error("Request timed out. The model may still be loading — try again.")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


# ── Footer ────────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<p style='text-align:center; color:#555; font-size:0.8rem;'>"
    "Maasai Mara Wildlife Intelligence Guide · "
    "MSc Big Data Technologies · Glasgow Caledonian University · "
    "Alvin Kimani</p>",
    unsafe_allow_html=True
)
