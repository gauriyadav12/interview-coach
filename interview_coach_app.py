import streamlit as st
import random

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
st.set_page_config(page_title="Smart Interview Coach", page_icon="🎤", layout="centered")

st.title("🎤 Smart Interview Coach")
st.write("Practice your interview skills. Pick a category, answer the question, and keep going!")

# ----------------------------
# Session State Init
# ----------------------------
if "category" not in st.session_state:
    st.session_state.category = CATEGORIES[0]

if "current_question" not in st.session_state:
    st.session_state.current_question = random.choice(QUESTIONS[st.session_state.category])

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
    st.session_state.current_question = random.choice(QUESTIONS[selected_category])
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
                (st.session_state.category, st.session_state.current_question, st.session_state.answer)
            )
            st.success("Answer saved! Great job — hit 'Next Question' to keep practicing.")
        else:
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
