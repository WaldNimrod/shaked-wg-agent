"""CLI entry point: python -m shaked_wg_agent [run|status|list]"""
from __future__ import annotations

import sys
from datetime import UTC, datetime

from rich.console import Console
from rich.table import Table

console = Console()


def cmd_run() -> None:
    """Trigger a full scan across all enabled sources."""
    from shaked_wg_agent.runner import run_scan

    console.print("[bold cyan]🔍 Starting WG scan…[/bold cyan]")
    run = run_scan()

    console.print(f"[green]✅ Run complete:[/green] {run['run_id']}")
    console.print(f"   Sources scanned : {run['sources_scanned']}")
    console.print(f"   Results scanned : {run['results_scanned']}")
    console.print(f"   New listings    : {run['new_results']}")
    console.print(f"   Updated         : {run['updated_results']}")
    console.print(f"   Stale removed   : {run['stale_removed']}")
    console.print(f"   Duration        : {run['duration_seconds']}s")
    if run.get("errors"):
        console.print("[yellow]⚠️  Errors:[/yellow]")
        for err in run["errors"]:
            console.print(f"   - {err}")


def cmd_status() -> None:
    """Print a project summary."""
    from shaked_wg_agent.config import load_config
    from shaked_wg_agent.persistence import last_run, load_listings

    cfg = load_config()
    listings = load_listings()
    last = last_run()

    console.rule("[bold]Shaked WG Basel — Status[/bold]")
    console.print(f"  Profile   : [cyan]{cfg.agent.profile_name}[/cyan]")
    console.print(f"  Budget    : CHF {cfg.agent.budget_min_chf}–{cfg.agent.budget_max_chf}")
    console.print(f"  Move-in   : {cfg.agent.move_in_from}")
    console.print(f"  Diet      : {cfg.agent.diet}")
    console.print(f"  Tram lines: {', '.join(cfg.agent.tram_lines)}")
    console.print()
    console.print(f"  Listings  : {len(listings)} total")

    if listings:
        top = max(listings, key=lambda x: x.get("relevance_score", 0))
        console.print(
            f"  Top pick  : [green]{top.get('title', '?')[:60]}[/green] "
            f"(score {top.get('relevance_score', 0)})"
        )

    if last:
        console.print(f"  Last run  : {last['run_timestamp']} — "
                      f"{last['new_results']} new, {last['results_scanned']} scanned")
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
    from shaked_wg_agent.persistence import load_listings

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
    table.add_column("Tram", width=8)
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
        price = f"CHF {lst['price_chf']}" if lst.get("price_chf") else "?"
        tram = ", ".join(lst.get("tram_match_lines", []))
        vegan = lst.get("vegan_signal", "")[:17]
        table.add_row(
            str(score),
            f"[{color}]{status}[/{color}]",
            price,
            lst.get("district", "")[:13],
            tram,
            vegan,
            lst.get("title", "")[:60],
        )

    console.print(table)
    console.print(f"\n[dim]{len(listings)} listings total[/dim]")


def main() -> None:
    commands = {"run": cmd_run, "status": cmd_status, "list": cmd_list}
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        console.print("[bold]Usage:[/bold] python -m shaked_wg_agent [run|status|list]")
        console.print()
        console.print("  [cyan]run[/cyan]     — trigger full scan across all enabled sources")
        console.print("  [cyan]status[/cyan]  — show project summary and last run info")
        console.print("  [cyan]list[/cyan]    — show all listings sorted by relevance score")
        sys.exit(1)
    commands[sys.argv[1]]()


if __name__ == "__main__":
    main()
