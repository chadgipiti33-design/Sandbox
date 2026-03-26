from rich.console import Console
from rich.table import Table
from rich import box
from rich.text import Text
import plotext as plt

from db import get_logs, get_log_routines

console = Console()


def _score_color(score: int) -> str:
    if score >= 8:
        return "bright_green"
    if score >= 5:
        return "yellow"
    return "red"


def show_stats(days: int = 30):
    logs = get_logs(days)
    if not logs:
        console.print("[yellow]No data yet. Run [bold]python main.py log[/bold] first.[/yellow]")
        return

    logs_sorted = sorted(logs, key=lambda x: x["date"])
    dates = [l["date"][5:] for l in logs_sorted]  # MM-DD
    looks = [l["looks_score"] for l in logs_sorted]
    retard = [l["retard_score"] for l in logs_sorted]

    plt.clf()
    plt.plot_size(70, 20)
    plt.theme("dark")
    plt.title(f"Progress — last {len(logs)} days")
    plt.plot(looks, label="Looks Score", color="green+")
    plt.plot(retard, label="Retard Score", color="cyan+")
    plt.ylim(0, 10)
    plt.xticks(list(range(len(dates))), dates)
    plt.show()

    console.print()
    avg_looks = sum(looks) / len(looks)
    avg_retard = sum(retard) / len(retard)
    console.print(
        f"  [bold]Avg Looks:[/bold] [{_score_color(round(avg_looks))}]{avg_looks:.1f}[/]  "
        f"[bold]Avg Retard:[/bold] [{_score_color(round(avg_retard))}]{avg_retard:.1f}[/]"
    )


def show_history(days: int = 30):
    logs = get_logs(days)
    if not logs:
        console.print("[yellow]No entries yet.[/yellow]")
        return

    table = Table(
        title=f"Last {len(logs)} entries",
        box=box.SIMPLE_HEAVY,
        show_lines=True,
    )
    table.add_column("Date", style="bold cyan", width=12)
    table.add_column("Looks", justify="center", width=7)
    table.add_column("Retard", justify="center", width=8)
    table.add_column("Routines", width=30)
    table.add_column("Notes", width=30)

    for log in logs:
        routines = get_log_routines(log["id"])
        done_names = [r["name"] for r in routines if r["done"]]
        routine_str = ", ".join(done_names) if done_names else "-"

        looks_txt = Text(str(log["looks_score"]), style=_score_color(log["looks_score"]))
        retard_txt = Text(str(log["retard_score"]), style=_score_color(log["retard_score"]))

        table.add_row(
            log["date"],
            looks_txt,
            retard_txt,
            routine_str,
            log["notes"] or "-",
        )

    console.print(table)
