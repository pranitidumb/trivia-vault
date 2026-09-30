"""Loads trivia from the published Google Sheet.

The sheet is the source of truth: add a row there and it shows up here
within a few minutes (Google refreshes published sheets about every 5 min,
and we cache for 5 min on our side too).

Expected columns (case and spacing don't matter):
  FACTS, SOURCE, TAGS, SURE?, QUESTION, ANSWER, WRONG 1, WRONG 2, WRONG 3
Only FACTS is required. Rows without a QUESTION and ANSWER still appear in
Browse, just not in the quiz.
"""
import csv
import io
import random
import requests
import streamlit as st

SHEET_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vSJQP6tIyNxgkRiPHr--oHSODtQghpxSRIeam1wKKAP4wQ6lGSKLMXQo0rxw4ndflnCMTPSmjPBMdq9"
    "/pub?gid=0&single=true&output=csv"
)


def _split_tags(raw):
    """'Art, history ' -> ['Art', 'History']"""
    return [t.strip().title() for t in (raw or "").split(",") if t.strip()]


@st.cache_data(ttl=300, show_spinner=False)
def load_trivia():
    """Returns a list of fact dicts. Raises requests.RequestException if the
    sheet can't be reached."""
    resp = requests.get(SHEET_CSV_URL, timeout=15)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    reader = csv.DictReader(io.StringIO(resp.text))
    facts = []
    for row in reader:
        row = {(k or "").strip().upper(): (v or "").strip() for k, v in row.items()}
        fact = row.get("FACTS") or row.get("FACT")
        if not fact:
            continue
        facts.append({
            "id": len(facts),
            "fact": fact,
            "source": row.get("SOURCE", ""),
            "tags": _split_tags(row.get("TAGS")),
            "question": row.get("QUESTION", ""),
            "answer": row.get("ANSWER", ""),
            "wrong": [row.get(f"WRONG {n}", "") for n in (1, 2, 3) if row.get(f"WRONG {n}", "")],
        })
    return facts


def all_tags(facts):
    counts = {}
    for f in facts:
        for t in f["tags"]:
            counts[t] = counts.get(t, 0) + 1
    return sorted(counts, key=lambda t: (-counts[t], t))


def quizzable(facts):
    return [f for f in facts if f["question"] and f["answer"]]


def build_options(item, facts):
    """Answer + up to 3 wrong options, shuffled. If a row has fewer than 3
    wrong answers filled in, borrow answers from other facts with the same
    tag so the question still works."""
    options = [item["answer"]] + [w for w in item["wrong"] if w != item["answer"]]
    if len(options) < 4:
        same_tag = [f["answer"] for f in facts
                    if f["answer"] and f["id"] != item["id"] and set(f["tags"]) & set(item["tags"])]
        others = [f["answer"] for f in facts if f["answer"] and f["id"] != item["id"]]
        for pool in (same_tag, others):
            random.shuffle(pool)
            for a in pool:
                if len(options) >= 4:
                    break
                if a not in options:
                    options.append(a)
    random.shuffle(options)
    return options
