#!/usr/bin/env python3
"""
RetardMaxxing / LooksMaxxing Tracker
Experimental personal protocol tracker — CLI edition
"""
import argparse
from datetime import date

from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.table import Table
from rich import box
from rich.panel import Panel
from rich.text import Text

import db
import stats as st

console = Console()

BANNER = """[bold magenta]
 ██████╗ ███████╗████████╗ █████╗ ██████╗ ██████╗
 ██╔══██╗██╔════╝╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗
 ██████╔╝█████╗     ██║   ███████║██████╔╝██║  ██║
 ██╔══██╗██╔══╝     ██║   ██╔══██║██╔══██╗██║  ██║
 ██║  ██║███████╗   ██║   ██║  ██║██║  ██║██████╔╝
 ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
[/bold magenta][dim]          M A X X I N G   T R A C K E R[/dim]"""

CATEGORIES = ["peptide", "physical", "mental", "skincare", "other"]


def cmd_log(args):
    db.init_db()
    today = date.today().isoformat()
    routines = db.get_routines()

    console.print(Panel(BANNER, border_style="magenta", padding=(0, 2)))
    console.print(f"\n[bold]Logging entry for [cyan]{today}[/cyan][/bold]\n")

    looks = IntPrompt.ask(
        "[green]Looks score[/green] (1-10)", default=5
    )
    looks = max(1, min(10, looks))

    retard = IntPrompt.ask(
        "[cyan]Retard score[/cyan] (1-10)", default=5
    )
    retard = max(1, min(10, retard))

    notes = Prompt.ask("[dim]Notes (optional)[/dim]", default="")

    done_ids = []
    if routines:
        console.print("\n[bold]Routines — mark completed:[/bold]")
        for r in routines:
            cat_color = {
                "peptide": "blue",
                "physical": "green",
                "mental": "yellow",
                "skincare": "magenta",
                "other": "white",
            }.get(r["category"], "white")
            label = f"[{cat_color}][{r['category']}][/{cat_color}] {r['name']}"
            if Confirm.ask(f"  {label}?", default=False):
                done_ids.append(r["id"])

    db.save_log(today, looks, retard, notes, done_ids)
    console.print(f"\n[bold green]✓ Saved![/bold green] looks={looks} retard={retard}")


def cmd_stats(args):
    db.init_db()
    days = getattr(args, "days", 30)
    st.show_stats(days)


def cmd_history(args):
    db.init_db()
    days = getattr(args, "days", 30)
    st.show_history(days)


def cmd_routine(args):
    db.init_db()
    if args.routine_cmd == "add":
        name = args.name
        category = args.category.lower()
        if category not in CATEGORIES:
            console.print(
                f"[red]Category must be one of: {', '.join(CATEGORIES)}[/red]"
            )
            return
        ok = db.add_routine(name, category)
        if ok:
            console.print(f"[green]Added routine:[/green] [bold]{name}[/bold] [{category}]")
        else:
            console.print(f"[yellow]Routine '{name}' already exists.[/yellow]")

    elif args.routine_cmd == "list":
        routines = db.get_routines(active_only=False)
        if not routines:
            console.print("[yellow]No routines yet. Use: python main.py routine add <name> <category>[/yellow]")
            return
        table = Table(title="Routines", box=box.SIMPLE_HEAVY)
        table.add_column("ID", style="dim", width=4)
        table.add_column("Name", style="bold")
        table.add_column("Category")
        table.add_column("Active", justify="center")
        cat_colors = {
            "peptide": "blue", "physical": "green",
            "mental": "yellow", "skincare": "magenta", "other": "white"
        }
        for r in routines:
            color = cat_colors.get(r["category"], "white")
            cat_text = Text(r["category"], style=color)
            active_text = Text("✓", style="green") if r["active"] else Text("✗", style="red")
            table.add_row(str(r["id"]), r["name"], cat_text, active_text)
        console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description="RetardMaxxing / LooksMaxxing Tracker",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
commands:
  log                   Log today's entry (interactive)
  stats [--days N]      Show ASCII progress charts
  history [--days N]    Show history table
  routine add NAME CAT  Add a routine (categories: peptide/physical/mental/skincare/other)
  routine list          List all routines
        """
    )
    subparsers = parser.add_subparsers(dest="command")

    # log
    subparsers.add_parser("log", help="Log today's entry")

    # stats
    p_stats = subparsers.add_parser("stats", help="Show progress charts")
    p_stats.add_argument("--days", type=int, default=30, help="Number of days to show")

    # history
    p_hist = subparsers.add_parser("history", help="Show history table")
    p_hist.add_argument("--days", type=int, default=30, help="Number of days to show")

    # routine
    p_routine = subparsers.add_parser("routine", help="Manage routines")
    routine_sub = p_routine.add_subparsers(dest="routine_cmd")
    p_add = routine_sub.add_parser("add", help="Add a routine")
    p_add.add_argument("name", help="Routine name")
    p_add.add_argument("category", help="Category: peptide/physical/mental/skincare/other")
    routine_sub.add_parser("list", help="List routines")

    args = parser.parse_args()

    if args.command == "log":
        cmd_log(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "history":
        cmd_history(args)
    elif args.command == "routine":
        if not args.routine_cmd:
            p_routine.print_help()
        else:
            cmd_routine(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
