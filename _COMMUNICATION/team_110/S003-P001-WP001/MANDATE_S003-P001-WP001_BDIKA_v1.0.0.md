---
id: MANDATE_S003-P001-WP001_BDIKA_v1.0.0
from: Team 100 (Chief System Architect)
to: Team 110 (Domain Architect)
date: 2026-04-20
type: BDIKA_SPEC_MANDATE
wp: S003-P001-WP001
project: shaked-wg-agent
status: ACTIVE
verdict: PENDING
he_title: מנדט בדיקת אפיון (L-GATE_S — שכבת ארכיטקטורה)
---

# מנדט בדיקה — S003-P001-WP001: מודל נתונים מולטי-טננט (PostgreSQL)

## מטרה

**בדיקת אפיון** (אינספקציה ארכיטקטונית) לפני מימוש: לוודא ש-**LOD300 (LOCKED)** ו-**LOD400 (v1.0.0)** עקביים זה עם זה, ניתנים למימוש ללא הזמנת הבהרות, ומיושרים לקוד הקיים (`persistence.py`, `config.py`, `runner.py`) ולתלות **S003-P001-WP002**.

זהו **מנדט Team 110** — לא מחליף את **מנדט Team 190** ל-L-GATE_S / חוקה; השניים משלימים (ארכיטקטורה → חוקה).

## 1. כותרת

| שדה | ערך |
|-----|-----|
| שער יעד | L-GATE_S (הרשאת אפיון) — היבט **ארכיטקטורה** |
| Work Package | S003-P001-WP001 |
| מסלול | B |
| פרופיל | L2.5 |
| ארטיפקטים | `LOD300_S003-P001-WP001.md` (LOCKED), `LOD400_S003-P001-WP001.md` |

## 2. היקף הבדיקה (מה לבדוק)

| # | נושא | ציפייה |
|---|--------|--------|
| B-01 | עקביות LOD300 ↔ LOD400 | טבלאות, FK, env, שכבת `persistence` — תואמים ל-§5 LOD300 ול-Appendix A LOD400 |
| B-02 | דואליות backend | `PERSISTENCE_BACKEND=json` default שומרת על CI/התנהגות קיימת |
| B-03 | חוזה `load_config` ב-PostgreSQL | מיפוי `ProjectConfig` מזהה לנתיב JSON (או תיעוד פערים מפורשים) |
| B-04 | בידוד טננט | `tenant_id` בכל שאילתה; אימות ב-repository (AC-06) — מספיק ל-MVP |
| B-05 | הפרדת היקפים | JWT, RLS, billing — **מחוץ** ל-WP001; אין דליפה ל-LOD400 |
| B-06 | מיגרציה | סדר P1–P8, idempotency, כישלון import — התנהגות מוגדרת |
| B-07 | תלות WP002 | מזהי ישויות/טבלאות שירותי auth עתידיים — לא שוברים סכמה |

## 3. קבצים לקריאה חובה

| נתיב | מטרה |
|------|--------|
| `_aos/work_packages/S003-P001-WP001/LOD300_S003-P001-WP001.md` | מודל מערכת |
| `_aos/work_packages/S003-P001-WP001/LOD400_S003-P001-WP001.md` | מפרט מימוש |
| `shaked_wg_agent/persistence.py` | קווי בסיס ל-parity |
| `shaked_wg_agent/config.py` | `load_config` / מודל ישויות S002 |
| `_aos/roadmap.yaml` | שורת WP S003-P001-WP001 |

## 4. פלט מצופה (Team 110)

אחת מהאפשרויות:

- קובץ `_COMMUNICATION/team_110/S003-P001-WP001/REVIEW_S003-P001-WP001_BDIKA_v1.0.0.md` — **APPROVE** / **APPROVE_WITH_NOTES** / **BLOCK** עם הערות ממוקדות, או
- הערה ב-team_00 לניתוב, אם הזרימה הארגונית אינה דורשת קובץ נפרד

## 5. אילוצים

- **אינה** ולידציה חוקתית (זה **Team 190** — ראו מנדט `L-GATE_VALIDATE` נפרד).
- **אינה** ביצוע מימוש (זה **builder** לאחר L-GATE_S + EXT-CP1 לפי המתודולוגיה).

## 6. ניתוב

לאחר **APPROVE** (או **APPROVE_WITH_NOTES** בלי BLOCK), Team 00/100 מנתבים ל-**Team 190** לביצוע מנדט L-GATE_S החוקתי (`MANDATE_*LOD400_REVIEW*` או מנדט S נפרד), אם עדיין לא הוחזר verdict.

---
*MANDATE BDIKA v1.0.0 — team_100 → team_110 — 2026-04-20*
