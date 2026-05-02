---
type: COWORK_CONTEXT
title: "AOS — Cowork Session Context"
version: "1.2.0"
authored_by: team_200
date: "2026-05-02"
status: ACTIVE
usage: "Read at the start of every Cowork session — hub or spoke. Propagated to all spoke _COMMUNICATION/team_200/ via aos_sync_all.sh."
current_release: "v4.0.0 'Autonomous' — tagged 2026-05-02"
---

> **🚀 CURRENT RELEASE: AOS v4.0.0 'Autonomous' (tagged 2026-05-02)**
>
> Milestone AOS-V4-MS001 complete. 11/11 WPs LOD500_LOCKED. 159/159 ACs verified. Hub `validate_aos.sh` extended to **45 checks** (W7 added 39–44; W11 added Check 45 WAN dual-stack `[SKIP:WARN]`). New: **Iron Rule #15** (IPv6-only WAN compatibility), **ADR048**, lean-kit WAN canon + probe.
>
> 9 spokes received the propagation; spoke team_99 sessions have 14 days from pull (deadline 2026-05-16) to run `wan_dual_stack_probe.sh` and reply with status per `MSG-HUB-20260502-005`.
>
> Master closure: `_COMMUNICATION/team_00/MASTER_CLOSURE_V4_0_0_v1.0.0.md`.

# AOS — Cowork Session Context

## מה זה AOS?

**Agents OS (AOS) הוא תשתית — לא מוצר.**

AOS הוא מסגרת ממשל (governance framework) ומנוע אורקסטרציה לניהול פרויקטים רב-דומיין ורב-מנוע. הוא מנהל פרויקטי spoke דרך מבנה Hub-and-Spoke: ה-Hub הוא `agents-os`, כל פרויקט עצמאי הוא spoke. AOS לא כותב קוד מוצר של spoke — הוא מגדיר את כללי המשחק, ה-methodology, ומנגנוני הממשל שלהם.

---

## מבנה Hub + Spoke

```
agents-os (Hub)
├── methodology/       ← SSoT למתודולוגיה
├── core/              ← מנוע AOS v3 (FastAPI + DB)
├── lean-kit/          ← Kit ניהולי לפי פרופיל (L0/L2/L2.5)
├── governance/        ← ADRs, Iron Rules
├── _aos/              ← שכבת ממשל (READ-ONLY לצוותים לא-ממשל)
└── _COMMUNICATION/    ← תיבות דואר לכל צוות
```

כל spoke קורא `_aos/` כ-snapshot לקריאה בלבד. שינויים ב-AOS layer מוגשים כ-GCR דרך Team 100.

---

## רשימת פרויקטים מלאה (SSoT: `_aos/projects.yaml`)

| ID | שם | נתיב מקומי | פרופיל | סטטוס |
|----|----|------------|--------|-------|
| `agents-os` | Agents OS (Hub) | `/Users/nimrod/Documents/agents-os` | L0 + L2 | ✅ פעיל |
| `tiktrack` | TikTrack Phoenix | `/Users/nimrod/Documents/TikTrack-Phoenix_AOSProject` | L2 | ✅ פעיל |
| `smallfarmsagents` | SmallFarmsAgents | `/Users/nimrod/Documents/SmallFarmsAgents` | L0 | ✅ פעיל |
| `eyalamit` | Eyal Amit — EyalAmit.co.il | `/Users/nimrod/Documents/Eyal Amit/EyalAmit.co.il-2026` | L0 | ✅ פעיל |
| `hobbithome` | HobbitHome (WordPress Hebrew) | `/Users/nimrod/Documents/HobbitHome` | L0 | ✅ פעיל |
| `microgreens` | Israel Microgreens (Blender V2) | `/Users/nimrod/Documents/israel Microgreens/IsraelMicrogreens-BlenderV2-Project` | L0 | ✅ פעיל |
| `shaked-wg-agent` | Shaked WG Basel Search Agent | `/Users/nimrod/Documents/shaked-wg-agent` | L0 | ✅ פעיל |
| `nimrod-book` | Nimrod Book (Context Substrate) | `/Users/nimrod/Documents/nimrod-book` | L0 | ✅ פעיל |
| `aos-sandbox-lean` | AOS Sandbox Lean | `/Users/nimrod/Documents/AOS-Sandbox-Lean` | L0 | ✅ פעיל |
| `aos-sandbox-full` | AOS Sandbox Full | `/Users/nimrod/Documents/AOS-Sandbox-Full` | L2 | ✅ פעיל |
| `agros-insite` | Agros Insite (AI) | `/Users/nimrod/Documents/agros-insite` | L0→L2 | ✅ פעיל (שרת: `/data/projects/agros-insite`) |

### הערות על פרויקטים
- **agents-os**: Hub. מנהל את כל ה-spokes. L0 בפועל + מנוע L2 פעיל (core/).
- **tiktrack**: הפרויקט המתקדם ביותר — L2 dual-profile, FastAPI + DB.
- **agros-insite**: סוכן פרודוקטיביות אישי. Phase A: Gmail. נפרש על waldhomeserver. `future_profile: L2`.
- **nimrod-book**: Context substrate — לא פרויקט רגיל. מוגדר כ-`CONTENT_SUBSTRATE`.
- **Famely Newsletter**: קיים אך **מחוץ** למערכת AOS — אסור ליצור deliverables שלו ב-agents-os.

---

## פרופילי פריסה

| פרופיל | תיאור | מאפיין |
|--------|--------|---------|
| **L0** | Lean/Manual | lean-kit בלבד, אין DB, ניהול קבצים ידני |
| **L2** | AOS v3 / Dashboard | מנוע FastAPI + PostgreSQL, API mutations חובה |
| **L2.5** | Managed Agent Pipeline | ל-WPs מורכבים (≥2 צוותים, MEDIUM/HIGH risk) |
| **L3** | AOS v4 "Autonomous" | ✅ **שוחרר 2026-05-02** (tag `v4.0.0`). Track Model + Engine Matrix + MSG infrastructure + AUTO-ACTIVATION dryrun + validate_aos.sh 45 checks + IR#15 IPv6-only WAN compatibility |

בחירת פרופיל: `lean-kit/PROFILE_SELECTION_GUIDE.md`

---

## מפת מנועים וסביבות עבודה

AOS הוא מולטי-מנוע. הצוותות פועלות על פלטפורמות שונות — לא רק Claude:

| צוות | שם | מנוע | סביבה | תפקיד |
|------|-----|-------|--------|--------|
| **Team 00** | Nimrod (Principal) | human | chat | Principal — אישור הכל |
| **Team 10** | Gateway / Builder | Cursor | cursor IDE | אורקסטרציה + ביצוע WPs |
| **Team 20** | Backend Implementation | Cursor | IDE | API, DB, services |
| **Team 30** | Frontend Implementation | Cursor | IDE | UI, components, pages |
| **Team 35** | Design Studio | claude-design | design-sandbox | עיצוב, wireframes — on-demand בלבד |
| **Team 40** | DevOps (light) | Cursor | IDE | infra, CI |
| **Team 50** | QA | Cursor | IDE | L-GATE_BUILD + validations |
| **Team 60** | DevOps & Platform | Cursor | IDE | port canon, infra, scripts |
| **Team 70** | Documentation | OpenAI Codex | isolated | docs, AS_MADE_REPORT |
| **Team 80** | Research | variable (Claude Chat+) | chat | מחקר חיצוני, ניתוח |
| **Team 90** | Default Validator | Cursor Composer 2 | isolated | L-GATE_BUILD, ולידציות ביניים |
| **Team 98** | Phone Joker | Claude Sonnet (Cowork mobile) | chat | Dispatch נייד — ביצוע מיידי, universal |
| **Team 99** | Home Server Team | Claude Code | terminal (waldhomeserver) | server ops, SSH/Tailscale |
| **Team 100** | Chief System Architect | Claude Sonnet 4.6 | terminal | ממשל, ADRs, roadmap, `/AOS_gov-*` |
| **Team 110** | AOS Domain Architect | Cursor Composer 2 | IDE | ספק/LOD/GATE_2 review |
| **Team 170** | Domain Archive | OpenAI Codex | isolated | ארכיב cross-domain |
| **Team 190** | Senior Constitutional Validator | OpenAI Codex | isolated | L-GATE_ELIGIBILITY, SPEC, VALIDATE |
| **Team 200** | **AOS Cowork Bundle Execution** | **Claude Sonnet (Desktop)** | **claude-desktop + Project** | **P-AOS-4 bundles** |

### צוותות OUT_OF_GATE_ISOLATED (לא בתהליך gate רגיל)
- **Team 98** — Dispatch מובייל, universal scope, worktrees אוטומטיים
- **Team 99** — שרת ביתי, Claude Code על waldhomeserver
- **Team 200** — Cowork bundle, domain-specific per invocation, isolated branch

כולם דורשים L-GATE_VALIDATE של Team 190 לפני merge ל-main.

---

## סביבות Cowork וה-Entry Points שלהן

Team 200 מופעל בשלוש סביבות, לכל אחת entry point שונה:

| סביבה | Entry Point | מתי |
|--------|-------------|-----|
| **P-AOS-4 bundle** (Claude Desktop + Project) | `PROJECT_INSTRUCTIONS.md` → Custom Instructions | בנדל מאושר ע"י Team 00 |
| **Cowork folder-based** (סשן נוכחי) | `CLAUDE.md` נטען אוטומטית | Cowork mode עם workspace |
| **Session ב-spoke** | `_aos/governance/team_200.md` + `_COMMUNICATION/team_200/` של ה-spoke | כשנפרסים על TikTrack וכו' |

### ממשל ו-Propagation
- **`/AOS_gov-sync`** — מפיץ team contracts (`core/governance/team_*.md`) לכל spoke (API: `POST /api/governance/sync {"scope": "teams"}`). מוגבל ל-team_00 + team_100 בלבד.
- **`/AOS_gov-update`** — הפצה מלאה (methodology + directives + team contracts) דרך `aos_sync_all.sh`. מוגבל ל-team_00 + team_100 בלבד.
- **קובץ זה** מיועד להפצה ל-spoke דרך `/AOS_gov-update` (GCR פתוח ל-team_100).

---

## הרשאות כתיבה — Team 200 (Cowork)

### מותר לכתוב:
- `_COMMUNICATION/team_200/` — תיקייה מלאה
- הודעות בין-צוותיות (MSG, RESPONSE, mandate, verdict) → כל `_COMMUNICATION/team_X/`

### אסור לגעת (ללא אישור Team 00):
- `_aos/` — שכבת ממשל (שינויים חייבים דרך API כשDB פעיל)
- קוד אפליקציה של spoke projects (TikTrack, SmallFarmsAgents, וכו')
- `core/`, `lean-kit/`, `methodology/`, `governance/` — קריאה מותרת, כתיבה רק במסגרת bundle מאושר
- **Famely Newsletter** — אסור בכלל ביצירת deliverables

### גישה לפרויקטים:
כל spoke דורש חיבור workspace נפרד + אישור מפורש מ-Team 00.
נתיב handoff בין-פרויקטי: `~/Documents/_agent_comm/outbox/`

---

## מצב עבודה נוכחי (נכון ל-2026-04-23)

**Milestone פעיל: V321** (ממתין לאקטיבציה Team 00 + Team 100)

| WP | Milestone | סטטוס | תיאור |
|----|-----------|-------|--------|
| `AOS-V321-WP-SERVER-GITOPS` | V321 | PLANNED | Server GitOps — waldhomeserver כ-Primary Runtime |
| `AOS-V324-WP-E2E-SCAFFOLD` | V324 | PLANNED | Playwright E2E Scaffold Module |
| `AOS-V324-WP-QA-ENUM-LINT` | V324 | PLANNED | QA Enum Lint Script |
| `AOS-V325-WP-ROADMAP-API` | V325 | PLANNED | Roadmap Mutation API + Slash Commands |
| `AOS-V326-WP-CHECK24-ENFORCEMENT` | V326 | PLANNED | Check 24 v2 Post-Grace Enforcement |
| `AOS-V327-WP-TEAM-MESSAGING` | V327 | **IN_PROGRESS** | AOS Team Messaging Layer |
| `AOS-V328-WP-SYNC-AUTO-COMMIT` | V328 | PLANNED | aos_sync_all.sh Auto-Commit |
| `AOS-V328-WP-SESSION-DISPATCH` | V328 | **IN_PROGRESS** | Session Lifecycle Orchestration |
| `AOS-V329-WP-CONTENT-ARCHETYPE-POLISH` | V329 | PLANNED | CONTENT_SUBSTRATE Glossary |

---

## Iron Rules קריטיים לסשן Cowork

1. **Cross-engine**: builder engine ≠ validator engine — Team 200 לא מאשר עצמו בלי הרשאה מפורשת
2. **Data authority**: כשDB פעיל — mutations רק דרך API (ADR034, Iron Rule #7)
3. **Governance flows** source→snapshot בלבד — לא לערוך `_aos/governance/` ישירות
4. **Governance authority**: `/AOS_gov-update` ו-`/AOS_gov-sync` — Team 00 + Team 100 בלבד
5. **Port canon**: כל listener חדש → רישום ב-`lean-kit/modules/12-home-server-infrastructure/deployment/port-registry.yaml` (Team 60)
6. **Routing display**: תמיד inline fenced block ("── Copy this block ──") + קובץ artifact במקביל
7. **Cross-project boundary**: אסור לגעת בקוד spoke מה-hub. GCR דרך Team 100 לכל שינוי AOS-layer

---

## קבצי מפתח לקריאה

| קובץ | תוכן |
|------|-------|
| `_aos/projects.yaml` | רשם כל הפרויקטים (SSoT) |
| `_aos/roadmap.yaml` | WPs, milestones, gate history |
| `core/definition.yaml` | מודל צוותות + seed DB |
| `_aos/context/PROJECT_CONTEXT.md` | מפת Hub קצרה |
| `methodology/AOS_CONCEPT_AND_PRINCIPLES.md` | Iron Rules מלאים |
| `governance/directives/ADR034_*.md` | Data Authority (DB SSoT) |
| `lean-kit/PROFILE_SELECTION_GUIDE.md` | בחירת פרופיל לWP |
| `_COMMUNICATION/team_200/` | תיקיית Cowork (כתיבה מלאה) |

---

## DB Probe (חובה בסשן טכני)

```bash
python3 -c "from agents_os_v3.modules.management.db import probe_database; print(probe_database())"
```
- `status: online` → כל mutations דרך API בלבד
- `status: offline` → **עצור ודווח ל-Team 00 מיידית** (לא להמשיך אוטומטית)

---

*עודכן: 2026-04-23 | Team 200 — AOS Cowork Bundle Execution*
