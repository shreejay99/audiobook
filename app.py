import streamlit as st
import os
import base64
from utils.pdf_loader import extract_text_from_pdf
from utils.ai_processor import generate_summary, ask_gemini
from utils.tts_engine import text_to_speech_with_karaoke, get_available_voices
from utils.database import init_db, save_history_record, get_all_history

# Initialize Database
init_db()

st.set_page_config(page_title="AI Audiobook Suite", layout="wide", page_icon="🎧")

def render_karaoke_player(mp3_path, vtt_path):
    """Renders HTML5 media player with WebVTT subtitle track for word sync."""
    if not os.path.exists(mp3_path) or not os.path.exists(vtt_path):
        st.error("Audio or Subtitle file missing.")
        return

    with open(mp3_path, "rb") as f:
        mp3_b64 = base64.b64encode(f.read()).decode("utf-8")
    with open(vtt_path, "rb") as f:
        vtt_b64 = base64.b64encode(f.read()).decode("utf-8")

    player_html = f"""
    <div style="background-color: #1e1e1e; padding: 20px; border-radius: 12px; margin-top: 10px;">
        <audio id="audio-element" controls style="width: 100%; margin-bottom: 15px;">
            <source src="data:audio/mp3;base64,{mp3_b64}" type="audio/mp3">
            <track id="caption-track" default kind="captions" srclang="en" src="data:text/vtt;base64,{vtt_b64}">
        </audio>
        <div id="karaoke-display" style="
            font-size: 1.25rem; 
            line-height: 1.8; 
            color: #d1d5db; 
            background: #111827; 
            padding: 20px; 
            border-radius: 8px; 
            min-height: 100px;
            border-left: 4px solid #3b82f6;
        ">
            <em>Subtitles/Karaoke will display here as audio plays...</em>
        </div>
    </div>

    <script>
        const audio = document.getElementById('audio-element');
        const display = document.getElementById('karaoke-display');

        audio.addEventListener('loadedmetadata', () => {{
            const track = audio.textTracks[0];
            if (track) {{
                track.mode = 'hidden';
                track.oncuechange = () => {{
                    const cue = track.activeCues[0];
                    if (cue) {{
                        display.innerHTML = '<span style="color: #60a5fa; font-weight: bold;">' + cue.text + '</span>';
                    }}
                }};
            }}
        }});
    </script>
    """
    st.components.v1.html(player_html, height=220)

# Sidebar
st.sidebar.title("🎧 Audio Controls")
voices = get_available_voices()
selected_voice_label = st.sidebar.selectbox("Voice Model", list(voices.keys()))
selected_voice_id = voices[selected_voice_label]

tabs = st.tabs(["📖 Converter & Player", "📜 Session Audio History"])

# Tab 1: Processing & Conversion
with tabs[0]:
    st.title("📚 AI Audiobook Generator")
    uploaded_file = st.file_uploader("Upload PDF Document", type=["pdf"])

    if uploaded_file is not None:
        if "pdf_text" not in st.session_state or st.session_state.get("file_name") != uploaded_file.name:
            with st.spinner("Extracting PDF content..."):
                st.session_state.pdf_text = extract_text_from_pdf(uploaded_file)
                st.session_state.file_name = uploaded_file.name

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📄 Text & AI Tools")
            st.text_area("Extracted Preview", st.session_state.pdf_text[:1500] + "...", height=250)

            if st.button("Generate Summary"):
                with st.spinner("Generating summary via Gemini..."):
                    st.session_state.summary = generate_summary(st.session_state.pdf_text)
            
            if "summary" in st.session_state:
                st.info(st.session_state.summary)

            st.markdown("---")
            q = st.text_input("Ask a question about this PDF:")
            if q:
                with st.spinner("Analyzing context..."):
                    st.write(ask_gemini(st.session_state.pdf_text, q))

        with col2:
            st.subheader("🔊 Audio & Karaoke Sync")
            conversion_source = st.radio("Target Text", ["Full Document Excerpt (5,000 chars)", "AI Summary Only"])

            if st.button("Convert to Audiobook"):
                text_to_convert = ""
                if conversion_source == "AI Summary Only":
                    if "summary" not in st.session_state:
                        st.session_state.summary = generate_summary(st.session_state.pdf_text)
                    text_to_convert = st.session_state.summary
                else:
                    text_to_convert = st.session_state.pdf_text[:5000]

                with st.spinner("Synthesizing neural audio & subtitle timings..."):
                    mp3_path, vtt_path = text_to_speech_with_karaoke(text_to_convert, selected_voice_id)
                    save_history_record(
                        title=st.session_state.file_name,
                        voice=selected_voice_label,
                        summary=st.session_state.get("summary", "N/A"),
                        mp3_path=mp3_path,
                        vtt_path=vtt_path
                    )
                    st.session_state.current_mp3 = mp3_path
                    st.session_state.current_vtt = vtt_path
                    st.success("Conversion complete!")

            if "current_mp3" in st.session_state:
                render_karaoke_player(st.session_state.current_mp3, st.session_state.current_vtt)

# Tab 2: Audio History
with tabs[1]:
    st.title("📜 Generated Audio Library")
    history_records = get_all_history()

    if not history_records:
        st.info("No audio tracks saved yet. Convert a PDF to populate this history.")
    else:
        for rec in history_records:
            rec_id, title, voice, summary, mp3_path, vtt_path, created_at = rec
            with st.expander(f"🎵 {title} — ({created_at})"):
                st.write(f"**Voice:** {voice}")
                st.write(f"**Summary:** {summary}")
                if os.path.exists(mp3_path) and os.path.exists(vtt_path):
                    render_karaoke_player(mp3_path, vtt_path)
                    with open(mp3_path, "rb") as f:
                        st.download_button("Download MP3", f, file_name=os.path.basename(mp3_path), key=f"dl_{rec_id}")
                else:
                    st.warning("Source audio files missing on server storage.")