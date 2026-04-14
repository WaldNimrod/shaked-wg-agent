"""CLI entry point: python -m shaked_wg_agent [run|status|list]"""
from __future__ import annotations

import argparse
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from shaked_wg_agent.config import DATA_DIR

# Load .env from project root (two levels up from this file)
load_dotenv(Path(__file__).parent.parent / ".env")

logger = logging.getLogger(__name__)
console = Console()


def _profile_id_for_city(city_id: str) -> str | None:
    """Return profile_id of the first profile JSON whose city_id matches."""
    profiles_dir = DATA_DIR / "profiles"
    if not profiles_dir.is_dir():
        return None
    for path in sorted(profiles_dir.glob("*.json")):
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("city_id") == city_id:
            return str(raw["profile_id"])
    return None


def cmd_run(args: argparse.Namespace) -> None:
    """Trigger a full scan across all enabled sources."""
    from shaked_wg_agent.runner import run_scan

    profile_id: str | None = args.profile
    if args.city is not None and profile_id is None:
        logging.basicConfig(level=logging.WARNING)
        logger.warning("--city is deprecated; use --profile instead")
        resolved = _profile_id_for_city(args.city)
        if resolved is None:
            raise SystemExit(f"No profile found targeting city '{args.city}'")
        profile_id = resolved
    elif args.city is not None and profile_id is not None:
        pass  # profile takes precedence — ignore city

    console.print("[bold cyan]🔍 Starting WG scan…[/bold cyan]")
    run = run_scan(profile_id=profile_id)

    console.print(f"[green]✅ Run complete:[/green] {run['run_id']}")
    console.print(f"   Sources scanned : {run['sources_scanned']}")
    console.print(f"   Results scanned : {run['results_scanned']}")
    console.print(f"   New listings    : {run['new_results']}")
    console.print(f"   Updated         : {run['updated_results']}")
    console.print(f"   Stale removed   : {run['stale_removed']}")
    console.print(f"   Duration        : {run['duration_seconds']}s")
    url = run.get("report_url")
    if url and not str(url).startswith("ERROR"):
        console.print(f"   [bold green]🌐 Report URL    : {url}[/bold green]")
    elif url:
        console.print(f"   [yellow]⚠️  Upload error  : {url}[/yellow]")
    if run.get("errors"):
        console.print("[yellow]⚠️  Errors:[/yellow]")
        for err in run["errors"]:
            console.print(f"   - {err}")


def cmd_status(args: argparse.Namespace) -> None:
    """Print a project summary."""
    from shaked_wg_agent.config import load_config
    from shaked_wg_agent.persistence import last_run, load_listings

    cfg = load_config(args.profile)
    listings = load_listings()
    last = last_run()

    console.rule("[bold]Shaked WG Basel — Status[/bold]")
    console.print(f"  Profile   : [cyan]{cfg.profile.profile_name}[/cyan]")
    console.print(
        f"  Budget    : {cfg.city.currency} {cfg.profile.budget_min}–{cfg.profile.budget_max}"
    )
    console.print(f"  Move-in   : {cfg.profile.move_in_from}")
    console.print(f"  Diet      : {cfg.profile.diet}")
    console.print(f"  Transit lines: {', '.join(cfg.profile.transit_lines)}")
    console.print()
    console.print(f"  Listings  : {len(listings)} total")

    if listings:
        top = max(listings, key=lambda x: x.get("relevance_score", 0))
        console.print(
            f"  Top pick  : [green]{top.get('title', '?')[:60]}[/green] "
            f"(score {top.get('relevance_score', 0)})"
        )

    if last:
        console.print(
            f"  Last run  : {last['run_timestamp']} — "
            f"{last['new_results']} new, {last['results_scanned']} scanned"
        )
    else:
        console.print("  Last run  : [yellow]none yet[/yellow]")

    now = datetime.now(UTC).date().isoformat()
    end = cfg.agent.project_end
    if end:
        try:
            from datetime import date

            days_left = (date.fromisoformat(end) - date.fromisoformat(now)).days
            color = "red" if days_left < 10 else "yellow" if days_left < 21 else "green"
            console.print(f"  Deadline  : [{color}]{days_left} days left (ends {end})[/{color}]")
        except ValueError:
            pass


def cmd_list() -> None:
    """Print listings table sorted by relevance score."""
    from rich.table import Table

    from shaked_wg_agent.config import load_config
    from shaked_wg_agent.locale import get_locale
    from shaked_wg_agent.persistence import load_listings

    try:
        cfg = load_config(None)
        locale = get_locale(cfg.city.country)
    except Exception:
        locale = get_locale("CH")
    listings = load_listings()
    if not listings:
        console.print("[yellow]No listings found. Run `python -m shaked_wg_agent run` first.[/yellow]")
        return

    sorted_listings = sorted(listings, key=lambda x: x.get("relevance_score", 0), reverse=True)

    table = Table(title="WG Listings — Basel", show_lines=True)
    table.add_column("Score", style="bold", width=6, justify="right")
    table.add_column("Status", width=12)
    table.add_column("Price", width=8)
    table.add_column("District", width=14)
    table.add_column("Transit", width=8)
    table.add_column("Vegan", width=18)
    table.add_column("Title", min_width=30, no_wrap=False)

    status_colors = {
        "favorit": "green",
        "interessant": "cyan",
        "kontaktiert": "blue",
        "neu": "white",
        "abgesagt": "red",
    }

    for lst in sorted_listings:
        score = lst.get("relevance_score", 0)
        status = lst.get("status", "")
        color = status_colors.get(status, "white")
        status_label = locale.status_labels.get(status, status)
        price_val = lst.get("price")
        if price_val is None:
            price_val = lst.get("price_chf")
        currency = lst.get("currency", "CHF")
        price = f"{currency} {price_val}" if price_val else "?"
        lines = lst.get("transit_match_lines") or lst.get("tram_match_lines") or []
        tram = ", ".join(lines)
        vegan = lst.get("vegan_signal", "")[:17]
        table.add_row(
            str(score),
            f"[{color}]{status_label}[/{color}]",
            price,
            lst.get("district", "")[:13],
            tram,
            vegan,
            lst.get("title", "")[:60],
        )

    console.print(table)
    console.print(f"\n[dim]{len(listings)} listings total[/dim]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Shaked WG Basel search agent",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="trigger full scan across all enabled sources")
    p_run.add_argument("--profile", type=str, default=None, help="Profile ID (default: from agent.json)")
    p_run.add_argument("--city", type=str, default=None, help=argparse.SUPPRESS)
    p_run.set_defaults(func=cmd_run)

    p_status = sub.add_parser("status", help="show project summary")
    p_status.add_argument("--profile", type=str, default=None, help="Profile ID (default: from agent.json)")
    p_status.set_defaults(func=cmd_status)

    p_list = sub.add_parser("list", help="show all listings sorted by relevance score")

    def _cmd_list(_a: argparse.Namespace) -> None:
        cmd_list()

    p_list.set_defaults(func=_cmd_list)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
