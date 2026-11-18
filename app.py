"""Streamlit app for the HCC Student Technical Support and Routing POC.

Two tabs. The Live Routing Demo takes a student message and runs it through
the input guard, the classifier and the delegation engine, then shows the
tier, the next steps, the verified HCC source and a handoff summary for Tier 3
and Tier 4. The Evaluation Dashboard runs the 100 labeled synthetic cases
through the same functions.

Run with:  python -m streamlit run app.py

This is a proof of concept. It does not log in users, reset passwords or touch
any HCC system, and it keeps no raw message text.
"""
import streamlit as st
import pandas as pd

from src.input_guard import inspect_input
from src.classifier import classify_issue
from src.delegation import assign_tier
from src.troubleshooting import get_guidance
from src.case_summary import build_case_summary
from src.analytics import Event, summarize
from src.knowledge_base import get_knowledge_entry
from src.evaluation_engine import evaluate_cases


# --- Page setup ---
st.set_page_config(
    page_title="HCC Student Tech Support POC",
    page_icon="🛠️",
    layout="wide",
)

st.title("HCC Student Technical Support and Routing")
st.caption("ITAI 4373 Capstone Proof of Concept")

st.info(
    "Prototype only. Do not enter passwords, MFA codes, Social Security numbers, "
    "student ID numbers, payment information, or other sensitive personal data."
)

# --- Session state ---
# Streamlit reruns this whole script on every click, so the list of routed
# cases lives in session_state. Each Event holds only category, tier and
# escalated. The message text itself is never stored.
if "events" not in st.session_state:
    st.session_state.events = []

# --- Sidebar ---
with st.sidebar:
    st.header("POC Controls")
    st.write(
        "This prototype uses deterministic rules so the delegation and safety logic "
        "can be inspected, tested, and explained during the capstone demo."
    )
    if st.button("Clear session analytics"):
        st.session_state.events = []
        st.rerun()

live_tab, eval_tab = st.tabs(["Live Routing Demo", "Evaluation Dashboard"])

# --- Live routing tab ---
with live_tab:
    issue = st.text_area(
        "Describe the technical problem",
        height=140,
        placeholder="Example: Canvas keeps rejecting my login and I do not know where to go for help.",
    )

    if st.button("Analyze and route issue", type="primary") and issue.strip():
        # Routing steps, in order:
        # 1. The guard looks for security and sensitive data triggers.
        # 2. The classifier picks a category.
        # 3. The delegation engine picks the tier. A guard trigger forces Tier 4.
        # 4. The troubleshooting module returns the approved steps for that tier.
        guard = inspect_input(issue)
        classification = classify_issue(issue)
        decision = assign_tier(
            classification.category,
            guard.force_tier4,
            guard.reasons,
        )
        guidance = get_guidance(classification.category, decision.tier)

        # Record only category, tier and escalation status for the session
        # analytics below.
        st.session_state.events.append(
            Event(
                category=classification.category,
                tier=decision.tier,
                escalated=decision.human_required,
            )
        )

        st.subheader("Routing result")

        c1, c2, c3 = st.columns(3)
        c1.metric("Category", classification.category)
        c2.metric("Delegation tier", f"Tier {decision.tier}")
        c3.metric("Human required", "Yes" if decision.human_required else "No")

        st.write(f"**Tier function:** {decision.tier_name}")
        # Confidence is a display value from the keyword count, not a
        # calibrated probability.
        st.write(f"**Classifier confidence:** {classification.confidence:.0%}")
        # Five risk dimensions scored 1 to 5, so the maximum is 25. The score
        # only explains the risk to the viewer. The tier is set by category
        # and by the guard, not by this number.
        st.write(f"**Decision score:** {decision.total_score}/25")

        # Banner by tier: Tier 4 stops, Tier 3 needs a person, Tier 1 and 2 may
        # show the approved low-risk guidance.
        if decision.tier == 4:
            st.error("Tier 4 hard stop: this issue requires human support.")
            if guard.reasons:
                st.write("**Safety triggers:** " + ", ".join(guard.reasons))
        elif decision.tier == 3:
            st.warning("AI may organize the issue, but a human should review the next action.")
        else:
            st.success("Low-risk guidance may be shown within the approved playbook.")

        st.subheader("Recommended next steps")
        for step in guidance:
            st.write(f"• {step}")

        # Guidance and source link from the small local knowledge base of
        # public HCC pages. Not every category has an entry.
        kb_entry = get_knowledge_entry(classification.category)
        if kb_entry:
            st.subheader("Verified HCC information")
            for item in kb_entry.get("guidance", []):
                st.write(f"• {item}")
            st.caption("Public source used for this POC:")
            st.markdown(f"[{kb_entry['source_name']}]({kb_entry['source_url']})")

        # Tier 3 and Tier 4 get a handoff summary. Common sensitive values are
        # redacted inside build_case_summary before the text is shown.
        if decision.tier >= 3:
            st.subheader("Human handoff summary")
            summary = build_case_summary(
                issue,
                classification.category,
                decision.tier,
                decision.reasons,
            )
            st.code(summary, language=None)

    # --- Session analytics ---
    # Counts for this browser session only. They reset when the session ends
    # or when the sidebar button is pressed.
    st.divider()
    st.subheader("Session analytics")

    session_summary = summarize(st.session_state.events)
    a1, a2, a3 = st.columns(3)
    a1.metric("Cases analyzed", session_summary["total_cases"])
    a2.metric("Escalations", session_summary["escalated_cases"])
    a3.metric("Tier 4 cases", session_summary["tier4_cases"])

    if st.session_state.events:
        df = pd.DataFrame(
            [
                {
                    "Category": event.category,
                    "Tier": event.tier,
                    "Escalated": event.escalated,
                }
                for event in st.session_state.events
            ]
        )
        st.bar_chart(df["Tier"].value_counts().sort_index())
        st.dataframe(df, width="stretch")

# --- Evaluation dashboard tab ---
# Reruns the labeled synthetic cases each time the page loads. These 100 cases
# were also used to tune the rules, so this is a regression check and not
# proof of accuracy on real student messages.
with eval_tab:
    st.header("100-Case Synthetic Evaluation")
    st.write(
        "This dashboard evaluates the routing and delegation logic against a labeled "
        "synthetic test set. No student records are used."
    )

    metrics, results = evaluate_cases()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Test cases", metrics["total_cases"])
    m2.metric("Category accuracy", f"{metrics['category_accuracy']:.1%}")
    m3.metric("Tier accuracy", f"{metrics['tier_accuracy']:.1%}")
    m4.metric("Tier 4 recall", f"{metrics['tier4_recall']:.1%}")

    n1, n2 = st.columns(2)
    n1.metric("Tier 4 false safe answers", metrics["false_safe_answers"])
    n2.metric("Escalation rate", f"{metrics['escalation_rate']:.1%}")

    results_df = pd.DataFrame(results)

    st.subheader("Predicted tier distribution")
    st.bar_chart(results_df["predicted_tier"].value_counts().sort_index())

    st.subheader("Category performance")
    category_summary = (
        results_df.groupby("expected_category")
        .agg(
            Cases=("issue", "count"),
            Correct=("category_correct", "sum"),
        )
        .reset_index()
    )
    category_summary["Accuracy"] = category_summary["Correct"] / category_summary["Cases"]
    st.dataframe(category_summary, width="stretch")

    st.subheader("Evaluation results")
    st.dataframe(results_df, width="stretch")

    csv_bytes = results_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download evaluation results CSV",
        data=csv_bytes,
        file_name="hcc_poc_evaluation_results.csv",
        mime="text/csv",
    )

    # Safety criterion: every case labeled Tier 4 must come back as Tier 4.
    # If this banner turns red, fix the Tier 4 routing before anything else.
    if metrics["tier4_recall"] == 1.0 and metrics["false_safe_answers"] == 0:
        st.success("Safety criterion passed: all labeled Tier 4 cases escalated with zero Tier 4 false safe answers.")
    else:
        st.error("Safety criterion failed: review Tier 4 routing before final submission.")
