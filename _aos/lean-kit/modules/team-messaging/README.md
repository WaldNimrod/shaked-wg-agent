# team-messaging (Hub)

Small lean-kit bundle for **AOS hub** inter-team messaging.

- **ADR:** `governance/directives/ADR043_TEAM_MESSAGING_PROTOCOL_v1.0.0.md`
- **Implementation:** `core/modules/management/team_messaging.py`
- **Routes:** `GET|POST /api/messaging/*` in `core/modules/management/dashboard_routes.py`

Spoke projects may copy this folder for documentation; runtime behavior lives on the hub API.
