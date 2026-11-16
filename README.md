# HCC Student Technical Support and Routing POC

## Purpose

This repository is a proof of concept for the ITAI 4373 capstone continuation of the Group 1 midterm project:

**AI Delegation Pilot for HCC Student Technical Support and Routing**

The POC demonstrates a student-facing intake and routing workflow. It does **not** connect to production HCC systems, does **not** access student records, and does **not** perform account changes.

## Core flow

1. Student enters a technical support problem.
2. A deterministic input guard checks for account-security, identity, credential, and sensitive-data indicators.
3. The issue classifier assigns a support category.
4. The delegation engine assigns Tier 1 through Tier 4.
5. Low-risk issues receive approved troubleshooting guidance.
6. Tier 3 issues produce a structured human-review summary.
7. Tier 4 issues stop autonomous troubleshooting and require human escalation.
8. Session-only analytics show routing and escalation outcomes.

## Safety boundary

Tier 4 is a hard boundary. Requests involving suspected account compromise, MFA takeover, identity verification, credential sharing, or other sensitive account actions must be escalated to a human.

The current POC uses local deterministic rules so the safety logic is easy to inspect and test. A language model can be added later behind these controls.

## Windows setup

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Run the starter evaluation

```powershell
python tests\evaluation.py
```

## Repository structure

```text
app.py
requirements.txt
README.md

src/
  input_guard.py
  classifier.py
  delegation.py
  troubleshooting.py
  case_summary.py
  analytics.py

data/
  hcc_knowledge_base.json
  synthetic_test_cases.csv

tests/
  evaluation.py
```

## Current status

This is the first functional skeleton. Before final submission the team should:

- Re-verify public HCC source content before final submission and record the verification date.
- Expand the synthetic test set toward the planned 100 cases.
- Record routing accuracy and Tier 4 recall.
- Add a polished analytics view.
- Document architecture, testing, limitations, and ethical safeguards.
- Keep real student information out of the prototype.

## Suggested capstone success metrics

- Correct first-route accuracy
- Tier 4 recall: target 100 percent on security/account-compromise test cases
- Incorrect safe-answer rate
- Escalation rate
- Estimated human triage time saved

## AI-use note

AI tools may be used to assist with drafting, troubleshooting, and code review. Team members should verify code behavior, test outputs, sources, and all claims before submission.

## Verified public HCC sources added in v2

The POC now contains public-source entries for:

- Eagle Online (Canvas) Support
- Password Reset Information
- Student Email / Eagle ID
- Technology Support

These sources are used only for public guidance and routing. The POC still performs no production account actions.

## v3 demo polish

- Added explicit `Account Security / Compromise` classification.
- Security/account-compromise cases remain Tier 4 and human-controlled.
- Removed the deprecated Streamlit `use_container_width` call.

## v4 evaluation dashboard

- Expanded the synthetic evaluation set to 100 labeled cases.
- Added automated category accuracy, tier accuracy, Tier 4 recall, escalation rate, and false-safe-answer metrics.
- Added an in-app Evaluation Dashboard tab.
- Added downloadable evaluation results CSV.
- Keeps the evaluation fully synthetic; no student records are used.

## v5 classifier hardening

The 100-case evaluation exposed routing ambiguities that were hidden by the 20-case starter set.
The classifier was updated so named services take precedence over generic login wording, routing language is recognized more broadly, and security-compromise wording is labeled explicitly.
The deterministic Tier 4 guard was also expanded for stolen-account and stolen-credential phrasing.

## v6 final routing refinement

The 100-case evaluation identified one remaining false route:
`The internet works for a minute and then disconnects.`

The classifier was updated to recognize generic `internet` connectivity wording as
Wi-Fi / Connectivity. This change was made from observed test evidence rather than
by adding features without a demonstrated need.

The synthetic evaluation should not be interpreted as production validation. It is
evidence that the deterministic POC behaves as intended on the team's labeled test set.
