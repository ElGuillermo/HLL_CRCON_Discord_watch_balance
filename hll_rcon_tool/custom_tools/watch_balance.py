"""
watch_balance.py

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that watches the teams players levels.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import logging
from time import sleep
import datetime
import os
import pathlib
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
    slots_tot: int = 36
) -> str:
    """
    Returns a full gauge representing the balance between two average levels.
    ie (slots_tot = 40) : "`100 50% [--------------------|--------------------] 50% 100`"
    ie (slots_tot = 40) : "`200 67% [-------------------->>>>>>>|-------------] 33% 100`"
    ie (slots_tot = 40) : "` 50 25% [----------|<<<<<<<<<<--------------------] 75% 150`"
    """
    total_lvl = t1_lvl_avg + t2_lvl_avg
    mid = slots_tot // 2

    if total_lvl > 0:
        t1_pct = (t1_lvl_avg / total_lvl) * 100
        t2_pct = 100 - t1_pct
        pos = round((t1_pct * slots_tot) / 100)
    else:
        t1_pct, t2_pct = 0.0, 0.0
        pos = mid

    pos = max(0, min(pos, slots_tot - 1))
    gauge = list("-" * slots_tot)
    if pos > mid:
        for i in range(mid, pos):
            gauge[i] = ">"
    elif pos < mid:
        for i in range(pos + 1, mid + 1):
            gauge[i] = "<"

    gauge[pos] = "|"
    gauge_str = "".join(gauge)

    if t1_lvl_avg > 0 and t2_lvl_avg > 0:
        avg_val = str(round((t1_lvl_avg + t2_lvl_avg) / 2))
    else:
        avg_val = "N/A"

    return (
        f"`avg: {avg_val:>3} "
        f"{round(t1_lvl_avg):>4} {round(t1_pct):>3}%"
        f"[{gauge_str}]"
        f"{round(t2_pct):>3}% {round(t2_lvl_avg):>3}`"
    )


def level_pop_distribution(
    all_players: list,
    slots_tot: int = 36
) -> str:
    """
    Returns a multilines (5) string representing a graph of level tiers.
    """
    tiers = [
        (250, 500, "250-500"),
        (125, 249, "125-249"),
        (60, 124, " 60-124"),
        (30, 59,  " 30- 59"),
        (1, 29,   "  1- 29")
    ]

    counts = { (t[0], t[1]): [0, 0] for t in tiers }
    real_t1_total = 0
    real_t2_total = 0

    for p in all_players:
        if p.get("unit_name") == "unassigned":
            continue
        lvl, team = p.get("level", 0), p.get("team")
        if team == "allies": real_t1_total += 1
        elif team == "axis": real_t2_total += 1

        for low, high in counts:
            if low <= lvl <= high:
                if team == "allies": counts[(low, high)][0] += 1
                elif team == "axis": counts[(low, high)][1] += 1
                break

    half_slots = slots_tot // 2
    formatted_lines = []

    for low, high, label in tiers:
        c1, c2 = counts[(low, high)]

        p1 = round((c1 * 100) / real_t1_total) if real_t1_total > 0 else 0
        s1 = round((c1 * half_slots) / real_t1_total) if real_t1_total > 0 else 0

        p2 = round((c2 * 100) / real_t2_total) if real_t2_total > 0 else 0
        s2 = round((c2 * half_slots) / real_t2_total) if real_t2_total > 0 else 0

        s1, s2 = min(s1, half_slots), min(s2, half_slots)

        bar_left = f"{(half_slots - s1) * ' '}{s1 * '■'}"
        bar_right = f"{s2 * '■'}{(half_slots - s2) * ' '}"

        formatted_lines.append(
            f"`{label}: {c1:>2} {p1:>3}% [{bar_left}|{bar_right}] {p2:>3}% {c2:>2}`"
        )

    return (
        f"{formatted_lines[0]}\n"
        f"{formatted_lines[1]}\n"
        f"{formatted_lines[2]}\n"
        f"{formatted_lines[3]}\n"
        f"{formatted_lines[4]}"
    )


def role_avg(
    all_players: list[dict],
    roles: set[str] | list[str]
) -> tuple[int, float, int, float, float|str]:
    """
    Calculates counts, average levels and the difference ratio per team/role(s)
    """
    t1_lvl, t1_count = 0, 0
    t2_lvl, t2_count = 0, 0

    for p in all_players:
        if p.get("unit_name") == "unassigned":
            continue
        if p.get("role") in roles:
            team = p.get("team")
            if team == "allies":
                t1_lvl += p.get("level", 0)
                t1_count += 1
            elif team == "axis":
                t2_lvl += p.get("level", 0)
                t2_count += 1

    t1_avg = round(t1_lvl / t1_count, 1) if t1_count > 0 else 0.0
    t2_avg = round(t2_lvl / t2_count, 1) if t2_count > 0 else 0.0

    if t1_avg > 0 and t2_avg > 0:
        ratio = round(max(t1_avg, t2_avg) / min(t1_avg, t2_avg), 2)
    else:
        ratio = TRANSL['na'][config.LANG]

    return (t1_count, t1_avg, t2_count, t2_avg, ratio)


def units_squad_players_stats(data):
    """
    Extracts squads and players number by type (infantry, armor, etc) for each team
    """
    if "result" in data:
        results = data["result"]
    else:
        results = data

    stats = {
        "allies": {"players": {}, "units": {}},
        "axis": {"players": {}, "units": {}}
    }

    unit_types = ["infantry", "armor", "artillery", "recon"]

    for side in ["allies", "axis"]:
        team_data = results.get(side, {})

        stats[side]["players"] = {t: 0 for t in unit_types + ["armycommander"]}
        stats[side]["units"] = {t: 0 for t in unit_types}

        # Commander
        if team_data.get("commander") is not None:
            stats[side]["players"]["armycommander"] = 1

        # Squads
        squads = team_data.get("squads", {})
        if isinstance(squads, dict):
            for squad_info in squads.values():
                s_type = squad_info.get("type")

                if s_type in unit_types:
                    stats[side]["units"][s_type] += 1
                    player_count = len(squad_info.get("players", []))
                    stats[side]["players"][s_type] += player_count

    return stats


def watch_balance(
    rcon: Rcon,
    all_teams: list,
    all_players: list,
    engine
) -> None:
    """
    Gets the data from common_functions.team_view_stats(),
    process it, then display it in a Discord embed
    """
    # Check if enabled on this server
    try:
        server_number = int(get_server_number())
        server_config = config.SERVER_CONFIG[server_number - 1]

        if not server_config[1]:
            return

        discord_webhook = server_config[0]

    except (ValueError, TypeError, IndexError):
        logger.error("Could not retrieve server configuration.")
        return

    # All players
    # -------------------------------------------------------------------------
    t1_count = sum(1 for p in all_players if p.get("team") == "allies" and p.get("unit_name") != "unassigned")
    t2_count = sum(1 for p in all_players if p.get("team") == "axis" and p.get("unit_name") != "unassigned")

    t1_stats = next((t["allies"] for t in all_teams if "allies" in t), {})
    t2_stats = next((t["axis"] for t in all_teams if "axis" in t), {})

    t1_lvl_avg = team_avg(all_players, "allies", "level", t1_count)
    t2_lvl_avg = team_avg(all_players, "axis", "level", t2_count)

    if t1_lvl_avg > 0 and t2_lvl_avg > 0:
        avg_diff_ratio = round(max(t1_lvl_avg, t2_lvl_avg) / min(t1_lvl_avg, t2_lvl_avg), 2)
    else:
        avg_diff_ratio = TRANSL['na'][config.LANG]

    embed_title = f"{TRANSL['all_players'][config.LANG]} - {TRANSL['level'][config.LANG]} ({TRANSL['ratio'][config.LANG]}) : {avg_diff_ratio}"

    # Players/squads per unit type
    # -------------------------------------------------------------------------
    get_team_view_data = rcon.get_team_view()
    squad_and_player_stats = units_squad_players_stats(get_team_view_data)

    units_col1_text = f"{TRANSL['armycommander'][config.LANG]}\n"
    units_col2_text = f"{squad_and_player_stats['allies']['players']['armycommander']}\n"
    units_col3_text = f"{squad_and_player_stats['axis']['players']['armycommander']}\n"
    # infantry
    units_col1_text += f"{TRANSL['infantry'][config.LANG]}\n"
    units_col2_text += f"{squad_and_player_stats['allies']['players']['infantry']} / {squad_and_player_stats['allies']['units']['infantry']}\n"
    units_col3_text += f"{squad_and_player_stats['axis']['players']['infantry']} / {squad_and_player_stats['axis']['units']['infantry']}\n"
    # armor
    units_col1_text += f"{TRANSL['armor'][config.LANG]}\n"
    units_col2_text += f"{squad_and_player_stats['allies']['players']['armor']} / {squad_and_player_stats['allies']['units']['armor']}\n"
    units_col3_text += f"{squad_and_player_stats['axis']['players']['armor']} / {squad_and_player_stats['axis']['units']['armor']}\n"
    # artillery
    units_col1_text += f"{TRANSL['artillery'][config.LANG]}\n"
    units_col2_text += f"{squad_and_player_stats['allies']['players']['artillery']} / {squad_and_player_stats['allies']['units']['artillery']}\n"
    units_col3_text += f"{squad_and_player_stats['axis']['players']['artillery']} / {squad_and_player_stats['axis']['units']['artillery']}\n"
    # recon
    units_col1_text += f"{TRANSL['reconnaissance'][config.LANG]}\n"
    units_col2_text += f"{squad_and_player_stats['allies']['players']['recon']} / {squad_and_player_stats['allies']['units']['recon']}\n"
    units_col3_text += f"{squad_and_player_stats['axis']['players']['recon']} / {squad_and_player_stats['axis']['units']['recon']}\n"

    # Stats per role(s)
    # -------------------------------------------------------------------------
    results = {}
    for key, roles in config.CATEGORIES.items():
        t1_rc, t1_ra, t2_rc, t2_ra, ratio = role_avg(all_players, roles)
        if t1_rc > 0 or t2_rc > 0:
            results[key] = {
                "title": f"{TRANSL[key][config.LANG]} - {TRANSL['ratio'][config.LANG]} : {ratio}",
                "graph": level_cursor(t1_ra, t2_ra),
                "ratio": ratio
            }

    # Raw stats
    # -------------------------------------------------------------------------
    fields = [
        ("kills", t1_stats.get("kills", 0), t2_stats.get("kills", 0)),
        ("deaths", t1_stats.get("deaths", 0), t2_stats.get("deaths", 0)),
        ("combat", t1_stats.get("combat", 0), t2_stats.get("combat", 0)),
        ("offense", t1_stats.get("offense", 0), t2_stats.get("offense", 0)),
        ("defense", t1_stats.get("defense", 0), t2_stats.get("defense", 0)),
        ("support", t1_stats.get("support", 0), t2_stats.get("support", 0)),
    ]

    col1_text = f"{TRANSL['players'][config.LANG]}\n"
    col2_text = f"{t1_count}\n"
    col3_text = f"{t2_count}\n"

    for stat_key, v1, v2 in fields:
        s1, s2 = common_functions.bold_the_highest(v1, v2)
        a1 = round(team_avg(all_players, 'allies', stat_key, t1_count))
        a2 = round(team_avg(all_players, 'axis', stat_key, t2_count))

        col1_text += f"{TRANSL[stat_key][config.LANG]} ({TRANSL['tot'][config.LANG]}/{TRANSL['avg'][config.LANG]})\n"
        col2_text += f"{s1} / {a1}\n"
        col3_text += f"{s2} / {a2}\n"

    # Discord embed
    # -------------------------------------------------------------------------
    webhook = discord.SyncWebhook.from_url(discord_webhook)

    if isinstance(avg_diff_ratio, (int, float)):
        avg_diff_ratio_color = avg_diff_ratio
    else:
        avg_diff_ratio_color = 1

    embed = discord.Embed(
        title=embed_title,
        description=level_cursor(t1_lvl_avg, t2_lvl_avg),
        color=int(common_functions.green_to_red(value=avg_diff_ratio_color, min_value=1), base=16),
        url=common_functions.DISCORD_EMBED_AUTHOR_URL
    )
    embed.set_author(name=config.BOT_NAME, icon_url=common_functions.DISCORD_EMBED_AUTHOR_ICON_URL)

    # all players - distribution
    embed.add_field(name=f"{TRANSL['all_players'][config.LANG]} - {TRANSL['distribution'][config.LANG]}",
                    value=level_pop_distribution(all_players),
                    inline=False)

    # Players/squads per unit type
    embed.add_field(name=f"{TRANSL['players'][config.LANG]} / {TRANSL['squads'][config.LANG]}",
                    value=units_col1_text, inline=True)
    embed.add_field(name=f"{TRANSL['allies'][config.LANG]}",
                    value=units_col2_text, inline=True)
    embed.add_field(name=f"{TRANSL['axis'][config.LANG]}",
                    value=units_col3_text, inline=True)

    # Per role
    for key in config.CATEGORIES:
        if key in results:
            embed.add_field(name=results[key]["title"],
                            value=results[key]["graph"],
                            inline=False)

    # Raw stats
    embed.add_field(name=TRANSL['stats'][config.LANG], value=col1_text, inline=True)
    embed.add_field(name=TRANSL['allies'][config.LANG], value=col2_text, inline=True)
    embed.add_field(name=TRANSL['axis'][config.LANG], value=col3_text, inline=True)

    # Timestamp
    embed.timestamp = datetime.datetime.now()

    common_functions.discord_embed_send(embed, webhook, engine)

    # Logs
    # -------------------------------------------------------------------------
    if t1_lvl_avg > 0 and t2_lvl_avg > 0:
        avg_display = round((t1_lvl_avg + t2_lvl_avg) / 2, 1)
        ratio_display = round(max(t1_lvl_avg, t2_lvl_avg) / min(t1_lvl_avg, t2_lvl_avg), 1)
    else:
        avg_display = "N/A"
        ratio_display = "N/A"

    # avg_display = round((t1_lvl_avg + t2_lvl_avg) / 2, 1) if (t1_lvl_avg > 0 and t2_lvl_avg > 0) else "N/A"
    logger.info("Players: %s - Avg level: %s - Ratio: %s", t1_count + t2_count, avg_display, ratio_display)
    logger.info(" - Allies: %s players - Avg level: %s", t1_count, t1_lvl_avg if isinstance(t1_lvl_avg, (int, float)) and t1_lvl_avg != 0 else "N/A")
    logger.info(" - Axis: %s players - Avg level: %s", t2_count, t2_lvl_avg if isinstance(t2_lvl_avg, (int, float)) and t2_lvl_avg != 0 else "N/A")


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
        logger.error("Can't get team_view_stats()")
        return

    watch_balance(
        rcon,
        all_teams,
        all_players,
        engine
    )


logger = logging.getLogger('rcon')

logger.info(
    "\n-------------------------------------------------------------------------------\n"
    "%s (started)\n"
    "-------------------------------------------------------------------------------",
    config.BOT_NAME
)

# Launching
if __name__ == "__main__":
    root_path = os.getenv("BALANCE_WATCH_DATA_PATH", "/data")
    full_path = pathlib.Path(root_path) / pathlib.Path("watch_balance.db")
    engine = create_engine(f"sqlite:///file:{full_path}?mode=rwc&uri=true", echo=False)
    common_functions.Base.metadata.create_all(engine)

    # Running (infinite loop)
    while True:
        watch_balance_loop(engine)
        sleep(config.WATCH_INTERVAL_SECS)
