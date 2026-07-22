import os
import time
import importlib
import streamlit as st

import db
from gemini_ai import generate_response

db = importlib.reload(db)


def asset_path(filename: str) -> str | None:
    path = os.path.join(os.path.dirname(__file__), "assets", filename)
    return path if os.path.exists(path) else None


def render_html(text: str) -> str:
    """
    Strip ALL leading whitespace from every line of an HTML snippet before
    handing it to st.markdown(unsafe_allow_html=True).

    Streamlit's markdown renderer treats any line indented 4+ spaces as a
    preformatted code block. textwrap.dedent() only removes the *common*
    leading whitespace, which isn't enough once a blank line splits the HTML
    into multiple blocks â€” the next block's lines still carry their original
    (now non-common) indentation and get reinterpreted as code. Stripping
    every line individually avoids that entirely, regardless of blank lines.
    """
    lines = [line.strip() for line in text.strip("\n").splitlines()]
    return "\n".join(lines)


@st.fragment(run_every=1)
def render_timer_fragment(start_time: float, duration_seconds: int, is_locked: bool) -> None:
    elapsed = time.time() - start_time
    remaining = max(0.0, duration_seconds - elapsed)
    mins, secs = divmod(int(max(0, remaining)), 60)
    timer_class = "timer-box"
    if remaining <= 0:
        timer_class += " timer-danger"
    elif remaining <= 5 * 60:
        timer_class += " timer-warning"
    st.markdown(
        render_html(f"""
        <div class="{timer_class}">
            <div class="label">Time Remaining</div>
            <div class="value">{mins:02d}:{secs:02d}</div>
        </div>
        """),
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Page config & global styling
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="IGNITION@2026 AI PROMPT",
    page_icon="",
    layout="wide",
    initial_sidebar_state="collapsed",
)

CUSTOM_CSS = """
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden; display: none;}
    [data-testid="stStatusWidget"] {visibility: hidden; display: none;}
    [data-testid="stDecoration"] {visibility: hidden; display: none;}

    .stApp {
        background: #100e1b;
        color: #ffffff;
    }

    .block-container {
        padding-top: 2.8rem;
        padding-bottom: 2rem;
        max-width: 1320px;
    }



    .brand-kicker {
        color: #967633;
        font-size: 0.8rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0 0 0.35rem 0;
    }

    .brand-title {
        color: #ffffff;
        font-size: 2rem;
        line-height: 1.08;
        font-weight: 800;
        margin: 0 0 0.7rem 0;
    }

    .brand-copy {
        color: #d1d5db;
        font-size: 1rem;
        line-height: 1.55;
        max-width: 60ch;
    }

    .timer-box {
        background: linear-gradient(135deg, #161325, #100e1b);
        color: #ffffff;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 14px 20px;
        text-align: center;
        margin-bottom: 14px;
        font-family: 'SFMono-Regular', Consolas, monospace;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
    }
    .timer-box .label {
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #cbd5e1;
        margin-bottom: 2px;
    }
    .timer-box .value {
        font-size: 2.1rem;
        font-weight: 700;
    }
    .timer-warning .value { color: #f59e0b; }
    .timer-danger .value { color: #fb7185; }

    .round-pill {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        background: rgba(150, 118, 51, 0.16);
        color: #f7d58a;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 10px;
    }

    .char-card {
        background: #131827;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 18px 20px;
        position: sticky;
        top: 1rem;
        color: #ffffff;
        box-shadow: 0 12px 32px rgba(0, 0, 0, 0.24);
    }
    .char-name {
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 0;
        color: #ffffff;
    }
    .char-timeline {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin-bottom: 12px;
    }
    .char-section-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #cbd5e1;
        margin-top: 14px;
        margin-bottom: 4px;
        font-weight: 700;
    }
    .trait-tag {
        display: inline-block;
        background: rgba(150, 118, 51, 0.18);
        color: #f7d58a;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.78rem;
        margin: 2px 4px 2px 0;
    }
    .boundary-box {
        background: rgba(255, 255, 255, 0.04);
        border-left: 4px solid #967633;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.85rem;
        color: #ffffff;
        margin-top: 6px;
    }
    .instructions-box li {
        font-size: 0.85rem;
        margin-bottom: 4px;
        color: #e5e7eb;
    }

    .chat-bubble-user {
        background: rgba(255, 255, 255, 0.06);
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 4px;
        font-size: 0.9rem;
        color: #ffffff;
    }
    .chat-bubble-ai {
        background: rgba(255, 255, 255, 0.04);
        border-radius: 10px;
        padding: 8px 14px;
        margin-bottom: 14px;
        font-size: 0.9rem;
        color: #ffffff;
    }
    .word-count-ok { color: #4ade80; font-weight: 600; }
    .word-count-over { color: #fb7185; font-weight: 700; }
    .stButton > button {
        background: linear-gradient(90deg, #967633 0%, #b89446 100%);
        color: #ffffff;
        border: none;
        border-radius: 12px;
        font-weight: 700;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #b89446 0%, #967633 100%);
        color: #ffffff;
        border: none;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "db_initialized" not in st.session_state:
    db.init_db()
    st.session_state.db_initialized = True

# ---------------------------------------------------------------------------
# Character profile (would normally be uploaded by the administrator)
# ---------------------------------------------------------------------------
CHARACTER = {
    "name": "Nikola Tesla",
    "years": "1856â€“1943",
    "knowledge_ends": 1943,
    "background": (
        "Serbian-American inventor and electrical engineer renowned for his contributions "
        "to the design of the modern alternating current (AC) electricity supply system. "
        "Tesla worked on wireless power transmission, radio, and numerous groundbreaking "
        "electro-mechanical devices, holding hundreds of patents across several countries."
    ),
    "personality_traits": ["Analytical", "Visionary", "Curious", "Independent", "Precise"],
    "speaking_style": ["Formal", "Scientific", "Logical", "Professional", "Respectful"],
    "core_values": ["Scientific discovery", "Innovation", "Precision", "Curiosity", "Humanity"],
}

ROUND_GOALS = {
    1: "Create the basic identity of the AI â€” who the character is, their role, and basic behaviour.",
    2: "Add personality, language style, behaviour, knowledge boundaries, rules, and constraints.",
    3: "Finalize: stronger constraints, natural behaviour, historical consistency, response "
       "formatting, and handling of difficult questions.",
}

# ---------------------------------------------------------------------------
# Login / participant identification
# ---------------------------------------------------------------------------
if "participant_id" not in st.session_state:
    st.session_state.participant_id = None
if "participant_cache" not in st.session_state:
    st.session_state.participant_cache = None
if "judge_evals_cache" not in st.session_state:
    st.session_state.judge_evals_cache = {}
if "judge_eval_ran" not in st.session_state:
    st.session_state.judge_eval_ran = {}
if "judge_eval_pending" not in st.session_state:
    st.session_state.judge_eval_pending = False

bottom_banner_path = asset_path("foot.png")


def render_bottom_banner():
    if bottom_banner_path:
        st.image(bottom_banner_path, width="stretch")


if not st.session_state.participant_id:

    left_col, right_col = st.columns([7, 5], gap="large")
    with left_col:
        logo_path = asset_path("logo.png")
        if logo_path:
            st.image(logo_path, width=170)
        st.markdown('<div class="brand-kicker">IGNITION 2026</div>', unsafe_allow_html=True)
        st.markdown('<div class="brand-title">PROMPT QUEST</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="brand-copy">Enter your chest number to begin. Your 45-minute timer starts as soon as you continue.\n\nYou are tasked with creating AI instructions for the historical character persona Nikola Tesla (Subject to Change), intended for use in an educational environment such as a classroom or museum. Your objective is to ensure the AI consistently portrays Nikola Tesla with historical accuracy, remains fully in character throughout every interaction, reflects his unique personality, speaking style, mannerisms, scientific mindset, and worldview, and uses a creative yet authentic conversational style while resisting any attempts by users to manipulate, confuse, or persuade it into breaking character, ignoring its role, or providing responses that conflict with the historical figure it represents.</div>',
            unsafe_allow_html=True,
        )

    with right_col:
        st.markdown("### Start Session")
        st.caption("Use your chest number to open your workspace.")
        with st.form("login_form"):
            pid = st.text_input("Chest Number", placeholder="e.g. 014")
            name = st.text_input("Display name (optional)", placeholder="e.g. Jordan")
            started = st.form_submit_button("Begin Competition", type="primary", use_container_width=True)
    if started and pid.strip():
        st.session_state.participant_id = pid.strip()
        participant = db.get_or_create_participant(pid.strip(), name.strip() or pid.strip())
        round_cache = {}
        for round_num in (1, 2, 3):
            round_cache[round_num] = db.get_round_data(pid.strip(), round_num) or {
                "participant_id": pid.strip(),
                "round_num": round_num,
                "prompt_text": "",
                "word_count": 0,
                "submitted": 0,
            }
        st.session_state.participant_cache = {
            "participant": participant,
            "rounds": round_cache,
            "conversation": {1: [], 2: [], 3: []},
            "question_counts": {1: 0, 2: 0, 3: 0},
        }
        st.rerun()

    render_bottom_banner()
    st.stop()

participant_id = st.session_state.participant_id
cache = st.session_state.participant_cache
if not cache or cache["participant"]["participant_id"] != participant_id:
    participant = db.get_participant(participant_id)
    if participant is None:
        st.session_state.participant_id = None
        st.session_state.participant_cache = None
        st.warning("Your session could not be found (it may have expired or the app was restarted). Please sign in again.")
        st.rerun()

    round_cache = {}
    convo_cache = {1: [], 2: [], 3: []}
    question_counts = {}
    for round_num in (1, 2, 3):
        round_cache[round_num] = db.get_round_data(participant_id, round_num) or {
            "participant_id": participant_id,
            "round_num": round_num,
            "prompt_text": "",
            "word_count": 0,
            "submitted": 0,
        }
        convo_cache[round_num] = db.get_conversation(participant_id, round_num)
        question_counts[round_num] = len(convo_cache[round_num])
    st.session_state.participant_cache = {
        "participant": participant,
        "rounds": round_cache,
        "conversation": convo_cache,
        "question_counts": question_counts,
    }
    st.session_state.judge_evals_cache[participant_id] = {
        item["question_num"]: item
        for item in db.get_judge_answers(participant_id)
    }
    cache = st.session_state.participant_cache
else:
    participant = cache["participant"]

# Defensive guard: if session state points at a participant_id that isn't
# actually in the database (e.g. the app was restarted, the DB file was
# reset, or the script was run outside a normal `streamlit run` session),
# don't crash â€” just send them back to the login screen.
if participant is None:
    st.session_state.participant_id = None
    st.session_state.participant_cache = None
    st.warning("Your session could not be found (it may have expired or the app was restarted). Please sign in again.")
    st.rerun()

judge_questions = db.get_judge_questions()
judge_answers = st.session_state.judge_evals_cache.setdefault(
    participant_id,
    {item["question_num"]: item for item in db.get_judge_answers(participant_id)},
)

# ---------------------------------------------------------------------------
# Timer & lock state
# ---------------------------------------------------------------------------
elapsed = time.time() - participant["start_time"]
remaining = max(0.0, db.COMPETITION_DURATION_SECONDS - elapsed)
time_up = remaining <= 0
locked = bool(participant["final_submitted"]) or time_up

# Auto-submit on timeout: lock in whatever was last saved.
if time_up and not participant["final_submitted"]:
    db.finalize_submission(participant_id)
    participant["final_submitted"] = 1
    cache["participant"] = participant
    locked = True

# ---------------------------------------------------------------------------
# Layout: left workspace (70%) / right character reference (30%)
# ---------------------------------------------------------------------------
left, right = st.columns([7, 3], gap="large")

current_round = participant["current_round"]

# ================================= LEFT PANEL =================================
with left:
    render_timer_fragment(participant["start_time"], db.COMPETITION_DURATION_SECONDS, locked)

    if locked:
        if participant["final_submitted"] and not time_up:
            st.success("Final prompt submitted. Your workspace is locked.")
        else:
            st.error("Time is up. Your latest saved prompt has been submitted automatically.")

    st.markdown(f'<div class="round-pill">Round {current_round} of 3</div>', unsafe_allow_html=True)
    st.caption(ROUND_GOALS[current_round])

    # --- Navigation across rounds (view-only for completed rounds) ---
    available_rounds = [r for r in (1, 2, 3) if r <= current_round]
    view_round = st.radio(
        "Navigate rounds",
        available_rounds,
        index=available_rounds.index(current_round),
        horizontal=True,
        format_func=lambda r: f"Round {r}" + (" (current)" if r == current_round else " (submitted)"),
        label_visibility="collapsed",
    )
    is_editable_round = (view_round == current_round) and not locked

    round_row = cache["rounds"][view_round]
    word_limit = db.ROUND_WORD_LIMITS[view_round]
    question_limit = db.ROUND_QUESTION_LIMITS[view_round]

    # Seed the editor with the previous round's submitted prompt the first
    # time this round is opened.
    state_key = f"prompt_text_r{view_round}"
    if state_key not in st.session_state:
        seed_text = round_row["prompt_text"]
        if not seed_text and view_round > 1:
            prev = cache["rounds"][view_round - 1]
            seed_text = prev["prompt_text"] if prev else ""
        st.session_state[state_key] = seed_text

    st.markdown("#### Prompt Editor")

    def _on_prompt_change():
        text = st.session_state[state_key]
        wc = len((text or "").split())
        round_row["prompt_text"] = text
        round_row["word_count"] = wc
        cache["rounds"][view_round] = round_row

    prompt_text = st.text_area(
        "Prompt editor",
        key=state_key,
        height=260,
        disabled=not is_editable_round,
        on_change=_on_prompt_change,
        label_visibility="collapsed",
        placeholder=f"Write your Round {view_round} prompt here (max {word_limit} words)...",
    )

    word_count = len((prompt_text or "").split())
    if round_row["word_count"] != word_count and is_editable_round:
        round_row["word_count"] = word_count
        round_row["prompt_text"] = prompt_text or ""
        cache["rounds"][view_round] = round_row

    over_limit = word_count > word_limit
    wc_class = "word-count-over" if over_limit else "word-count-ok"
    st.markdown(
        f'<span class="{wc_class}">{word_count} / {word_limit} words</span>',
        unsafe_allow_html=True,
    )
    if over_limit:
        st.caption("âš ï¸ You are over the word limit. Trim your prompt before submitting.")

    st.markdown("---")

    # --- AI Testing ---
    st.markdown("#### Test Your AI")
    questions_asked = cache["question_counts"].get(view_round, 0)
    questions_left = max(0, question_limit - questions_asked)
    st.caption(f"Questions used this round: {questions_asked} / {question_limit}")

    # Pending-request lock: a click sets this flag and reruns *immediately*,
    # before the (slow) Gemini call happens, so the button re-renders as
    # disabled on the very next frame. This stops rapid re-clicks (e.g. while
    # waiting on a slow or rate-limited response) from firing multiple
    # duplicate API calls, which is what was burning through the free-tier
    # quota (5 requests/minute) after just a few impatient clicks.
    if "ai_call_pending" not in st.session_state:
        st.session_state.ai_call_pending = False
        st.session_state.pending_question = None
        st.session_state.pending_round = None
        st.session_state.pending_prompt_text = None

    request_in_flight = st.session_state.ai_call_pending

    q_key = f"question_input_r{view_round}"
    q_col, btn_col = st.columns([5, 1])
    with q_col:
        question = st.text_input(
            "Ask a question",
            key=q_key,
            disabled=not is_editable_round or questions_left == 0 or request_in_flight,
            label_visibility="collapsed",
            placeholder="Ask your in-progress AI a question...",
        )
    with btn_col:
        ask_clicked = st.button(
            "Asking..." if request_in_flight else "Ask AI",
            type="primary",
            disabled=(
                not is_editable_round
                or questions_left == 0
                or not (prompt_text or "").strip()
                or request_in_flight
            ),
            use_container_width=True,
        )

    # Phase 1: click received â€” lock immediately and rerun before calling
    # Gemini, so the UI reflects "in progress" right away.
    if ask_clicked and question.strip() and not request_in_flight:
        st.session_state.ai_call_pending = True
        st.session_state.pending_question = question.strip()
        st.session_state.pending_round = view_round
        st.session_state.pending_prompt_text = prompt_text or ""
        st.rerun()

    # Phase 2: the actual (slow) call happens here, only on the run where
    # the lock is already set â€” the button is disabled the whole time.
    if st.session_state.ai_call_pending and st.session_state.pending_round == view_round:
        prior_history = cache["conversation"].get(view_round, [])
        with st.spinner("Asking Gemini..."):
            response = generate_response(
                CHARACTER,
                st.session_state.pending_prompt_text,
                st.session_state.pending_question,
                view_round,
                conversation_history=prior_history,
            )
        db.add_conversation_entry(participant_id, view_round, st.session_state.pending_question, response)
        new_entry = {
            "participant_id": participant_id,
            "round_num": view_round,
            "question": st.session_state.pending_question,
            "response": response,
            "ts": time.time(),
        }
        cache["conversation"].setdefault(view_round, []).append(new_entry)
        cache["question_counts"][view_round] = len(cache["conversation"][view_round])
        st.session_state.ai_call_pending = False
        st.session_state.pending_question = None
        st.session_state.pending_round = None
        st.session_state.pending_prompt_text = None
        st.rerun()

    if is_editable_round and questions_left == 0:
        st.caption("You've used all your questions for this round. Keep refining your prompt below.")

    # --- Conversation history ---
    st.markdown("#### Conversation History")
    history = cache["conversation"].get(view_round, [])
    if not history:
        st.caption("No questions asked yet this round.")
    else:
        # Newest first: the box below has a fixed height and doesn't
        # auto-scroll, so a freshly-added answer at the *bottom* of a long
        # list would be invisible until you manually scrolled down. Showing
        # newest-first guarantees the latest response is always the first
        # thing visible.
        with st.container(height=260):
            for entry in reversed(history):
                st.markdown(
                    f'<div class="chat-bubble-user"><strong>You:</strong> {entry["question"]}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="chat-bubble-ai"><strong>(AI):</strong> {entry["response"]}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")

    # --- Submit controls ---
    if is_editable_round:
        submit_disabled = over_limit or word_count == 0
        if view_round < 3:
            if st.button(f"Submit Round {view_round}", type="primary", disabled=submit_disabled):
                db.save_round_data(participant_id, view_round, round_row["prompt_text"], round_row["word_count"])
                db.submit_round(participant_id, view_round)
                db.update_current_round(participant_id, view_round + 1)
                round_row["submitted"] = 1
                cache["rounds"][view_round] = round_row
                participant["current_round"] = view_round + 1
                cache["participant"] = participant
                st.success(f"Round {view_round} submitted. Round {view_round + 1} unlocked.")
                time.sleep(0.6)
                st.rerun()
        else:
            confirm_key = "confirm_final_submit"
            if not st.session_state.get(confirm_key):
                if st.button("Submit Final Prompt", type="primary", disabled=submit_disabled):
                    st.session_state[confirm_key] = True
                    st.rerun()
            else:
                st.warning(
                    "This is final. Once confirmed, editing will be permanently disabled "
                    "and your prompt will be locked for judging."
                )
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Confirm Final Submission", type="primary"):
                        db.save_round_data(participant_id, 3, round_row["prompt_text"], round_row["word_count"])
                        db.submit_round(participant_id, 3)
                        db.finalize_submission(participant_id)
                        round_row["submitted"] = 1
                        participant["final_submitted"] = 1
                        cache["rounds"][3] = round_row
                        cache["participant"] = participant
                        final_prompt = round_row["prompt_text"] or ""
                        judge_results = {}
                        st.session_state.judge_eval_ran[participant_id] = False
                        st.session_state[confirm_key] = False
                        st.rerun()
                with c2:
                    if st.button("Cancel"):
                        st.session_state[confirm_key] = False
                        st.rerun()
    else:
        st.caption("This round has already been submitted and is read-only.")

    if participant["final_submitted"]:
        if not st.session_state.judge_eval_ran.get(participant_id):
            existing_count = len(judge_answers)
            if existing_count < len(judge_questions):
                final_prompt = cache["rounds"][3]["prompt_text"] or ""
                judge_results = {}
                st.session_state.judge_eval_pending = True
                with st.spinner("Running judge evaluation..."):
                    for item in judge_questions:
                        qnum = item["question_num"]
                        answer = generate_response(
                            CHARACTER,
                            final_prompt,
                            item["question_text"],
                            3,
                            conversation_history=cache["conversation"].get(3, []),
                        )
                        db.save_judge_answer(participant_id, qnum, answer)
                        judge_results[qnum] = {
                            "participant_id": participant_id,
                            "question_num": qnum,
                            "answer_text": answer,
                            "answered": 1,
                            "ts": time.time(),
                        }
                st.session_state.judge_evals_cache[participant_id] = judge_results
                st.session_state.judge_eval_ran[participant_id] = True
                st.session_state.judge_eval_pending = False
                st.rerun()
            else:
                st.session_state.judge_eval_ran[participant_id] = True
        st.markdown("---")
        st.markdown("### Judge Evaluation")
        st.caption("The three judge prompts are automatically answered by the submitted AI using the final Round 3 prompt.")
        for item in judge_questions:
            qnum = item["question_num"]
            existing = judge_answers.get(qnum, {})
            st.markdown(f"**Judge Question {qnum}**")
            st.write(item["question_text"])
            st.markdown(
                f'<div class="chat-bubble-ai"><strong>AI:</strong> {existing.get("answer_text", "Pending evaluation.")}</div>',
                unsafe_allow_html=True,
            )

# ================================= RIGHT PANEL =================================
with right:
    traits_html = "".join(f'<span class="trait-tag">{t}</span>' for t in CHARACTER["personality_traits"])
    style_html = "".join(f"<li>{s}</li>" for s in CHARACTER["speaking_style"])
    values_html = "".join(f"<li>{v}</li>" for v in CHARACTER["core_values"])

    st.markdown(
        render_html(f"""
        <div class="char-card">
            <div class="char-name">{CHARACTER['name']}</div>
            <div class="char-timeline">{CHARACTER['years']} &middot; Knowledge ends in {CHARACTER['knowledge_ends']}</div>

            <div class="char-section-title">Background</div>
            <div style="font-size:0.88rem; color:#e5e7eb; line-height:1.65;">{CHARACTER['background']}</div>

            <div class="char-section-title">Personality Traits</div>
            <div>{traits_html}</div>

            <div class="char-section-title">Speaking Style</div>
            <ul class="instructions-box" style="margin:0; padding-left:18px;">{style_html}</ul>

            <div class="char-section-title">Core Values</div>
            <ul class="instructions-box" style="margin:0; padding-left:18px;">{values_html}</ul>

            <div class="char-section-title">Knowledge Boundary</div>
            <div class="boundary-box">The AI must only possess knowledge available during the character's lifetime.</div>

            <div class="char-section-title">Competition Instructions</div>
            <ul class="instructions-box" style="margin:0; padding-left:18px;">
                <li>Stay historically accurate.</li>
                <li>Never allow the AI to break character.</li>
                <li>Keep within the word limit.</li>
                <li>Use testing wisely.</li>
            </ul>
        </div>
        """),
        unsafe_allow_html=True,
    )

render_bottom_banner()





