import wave
from io import BytesIO
import json
import random
import streamlit as st
from google import genai
client = genai .Client(
    api_key=st.secrets["GEMINI_API_KEY"])
# ----------------------------
# Question Bank
# ----------------------------
QUESTIONS = {
    "Behavioral": [
        "Tell me about a time you faced a conflict with a coworker or teammate. How did you handle it?",
        "Describe a situation where you had to meet a tight deadline. What did you do?",
        "Give an example of a mistake you made at work or school. How did you fix it?",
        "Tell me about a time you received difficult feedback. How did you respond?",
        "Describe a time you had to work with someone whose working style was very different from yours.",
        "Tell me about a goal you set for yourself and how you achieved it.",
    ],
    "Situational": [
        "If you disagreed with your manager's decision, what would you do?",
        "How would you handle being given multiple urgent tasks with the same deadline?",
        "What would you do if you noticed a colleague struggling but they hadn't asked for help?",
        "If you realized halfway through a project that your approach wasn't working, what would you do?",
        "How would you respond if a client or customer was unhappy with your work?",
        "What would you do if you were asked to do something you felt was outside your skill set?",
    ],
    "General": [
        "Tell me about yourself.",
        "Why do you want to work here?",
        "What are your greatest strengths?",
        "What is an area you're currently working to improve?",
        "Where do you see yourself in five years?",
        "Why should we hire you?",
    ],
    "Technical Generic": [
        "Walk me through how you would approach solving a problem you've never seen before.",
        "How do you stay updated with new tools or technologies in your field?",
        "Describe your process for debugging or troubleshooting an issue.",
        "How do you decide which tool or approach to use for a given task?",
        "Explain a technical concept from your field to someone with no background in it.",
        "How do you ensure the quality of your work before considering it complete?",
    ],
    "Leadership": [
        "Tell me about a time you led a team or project, even informally.",
        "How do you motivate people who seem disengaged?",
        "Describe a time you had to make an unpopular decision.",
        "How do you handle delegating tasks to others?",
        "Tell me about a time you helped resolve a disagreement within a team.",
        "How do you give constructive feedback to someone you're working with?",
    ],
}

CATEGORIES = list(QUESTIONS.keys())

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(page_title="Smart Interview Coach",
                   page_icon="🎤", layout="centered")

st.title("🎤 Smart Interview Coach")
st.write("Practice your interview skills. Pick a category, answer the question, and keep going!")

# ----------------------------
# Session State Init
# ----------------------------
if "category" not in st.session_state:
    st.session_state.category = CATEGORIES[0]

if "current_question" not in st.session_state:
    st.session_state.current_question = random.choice(
        QUESTIONS[st.session_state.category])

if "answer" not in st.session_state:
    st.session_state.answer = ""

if "history" not in st.session_state:
    st.session_state.history = []  # list of (category, question, answer)


def pick_new_question():
    """Pick a random question from the current category, avoiding immediate repeats if possible."""
    pool = QUESTIONS[st.session_state.category]
    if len(pool) > 1:
        choices = [q for q in pool if q != st.session_state.current_question]
    else:
        choices = pool
    st.session_state.current_question = random.choice(choices)
    st.session_state.answer = ""


# ----------------------------
# Category Selector
# ----------------------------
selected_category = st.selectbox(
    "Choose a category:",
    CATEGORIES,
    index=CATEGORIES.index(st.session_state.category),
)

if selected_category != st.session_state.category:
    st.session_state.category = selected_category
    st.session_state.current_question = random.choice(
        QUESTIONS[selected_category])
    st.session_state.answer = ""

st.markdown("---")

# ----------------------------
# Show Question
# ----------------------------
st.subheader("Question")
st.write(f"**{st.session_state.current_question}**")

# ----------------------------
# Answer Box
# ----------------------------
st.session_state.answer = st.text_area(
    "Your answer:",
    value=st.session_state.answer,
    height=180,
    placeholder="Type your answer here...",
)

# ----------------------------
# Buttons
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Submit Answer", use_container_width=True):
        if st.session_state.answer.strip():
            st.session_state.history.append(
                (st.session_state.category,
                 st.session_state.current_question, st.session_state.answer)
            )
            prompt = f"""
            You are an expert interview coach.
            Interview Question:
            {st.session_state.current_question}
            Candidate Answer:
            {st.session_state.answer}
            Evaluate the answer and provide:
            1. Score out of 10
            2. strengths
            3. Weaknesses
            4. Suggestions for improvement 
            5. A better sample answer
            Be honest and encouraging.
            """
            response = client.models.generate_content(
                model="gemini-flash-latest", contents=prompt
            )
            st.markdown("## AI Feedback")
            st.write(response.text)
            st.warning("Please write an answer before submitting.")

with col2:
    if st.button("➡️ Next Question", use_container_width=True):
        pick_new_question()
        st.rerun()

# ----------------------------
# Past Answers (optional review)
# ----------------------------
if st.session_state.history:
    st.markdown("---")
    with st.expander(f"📚 Review your answers ({len(st.session_state.history)})"):
        for i, (cat, q, a) in enumerate(reversed(st.session_state.history), 1):
            st.markdown(f"**{i}. [{cat}]** {q}")
            st.write(a)
            st.markdown("")
# ============================================================
# NEW FEATURES: Voice Practice + Resume Analyzer + Dashboard
# ============================================================

FILLER_WORDS = ["um", "uh", "umm", "uhh", "like", "you know", "sort of",
                "kind of", "basically", "actually", "literally", "i mean"]

if "history" not in st.session_state:
    st.session_state.history = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = None
if "resume_feedback" not in st.session_state:
    st.session_state.resume_feedback = None


def get_audio_duration_seconds(audio_bytes):
    try:
        with wave.open(BytesIO(audio_bytes), "rb") as wf:
            return wf.getnframes() / float(wf.getframerate())
    except Exception:
        return None


def analyze_vocal_delivery(audio_bytes, transcript):
    duration_s = get_audio_duration_seconds(audio_bytes)
    words = [w.strip(".,!?") for w in transcript.split() if w.strip(".,!?")]
    word_count = len(words)
    wpm = round(word_count / (duration_s / 60), 1) if duration_s else None

    filler_count = sum(transcript.lower().count(f) for f in FILLER_WORDS)
    filler_ratio = filler_count / word_count if word_count else 0

    pace_score, pace_label = 100, "N/A"
    if wpm is not None:
        if 110 <= wpm <= 165:
            pace_score, pace_label = 100, "Great pace"
        elif wpm < 110:
            pace_score, pace_label = max(
                40, 100 - (110 - wpm) * 1.5), "A bit slow / hesitant"
        else:
            pace_score, pace_label = max(
                40, 100 - (wpm - 165) * 1.2), "Talking fast — may read as nervous"

    filler_score = max(0, 100 - filler_ratio * 400)
    vocal_confidence = round(0.6 * pace_score + 0.4 * filler_score)

    return {"wpm": wpm, "pace_label": pace_label, "filler_count": filler_count,
            "vocal_confidence": vocal_confidence}


def transcribe_audio(audio_bytes):
    response = client.models.generate_content(
        model="gemini-flash-latest",
        contents=[{"text": "Transcribe this spoken interview answer exactly, word for word."},
                  {"inline_data": {"mime_type": "audio/wav", "data": audio_bytes}}],
    )
    return response.text


def score_answer(question, answer, category):
    prompt = f"""You are a strict but fair interview coach.
Question ({category}): {question}
Answer: "{answer}"
Respond in raw JSON only, no markdown fences:
{{"score": <1-10>, "strengths": ["..."], "improvements": ["..."], "model_answer_snippet": "..."}}"""
    raw = client.models.generate_content(
        model="gemini-flash-latest", contents=prompt).text
    raw = raw.strip().removeprefix("json").removeprefix("").removesuffix("").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"score": None, "raw": raw}


def extract_resume_text(uploaded_file):
    name = uploaded_file.name.lower()
    data = uploaded_file.read()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(BytesIO(data)).pages)
    elif name.endswith(".docx"):
        import docx
        return "\n".join(p.text for p in docx.Document(BytesIO(data)).paragraphs)
    return data.decode("utf-8", errors="ignore")


def analyze_resume(resume_text, target_role=""):
    prompt = f"""You are a blunt hiring manager. Give honest, specific feedback, no generic praise.
Target role: {target_role or "Not specified"}
Resume: \"\"\"{resume_text}\"\"\"
Respond in raw JSON only:
{{"overall_score": <1-10>, "strengths": ["..."], "weaknesses": ["..."],
"missing_quantification": ["..."], "one_line_verdict": "..."}}"""
    raw = client.models.generate_content(
        model="gemini-flash-latest", contents=prompt).text
    raw = raw.strip().removeprefix("json").removeprefix("").removesuffix("").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"error": "Could not parse", "raw": raw}


st.markdown("---")
st.header("🎙️ Voice Practice, Resume Analyzer & Dashboard")

new_tab1, new_tab2, new_tab3 = st.tabs(
    ["🗣️ Voice Practice", "📄 Resume Analyzer", "📊 Dashboard"])

with new_tab1:
    category = st.selectbox("Category", list(QUESTIONS.keys()), key="new_cat")
    if st.button("🎲 New Question", key="new_q_btn"):
        st.session_state.current_q = random.choice(QUESTIONS[category])
    if "current_q" not in st.session_state:
        st.session_state.current_q = random.choice(QUESTIONS[category])

    st.markdown(f"### “{st.session_state.current_q}”")
    audio_value = st.audio_input("Record your answer")
    typed = st.text_area("...or type your answer")

    if st.button("✅ Submit Answer", key="submit_new"):
        answer_text, vocal_stats = None, None
        if audio_value is not None:
            answer_text = transcribe_audio(audio_value.getvalue())
            vocal_stats = analyze_vocal_delivery(
                audio_value.getvalue(), answer_text)
        elif typed.strip():
            answer_text = typed.strip()

        if answer_text:
            result = score_answer(
                st.session_state.current_q, answer_text, category)
            if result.get("score") is not None:
                st.session_state.history.append({"category": category, "question": st.session_state.current_q,
                                                 "answer": answer_text, "score": result["score"],
                                                 "feedback": result, "vocal_stats": vocal_stats})
                st.progress(result["score"] / 10)
                st.markdown(f"*Score: {result['score']}/10*")
                if vocal_stats:
                    v1, v2, v3 = st.columns(3)
                    v1.metric("Pace", f"{vocal_stats['wpm']} wpm")
                    v2.metric("Filler words", vocal_stats["filler_count"])
                    v3.metric("Vocal Confidence",
                              f"{vocal_stats['vocal_confidence']}/100")
                for s in result.get("strengths", []):
                    st.markdown(f"✅ {s}")
                for imp in result.get("improvements", []):
                    st.markdown(f"🔧 {imp}")

with new_tab2:
    target_role = st.text_input("Target role (optional)")
    uploaded = st.file_uploader(
        "Upload resume (PDF/DOCX)", type=["pdf", "docx"])
    if uploaded and st.button("🔍 Analyze Resume"):
        st.session_state.resume_text = extract_resume_text(uploaded)
        st.session_state.resume_feedback = analyze_resume(
            st.session_state.resume_text, target_role)

    fb = st.session_state.resume_feedback
    if fb and "error" not in fb:
        st.metric("Resume Score", f"{fb['overall_score']}/10")
        st.markdown(f"*Verdict:* {fb['one_line_verdict']}")
        for s in fb.get("strengths", []):
            st.markdown(f"✅ {s}")
        for w in fb.get("weaknesses", []):
            st.markdown(f"⚠️ {w}")
        for m in fb.get("missing_quantification", []):
            st.markdown(f"📊 {m}")

with new_tab3:
    history = st.session_state.history
    if not history:
        st.info("Answer some questions to see stats here.")
    else:
        scores = [h["score"] for h in history]
        st.metric("Avg Score", f"{sum(scores)/len(scores):.1f}/10")
        st.line_chart({"Score": scores})
        for h in reversed(history):
            with st.expander(f"[{h['category']}] {h['question'][:50]}... — {h['score']}/10"):
                st.markdown(f"*Answer:* {h['answer']}")
                if h.get("vocal_stats"):
                    st.markdown(f"Vocal: {h['vocal_stats']['wpm']} wpm, "
                                f"{h['vocal_stats']['filler_count']} fillers, "
                                f"{h['vocal_stats']['vocal_confidence']}/100 confidence")
