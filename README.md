# HCC Student Technical Support and Routing POC

## ITAI 4373 Capstone Project

This private repository contains the proof-of-concept implementation for Group 1's capstone continuation of the midterm project:

**AI Delegation Pilot for HCC Student Technical Support and Routing**

The POC demonstrates student-facing technical-support intake, deterministic safety screening, issue classification, risk-aware delegation, verified public HCC guidance, structured human handoff, and synthetic evaluation.

## Important implementation note

The current v6 POC does **not** use a trained machine-learning model or large language model for routing. It implements the AI delegation strategy with deterministic, inspectable rules so that higher-risk decisions can be tested, reproduced, and explained. A future language-model component could assist with natural-language understanding or summarization, but the hard safety boundary should remain outside the model.

## Scope

The POC:

- accepts a short student technical-support problem,
- checks the input for account-security, identity, credential, and sensitive-data indicators,
- assigns a support category,
- assigns Delegation Tier 1 through Tier 4,
- provides approved low-risk guidance,
- produces a human-review summary for Tier 3 and Tier 4 cases,
- redacts common sensitive values before user text appears in the handoff summary,
- uses a small local knowledge base based on public HCC support pages,
- provides session-only routing analytics,
- evaluates the routing logic on 100 labeled synthetic cases.

The POC does **not**:

- connect to production HCC systems,
- access student records,
- authenticate users,
- reset passwords,
- unlock accounts,
- modify MFA settings,
- verify identity,
- perform administrative account actions.

## Core flow

1. Student enters a technical-support problem.
2. The input guard checks for security, identity, credential, account-administration, and sensitive-data signals.
3. The classifier assigns the most specific supported issue category.
4. The delegation engine applies category-specific risk scores and assigns Tier 1 through Tier 4.
5. Any input-guard trigger forces Tier 4 regardless of the normal category result.
6. Tier 1 and Tier 2 cases receive approved public information or low-risk troubleshooting.
7. Tier 3 cases require human review and receive a structured handoff summary.
8. Tier 4 cases stop autonomous troubleshooting and require authorized human escalation.
9. The Evaluation Dashboard runs the labeled synthetic regression set through the same routing logic.

## Delegation tiers

| Tier | Meaning | Typical use |
| --- | --- | --- |
| 1 | Public information / approved FAQ | General support routing |
| 2 | Guided low-risk troubleshooting | Canvas, browser/device, Wi-Fi |
| 3 | Human review / routing | Password/login, Microsoft 365/student email, unknown issues |
| 4 | Human-controlled security or account action | Compromise, MFA/identity, credential disclosure, privileged account actions |

The five displayed risk dimensions are:

- financial risk,
- operational risk,
- reputational risk,
- task complexity,
- human expertise.

Each dimension is scored from 1 to 5 using the predicted category. The displayed total supports explanation, but **the total does not calculate the tier**. Tier assignment is conservative and category-based, with the input guard able to force Tier 4.

## Classifier priority and confidence

The classifier checks categories in this order:

1. Account Security / Compromise
2. Microsoft 365 / Student Email
3. Canvas / Eagle Online
4. Wi-Fi / Connectivity
5. Browser / Device
6. General Routing
7. Password / Login
8. Unknown / Human Review

The first category with a keyword match wins. There is no tie-break step because the classifier exits on the first matching category in the priority order. If nothing matches, the case becomes **Unknown / Human Review** and routes to Tier 3.

Confidence is a deterministic display value based on the number of matched keywords and a category-specific starting value. It is **not** a calibrated probability. Unknown cases display 0.35 confidence.

## Safety boundary

Tier 4 is a hard boundary. The input guard forces Tier 4 for detected:

- suspected account compromise,
- MFA or identity-security issues,
- credential disclosure,
- account-administration requests,
- possible sensitive personal data.

Examples:

- "I forgot my password" -> Password / Login -> Tier 3
- "I need help resetting my password" -> Password / Login -> Tier 3
- "Reset my password for me" -> account-administration trigger -> Tier 4
- "Unlock my account" -> Tier 4
- "Disable my MFA" -> Tier 4
- "Someone changed my MFA and I think my account was hacked" -> Tier 4

Common password values, PINs, security answers, SSN-like values, nine-digit ID-like values, and card-like numbers are redacted before raw input appears in a human handoff summary. Session analytics store only category, tier, and escalation status.

## Clone and run

Repository:

`https://github.com/oscarecortez361/ITAI4373-HCC-Student-Tech-Support`

### Windows PowerShell

```powershell
git clone https://github.com/oscarecortez361/ITAI4373-HCC-Student-Tech-Support.git
cd ITAI4373-HCC-Student-Tech-Support
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local Streamlit address shown in the terminal, normally:

`http://localhost:8501`

### macOS / Linux

```bash
git clone https://github.com/oscarecortez361/ITAI4373-HCC-Student-Tech-Support.git
cd ITAI4373-HCC-Student-Tech-Support
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## Run the synthetic evaluation

Windows:

```powershell
python tests\evaluation.py
```

macOS / Linux:

```bash
python tests/evaluation.py
```

The test runner calls the same guard, classifier, and delegation logic used by the Streamlit application. Detailed results are also available through the in-app **Evaluation Dashboard**.

## Current v6 synthetic results

| Metric | v6 result |
| --- | ---: |
| Synthetic cases | 100 |
| Category accuracy | 100.0% |
| Tier accuracy | 100.0% |
| Tier 4 recall | 100.0% |
| False safe answers | 0 |
| Escalation rate | 45.0% |

These figures apply only to the team's labeled synthetic cases. They are **not production accuracy**. The same 100-case set was used to identify routing failures and refine the deterministic rules, so it functions as a tuning and regression set rather than a held-out test set.

The larger test cycle showed the following progression:

- v4: 87% category accuracy, 92% tier accuracy, 93.3% Tier 4 recall, 1 false-safe answer
- v5: 99% category accuracy, 99% tier accuracy, 100% Tier 4 recall
- v6: 100% category accuracy, 100% tier accuracy, 100% Tier 4 recall

This progression documents iterative correction of observed failures. Real student language and production conditions remain untested.

## Repository structure

```text
app.py
requirements.txt
README.md

src/
  analytics.py
  case_summary.py
  classifier.py
  delegation.py
  evaluation_engine.py
  input_guard.py
  knowledge_base.py
  troubleshooting.py

data/
  hcc_knowledge_base.json
  synthetic_test_cases.csv
  evaluation_metrics.json
  evaluation_results.csv

tests/
  evaluation.py
```

## Public HCC knowledge-base sources

The local knowledge base contains selected public guidance and source URLs for:

- Eagle Online (Canvas) Support
- Password Reset Information
- Student Email / Eagle ID
- Technology Support

These entries support public guidance and routing only. The POC performs no production account actions.

Before final submission, public-source wording and URLs should be reverified and the verification date recorded in the project documentation.

## Code-quality approach

The core routing code is separated into small modules for the input guard, classifier, delegation engine, troubleshooting, knowledge retrieval, case-summary generation, analytics, and evaluation. Safety-sensitive behavior is deterministic and inspectable. Comments and docstrings are used where the purpose or safety consequence of a rule is not obvious from the code.

## AI-use disclosure

ChatGPT was used to assist with project planning, code drafting, debugging, synthetic test-case development, documentation drafting, and review. Claude was used as a second-opinion reviewer of the technical documentation and capstone-requirement coverage. The team manually ran the POC, inspected routing behavior, reviewed public HCC source information, executed the evaluation, and retained responsibility for final project decisions and claims.

## Version summary

- **v1:** initial 20-case functional POC
- **v2:** public HCC knowledge-base integration
- **v3:** explicit Account Security / Compromise classification and demo polish
- **v4:** 100-case evaluation dashboard and first large regression run
- **v5:** classifier and Tier 4 safety hardening based on observed failures
- **v6:** final connectivity-routing refinement, 100-case regression pass, and documentation hardening

## Current status

v6 is the current capstone baseline. Remaining capstone work is primarily documentation, business/performance analysis, presentation preparation, team collaboration, and final packaging rather than adding new routing features.
