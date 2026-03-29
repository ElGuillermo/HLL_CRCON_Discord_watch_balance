"""
watch_balance.py

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that watches the teams players levels.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import logging
from time import sleep
from datetime import datetime, timezone
import os
import pathlib
from typing import Tuple
import discord
from sqlalchemy import create_engine
from rcon.rcon import Rcon
from rcon.settings import SERVER_INFO
from rcon.utils import get_server_number
import custom_tools.common_functions as common_functions
from custom_tools.common_translations import TRANSL
import custom_tools.watch_balance_config as config


def team_avg(
    all_players: list,
    observed_team: str,
    observed_parameter: str,
    total_count: int
) -> float:
    """
    Divide the sum of "observed_parameter" values from all the players in "team" by "total_count"
    ie :
    t1_lvl_avg: float = team_avg(all_players, "allies", "level", t1_count)
    """
    if total_count == 0:
        return 0
    return_value = sum(
        player[observed_parameter] for player in all_players if player["team"] == observed_team
    ) / total_count
    if return_value == 0:
        return 0
    return return_value


def level_cursor(
    t1_lvl_avg: float,
    t2_lvl_avg: float,
    slots_tot: int = 44  # Prefer a pair value, or the 'middle pin' won't be in middle
) -> str:
    """
    Returns a full gauge :
    ie (slots_tot = 40) : "`100 50% [--------------------|--------------------] 100 50%`"
    ie (slots_tot = 40) : "`200 67% [-------------------->>>>>>>|-------------] 100 33%`"
    ie (slots_tot = 40) : "` 50 25% [----------|<<<<<<<<<<--------------------] 150 75%`"
    """
    t1_avg_pct: float = (t1_lvl_avg / (t1_lvl_avg + t2_lvl_avg)) * 100
    t1_avg_pct_slots: int = round(t1_avg_pct / (100 / slots_tot))
    t2_avg_pct_slots: int = slots_tot - t1_avg_pct_slots

    if t1_avg_pct_slots > round(slots_tot / 2):
        t1_below50pct_str: str = "-" * round(slots_tot / 2)
        t1_over50pct_str: str = ">" * (t1_avg_pct_slots - round(slots_tot / 2))
        t2_below50pct_str: str = "-" * t2_avg_pct_slots
        t2_over50pct_str: str = ""
    else:
        t1_below50pct_str: str = "-" * t1_avg_pct_slots
        t1_over50pct_str: str = ""
        t2_below50pct_str: str = "-" * round(slots_tot / 2)
        t2_over50pct_str: str = "<" * (t2_avg_pct_slots - round(slots_tot / 2))

    return(
        f"`{round(t1_lvl_avg):>3} {round(t1_avg_pct):>2}%"
        f" [{t1_below50pct_str}{t1_over50pct_str}|{t2_over50pct_str}{t2_below50pct_str}] "
        f"{round(t2_lvl_avg):>3} {round(100 - t1_avg_pct):>2}%`"
    )


def level_pop_distribution(
    all_players: list,
    t1_count: int,
    t2_count: int,
    slots_tot: int = 36  # Prefer a pair value, or the 'middle pin' won't be in middle
) -> str:
    """
    returns a multilines (5) string representing a graph of level tiers
    """
    t1_l1_count: int = sum(1 for player in all_players if player["team"] == "allies" and 1 <= player["level"] < 30)
    t1_l2_count: int = sum(1 for player in all_players if player["team"] == "allies" and 30 <= player["level"] < 60)
    t1_l3_count: int = sum(1 for player in all_players if player["team"] == "allies" and 60 <= player["level"] < 125)
    t1_l4_count: int = sum(1 for player in all_players if player["team"] == "allies" and 125 <= player["level"] < 250)
    t1_l5_count: int = sum(1 for player in all_players if player["team"] == "allies" and 250 <= player["level"] <= 500)

    t1_l1_slots: int = round((t1_l1_count * slots_tot) / (2 * t1_count))
    t1_l2_slots: int = round((t1_l2_count * slots_tot) / (2 * t1_count))
    t1_l3_slots: int = round((t1_l3_count * slots_tot) / (2 * t1_count))
    t1_l4_slots: int = round((t1_l4_count * slots_tot) / (2 * t1_count))
    t1_l5_slots: int = round((t1_l5_count * slots_tot) / (2 * t1_count))

    t2_l1_count: int = sum(1 for player in all_players if player["team"] == "axis" and 1 <= player["level"] < 30)
    t2_l2_count: int = sum(1 for player in all_players if player["team"] == "axis" and 30 <= player["level"] < 60)
    t2_l3_count: int = sum(1 for player in all_players if player["team"] == "axis" and 60 <= player["level"] < 125)
    t2_l4_count: int = sum(1 for player in all_players if player["team"] == "axis" and 125 <= player["level"] < 250)
    t2_l5_count: int = sum(1 for player in all_players if player["team"] == "axis" and 250 <= player["level"] <= 500)

    t2_l1_slots: int = round((t2_l1_count * slots_tot) / (2 * t2_count))
    t2_l2_slots: int = round((t2_l2_count * slots_tot) / (2 * t2_count))
    t2_l3_slots: int = round((t2_l3_count * slots_tot) / (2 * t2_count))
    t2_l4_slots: int = round((t2_l4_count * slots_tot) / (2 * t2_count))
    t2_l5_slots: int = round((t2_l5_count * slots_tot) / (2 * t2_count))

    return_str = (
        # level 5
        f"`250-500: {t1_l5_count:>2} {round((t1_l5_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l5_slots) * ' '}{t1_l5_slots * '■'}"
        f"|{t2_l5_slots * '■'}{round((slots_tot / 2) - t2_l5_slots) * ' '}]"
        f" {t2_l5_count:>2} {round((t2_l5_count * 100) / t2_count):>3}%`\n"
        # level 4
        f"`125-249: {t1_l4_count:>2} {round((t1_l4_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l4_slots) * ' '}{t1_l4_slots * '■'}"
        f"|{t2_l4_slots * '■'}{round((slots_tot / 2) - t2_l4_slots) * ' '}]"
        f" {t2_l4_count:>2} {round((t2_l4_count * 100) / t2_count):>3}%`\n"
        # level 3
        f"` 60-124: {t1_l3_count:>2} {round((t1_l3_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l3_slots) * ' '}{t1_l3_slots * '■'}"
        f"|{t2_l3_slots * '■'}{round((slots_tot / 2) - t2_l3_slots) * ' '}]"
        f" {t2_l3_count:>2} {round((t2_l3_count * 100) / t2_count):>3}%`\n"
        # level 2
        f"` 30- 59: {t1_l2_count:>2} {round((t1_l2_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l2_slots) * ' '}{t1_l2_slots * '■'}"
        f"|{t2_l2_slots * '■'}{round((slots_tot / 2) - t2_l2_slots) * ' '}]"
        f" {t2_l2_count:>2} {round((t2_l2_count * 100) / t2_count):>3}%`\n"
        # level 1
        f"`  1- 29: {t1_l1_count:>2} {round((t1_l1_count * 100) / t1_count):>3}%"
        f" [{round((slots_tot / 2) - t1_l1_slots) * ' '}{t1_l1_slots * '■'}"
        f"|{t2_l1_slots * '■'}{round((slots_tot / 2) - t2_l1_slots) * ' '}]"
        f" {t2_l1_count:>2} {round((t2_l1_count * 100) / t2_count):>3}%`"
    )

    return return_str


def role_avg(
    all_players: list[dict],
    roles: set[str] | list[str]
) -> tuple[int, float, int, float, float]:
    """
    Calculates counts, average levels per team, and the difference ratio.
    """
    stats = {
        "allies": {"level": 0, "count": 0},
        "axis": {"level": 0, "count": 0}
    }

    for player in all_players:
        team = player.get("team")
        if player.get("role") in roles and team in stats:
            stats[team]["level"] += player.get("level", 0)
            stats[team]["count"] += 1

    # Moyennes (arrondies à 1 décimale)
    t1_count = stats["allies"]["count"]
    t2_count = stats["axis"]["count"]

    t1_avg = round(stats["allies"]["level"] / t1_count, 1) if t1_count > 0 else 0.0
    t2_avg = round(stats["axis"]["level"] / t2_count, 1) if t2_count > 0 else 0.0

    # Ratio (arrondi à 2 décimales)
    low_val = min(t1_avg, t2_avg)
    if low_val > 0:
        ratio = round(max(t1_avg, t2_avg) / low_val, 2)
    else:
        ratio = 1.0

    return (t1_count, t1_avg, t2_count, t2_avg, ratio)


def watch_balance_loop(engine) -> None:
    """
    Calls the function that gathers data,
    then calls the function to analyze it.
    """
    rcon = Rcon(SERVER_INFO)

    try:
        (
            all_teams,
            all_players,
            _,  # all_commanders
            _,  # all_infantry_players
            _,  # all_armor_players
            _,  # all_artillery_players
            _,  # all_recon_players
            _,  # all_infantry_squads
            _,  # all_armor_squads
            _,  # all_artillery_squads
            _   # all_recon_squads
        ) = common_functions.team_view_stats(rcon)
    except Exception:
        return

    if len(all_teams) < 2:
        logger.info(
            "Less than 2 teams ingame. Waiting for %s mins...",
            round((config.WATCH_INTERVAL_SECS / 60), 1)
        )
        return

    watch_balance(
        all_teams,
        all_players,
        engine
    )


def watch_balance(
    all_teams: list,
    all_players: list,
    engine
) -> None:
    """
    Gets the data from common_functions.team_view_stats(),
    process it, then display it in a Discord embed
    """
    # Check if enabled on this server and get webhook url
    try:
        server_number = int(get_server_number())
        server_config = config.SERVER_CONFIG[server_number - 1]

        if not server_config[1]:
            return

        discord_webhook = server_config[0]

    except (ValueError, TypeError, IndexError):
        logger.error("Could not retrieve server configuration.")
        return

    # Get teams data
    t1_stats = next((t["allies"] for t in all_teams if "allies" in t), {})
    t2_stats = next((t["axis"] for t in all_teams if "axis" in t), {})

    if not t1_stats or not t2_stats:
        return

    t1_count = t1_stats.get("count", 0)
    t2_count = t2_stats.get("count", 0)

    t1_lvl_avg = team_avg(all_players, "allies", "level", t1_count)
    t2_lvl_avg = team_avg(all_players, "axis", "level", t2_count)

    if t1_lvl_avg == 0 or t2_lvl_avg == 0:
        logger.info(
            "Either Allies or Axis average level is 0. Waiting for %s mins...",
            round((config.WATCH_INTERVAL_SECS / 60), 2)
        )
        return

    # Global ratio
    avg_diff_ratio = max(t1_lvl_avg, t2_lvl_avg) / min(t1_lvl_avg, t2_lvl_avg)
    lang = config.LANG
    embed_title = f"{TRANSL['all_players'][lang]} - {TRANSL['level'][lang]} ({TRANSL['ratio'][lang]}) : {round(avg_diff_ratio, 2)}"

    results = {}
    for key, roles in config.CATEGORIES.items():
        t1_c, t1_a, t2_c, t2_a, ratio = role_avg(all_players, roles)
        if t1_c > 0 and t2_c > 0:
            avg_total = round((t1_a + t2_a) / 2)
            results[key] = {
                "title": f"{TRANSL[key][lang]} - {TRANSL['level'][lang]} ({TRANSL['avg'][lang]}) : {avg_total}",
                "graph": level_cursor(t1_a, t2_a)
            }

    # Raw stats
    fields = [
        ("kills", t1_stats.get("kills", 0), t2_stats.get("kills", 0)),
        ("deaths", t1_stats.get("deaths", 0), t2_stats.get("deaths", 0)),
        ("combat", t1_stats.get("combat", 0), t2_stats.get("combat", 0)),
        ("offense", t1_stats.get("offense", 0), t2_stats.get("offense", 0)),
        ("defense", t1_stats.get("defense", 0), t2_stats.get("defense", 0)),
        ("support", t1_stats.get("support", 0), t2_stats.get("support", 0)),
    ]

    col1_text = f"{TRANSL['players'][lang]}\n\n"
    col2_text = f"{t1_count}\n\n"
    col3_text = f"{t2_count}\n\n"

    for stat_key, v1, v2 in fields:
        s1, s2 = common_functions.bold_the_highest(v1, v2)
        a1 = round(team_avg(all_players, 'allies', stat_key, t1_count))
        a2 = round(team_avg(all_players, 'axis', stat_key, t2_count))

        col1_text += f"{TRANSL[stat_key][lang]} ({TRANSL['tot'][lang]}/{TRANSL['avg'][lang]})\n"
        col2_text += f"{s1} / {a1}\n"
        col3_text += f"{s2} / {a2}\n"

    # Discord embed
    webhook = discord.SyncWebhook.from_url(discord_webhook)
    embed = discord.Embed(
        title=embed_title,
        color=int(common_functions.green_to_red(value=avg_diff_ratio, min_value=1), base=16),
        url=common_functions.DISCORD_EMBED_AUTHOR_URL
    )
    embed.set_author(name=config.BOT_NAME, icon_url=common_functions.DISCORD_EMBED_AUTHOR_ICON_URL)

    # Distribution and global avg
    embed.add_field(name=f"{TRANSL['all_players'][lang]} - {TRANSL['distribution'][lang]}",
                    value=level_pop_distribution(all_players, t1_count, t2_count), inline=False)
    all_avg = round((t1_lvl_avg + t2_lvl_avg) / 2)
    embed.add_field(name=f"{TRANSL['all_players'][lang]} - {TRANSL['level'][lang]} ({TRANSL['avg'][lang]}) : {all_avg}",
                    value=level_cursor(t1_lvl_avg, t2_lvl_avg), inline=False)

    # Per role
    for key in config.CATEGORIES:
        if key in results:
            embed.add_field(name=results[key]["title"], value=results[key]["graph"], inline=False)

    # Raw stats
    embed.add_field(name=TRANSL['stats'][lang], value=col1_text, inline=True)
    embed.add_field(name=TRANSL['allies'][lang], value=col2_text, inline=True)
    embed.add_field(name=TRANSL['axis'][lang], value=col3_text, inline=True)

    embed.set_footer(text="Updated: ")
    embed.set_timestamp(datetime.now(tz=timezone.utc))

    common_functions.discord_embed_send(embed, webhook, engine)


# Launching - initial pause : wait to be sure the CRCON is fully started
sleep(60)

logger = logging.getLogger('rcon')

logger.info(
    "\n-------------------------------------------------------------------------------\n"
    "%s (started)\n"
    "-------------------------------------------------------------------------------",
    config.BOT_NAME
)

# Launching and running (infinite loop)
if __name__ == "__main__":
    root_path = os.getenv("BALANCE_WATCH_DATA_PATH", "/data")
    full_path = pathlib.Path(root_path) / pathlib.Path("watch_balance.db")
    engine = create_engine(f"sqlite:///file:{full_path}?mode=rwc&uri=true", echo=False)
    common_functions.Base.metadata.create_all(engine)
    while True:
        watch_balance_loop(engine)
        sleep(config.WATCH_INTERVAL_SECS)
