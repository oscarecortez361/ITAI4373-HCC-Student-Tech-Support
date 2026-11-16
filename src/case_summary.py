def build_case_summary(issue_text: str, category: str, tier: int, reasons: list[str]) -> str:
    safe_text = issue_text.strip()
    if len(safe_text) > 500:
        safe_text = safe_text[:500] + "..."

    reason_text = "; ".join(reasons) if reasons else "No special safety trigger detected."

    return (
        f"Issue summary: {safe_text}\n"
        f"Category: {category}\n"
        f"Delegation tier: Tier {tier}\n"
        f"Routing reason: {reason_text}\n"
        "Requested action: Human review and appropriate routing if unresolved."
    )
