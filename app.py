import html
import random
import requests
import streamlit as st
import trivia

st.set_page_config(page_title="Trivia Vault", page_icon="🗝️", layout="centered")

# Colours match pranitikhurana.com so the two feel like one place
TAG_STYLES = [
    ("#001D51", "#FFFFFF"),  # navy
    ("#6D712E", "#FFFFFF"),  # olive
    ("#5C0E22", "#FFFFFF"),  # burgundy
    ("#87D1EA", "#001D51"),  # sky blue
    ("#321912", "#FFFFFF"),  # mahogany
]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500&display=swap');
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp li, .stApp label, .stApp input,
.stApp button, .stApp [data-testid="stMarkdownContainer"], .stApp [data-testid="stCaptionContainer"],
.hero, .fact-card, .q-text, .opt, .verdict, .score-big, .eyebrow { font-family: 'Inter', -apple-system, sans-serif !important; }
.stApp {
  background-color: #FBF7EC;
  background-image:
    linear-gradient(rgba(16,12,8,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(16,12,8,0.05) 1px, transparent 1px);
  background-size: 40px 40px;
}
h1, h2, h3 { color: #100C08 !important; letter-spacing: -0.02em; }
.hero h1 { font-size: 3rem; font-weight: 800; margin: 0 0 4px; line-height: 1.05; }
.hero p { color: #5C584F; font-size: 1.05rem; margin: 0 0 18px; }
.hero .count { font-family: 'IBM Plex Mono', monospace; font-size: .85rem; color: #6D712E; }

.fact-card { background: #FFFFFF; border: 1px solid rgba(16,12,8,0.12); border-radius: 8px;
             padding: 16px 18px; margin-bottom: 12px; }
.fact-card.featured { border: 2px solid #001D51; }
.fact-card p { margin: 0 0 10px; color: #100C08; line-height: 1.6; }
.fact-meta { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
.tag { display: inline-block; font-size: .72rem; font-weight: 600; padding: 3px 10px; border-radius: 999px; }
.source { font-size: .78rem; color: #5C584F; margin-left: auto; }
.source a { color: #001D51; }
.eyebrow { font-size: .72rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase;
           color: #6D712E; margin-bottom: 6px; }

.q-progress { font-family: 'IBM Plex Mono', monospace; font-size: .8rem; color: #5C584F; }
.q-text { font-size: 1.35rem; font-weight: 700; color: #100C08; line-height: 1.35; margin: 6px 0 18px; }
.opt { border-radius: 8px; padding: 10px 14px; margin-bottom: 8px; border: 1px solid rgba(16,12,8,0.12);
       background: #FFFFFF; color: #100C08; }
.opt.right { background: #E7EEDC; border-color: #6D712E; font-weight: 600; }
.opt.wrong { background: #F3DDE1; border-color: #5C0E22; text-decoration: line-through; }
.verdict { font-weight: 700; font-size: 1.05rem; margin: 10px 0 6px; }
.verdict.right { color: #6D712E; } .verdict.wrong { color: #5C0E22; }
.score-big { font-size: 3.2rem; font-weight: 800; color: #001D51; line-height: 1; }

.stButton > button { border-radius: 8px; border: 1px solid rgba(16,12,8,0.18); background: #FFFFFF;
                     color: #100C08; font-weight: 500; min-height: 3rem; }
.stButton > button:hover { border-color: #001D51; color: #001D51; }
.stButton > button[kind="primary"] { background: #001D51; color: #FFFFFF; border: none; }
.stButton > button[kind="primary"]:hover { background: #0A2E6E; color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)


def tag_html(tags, palette):
    return "".join(
        f'<span class="tag" style="background:{palette[t][0]};color:{palette[t][1]}">{html.escape(t)}</span>'
        for t in tags
    )


def fact_card(f, palette, featured=False, eyebrow=""):
    source = ""
    if f["source"]:
        s = html.escape(f["source"])
        link = s if s.startswith("http") else f"https://{s}"
        source = f'<span class="source">Source: <a href="{link}" target="_blank" rel="noopener">{s}</a></span>'
    st.markdown(
        f'<div class="fact-card{" featured" if featured else ""}">'
        f'{f"<div class=eyebrow>{eyebrow}</div>" if eyebrow else ""}'
        f'<p>{html.escape(f["fact"])}</p>'
        f'<div class="fact-meta">{tag_html(f["tags"], palette)}{source}</div></div>',
        unsafe_allow_html=True,
    )


# ---------- Load the sheet ----------
try:
    facts = trivia.load_trivia()
except requests.RequestException:
    st.error("Couldn't reach the trivia sheet just now. Refresh the page in a minute to try again.")
    st.stop()

tags = trivia.all_tags(facts)
palette = {t: TAG_STYLES[i % len(TAG_STYLES)] for i, t in enumerate(tags)}
quiz_pool = trivia.quizzable(facts)

st.markdown(f"""
<div class="hero">
  <h1>Trivia Vault</h1>
  <p>Things I've learned and didn't want to forget. Browse the collection, or test yourself.</p>
  <span class="count">{len(facts)} facts · {len(tags)} topics</span>
</div>
""", unsafe_allow_html=True)

mode = st.segmented_control("Mode", ["Browse", "Quiz me"], default="Browse",
                            key="mode", label_visibility="collapsed")


# ---------- Browse ----------
def browse():
    col1, col2 = st.columns([3, 1], vertical_alignment="bottom")
    query = col1.text_input("Search", placeholder="Search facts, e.g. Venice, Michelangelo, 1913")
    if col2.button("🎲 Random fact", use_container_width=True):
        st.session_state["random_id"] = random.choice(facts)["id"]

    picked = st.pills("Topics", tags, selection_mode="multi", key="topic_filter")

    if "random_id" in st.session_state:
        fact_card(facts[st.session_state["random_id"]], palette, featured=True, eyebrow="Random fact")

    shown = [
        f for f in facts
        if (not picked or set(picked) & set(f["tags"]))
        and (not query or query.lower() in f["fact"].lower())
    ]
    st.caption(f"Showing {len(shown)} of {len(facts)} facts")
    if not shown:
        st.info("No facts match that search. Try another word or clear the topic filter.")
    for f in shown:
        fact_card(f, palette)


# ---------- Quiz ----------
def start_quiz(pool, n):
    items = [dict(f, options=trivia.build_options(f, facts)) for f in random.sample(pool, min(n, len(pool)))]
    st.session_state["quiz"] = {"items": items, "i": 0, "score": 0, "picked": None, "missed": []}


def pick(option):
    q = st.session_state["quiz"]
    if q["picked"] is not None:
        return  # already answered this one
    item = q["items"][q["i"]]
    q["picked"] = option
    if option == item["answer"]:
        q["score"] += 1
    else:
        q["missed"].append(item)


def next_question():
    q = st.session_state["quiz"]
    q["i"] += 1
    q["picked"] = None


def quiz():
    q = st.session_state.get("quiz")

    if q is None:
        if not quiz_pool:
            st.info("No quiz questions yet. Add QUESTION and ANSWER columns to the sheet to enable the quiz.")
            return
        st.markdown("#### Set up your quiz")
        quiz_tags = [t for t in tags if any(t in f["tags"] for f in quiz_pool)]
        topic = st.selectbox("Topic", ["All topics"] + quiz_tags)
        pool = quiz_pool if topic == "All topics" else [f for f in quiz_pool if topic in f["tags"]]
        sizes = [n for n in (5, 10, 20) if n <= len(pool)] or [len(pool)]
        n = st.segmented_control("Questions", sizes, default=sizes[min(1, len(sizes) - 1)],
                                 key="quiz_size")
        st.caption(f"{len(pool)} questions available in this topic")
        if st.button("Start quiz", type="primary", use_container_width=True):
            start_quiz(pool, n or sizes[0])
            st.rerun()
        return

    total = len(q["items"])

    if q["i"] >= total:
        pct = round(100 * q["score"] / total)
        st.markdown(f'<div class="eyebrow">Your score</div><div class="score-big">{q["score"]}/{total}</div>',
                    unsafe_allow_html=True)
        st.write("Flawless. 🏆" if pct == 100 else "Nicely done." if pct >= 70
                 else "Good start: the misses below are worth a reread." if pct >= 40
                 else "Tough round. Read the misses and try again.")
        c1, c2 = st.columns(2)
        if q["missed"] and c1.button(f"Retry the {len(q['missed'])} I missed", type="primary",
                                     use_container_width=True):
            start_quiz(q["missed"], len(q["missed"]))
            st.rerun()
        if c2.button("New quiz", use_container_width=True):
            del st.session_state["quiz"]
            st.rerun()
        if q["missed"]:
            st.markdown("#### What you missed")
            for item in q["missed"]:
                fact_card(item, palette, eyebrow=f"Answer: {html.escape(item['answer'])}")
        return

    item = q["items"][q["i"]]
    st.markdown(f'<div class="q-progress">Question {q["i"] + 1} of {total} · Score {q["score"]}</div>',
                unsafe_allow_html=True)
    st.progress(q["i"] / total)
    st.markdown(f'<div class="q-text">{html.escape(item["question"])}</div>', unsafe_allow_html=True)

    if q["picked"] is None:
        # One row of columns per pair, so phones (which stack columns) keep the same order
        for row in range(0, len(item["options"]), 2):
            cols = st.columns(2)
            for n, option in enumerate(item["options"][row:row + 2], start=row):
                cols[n - row].button(option, key=f"opt-{q['i']}-{n}", on_click=pick, args=(option,),
                                     use_container_width=True)
        if st.button("Quit quiz", key="quit"):
            del st.session_state["quiz"]
            st.rerun()
        return

    correct = q["picked"] == item["answer"]
    for option in item["options"]:
        cls = "right" if option == item["answer"] else "wrong" if option == q["picked"] else ""
        st.markdown(f'<div class="opt {cls}">{html.escape(option)}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="verdict {"right" if correct else "wrong"}">'
        f'{"Correct!" if correct else "Not quite. The answer is " + html.escape(item["answer"]) + "."}</div>',
        unsafe_allow_html=True,
    )
    fact_card(item, palette, eyebrow="The full story")
    st.button("See results" if q["i"] + 1 == total else "Next question", type="primary",
              on_click=next_question, use_container_width=True)


if mode == "Quiz me":
    quiz()
else:
    browse()
