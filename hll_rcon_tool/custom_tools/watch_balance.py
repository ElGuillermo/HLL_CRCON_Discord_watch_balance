"""
watch_balance.py

A plugin for HLL CRCON (https://github.com/MarechJ/hll_rcon_tool)
that watches the teams players levels.

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import logging
from time import sleep
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


def watch_balance_loop(engine) -> None:
    """
    Calls the function that gathers data,
    then calls the function to analyze it.
    """
    rcon = Rcon(SERVER_INFO)

    (
        all_teams,
        all_players,
        _,
        _,
        _,
        _,
        _
    ) = common_functions.team_view_stats(rcon)

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
    # Check if enabled
    server_number = int(get_server_number())
    if not config.SERVER_CONFIG[server_number - 1][1]:
        return
    discord_webhook = config.SERVER_CONFIG[server_number - 1][0]

    # Gather data
    for team in all_teams:
        if "allies" in team:
            t1_count: int = team["allies"]["count"]
            t1_lvl_avg: float = team_avg(all_players, "allies", "level", t1_count)
            t1_kills: int = team["allies"]["kills"]
            t1_deaths: int = team["allies"]["deaths"]
            t1_combat: int = team["allies"]["combat"]
            t1_off: int = team["allies"]["offense"]
            t1_def: int = team["allies"]["defense"]
            t1_support: int = team["allies"]["support"]
        elif "axis" in team:
            t2_count: int = team["axis"]["count"]
            t2_lvl_avg: float = team_avg(all_players, "axis", "level", t2_count)
            t2_kills: int = team["axis"]["kills"]
            t2_deaths: int = team["axis"]["deaths"]
            t2_combat: int = team["axis"]["combat"]
            t2_off: int = team["axis"]["offense"]
            t2_def: int = team["axis"]["defense"]
            t2_support: int = team["axis"]["support"]

    if t1_lvl_avg == 0 or t2_lvl_avg == 0:
        logger.info(
            "Bad data : either Allies or Axis average level is 0. Waiting for %s mins...",
            round((config.WATCH_INTERVAL_SECS / 60), 2)
        )
        return

    # Gather data : officers
    t1_officers_lvl_tot: int = 0
    t1_officers_count: int = 0
    t2_officers_lvl_tot: int = 0
    t2_officers_count: int = 0
    for player in all_players:
        if player["role"] in ("commander", "officer", "tankcommander", "spotter"):
            if player["team"] == "allies":
                t1_officers_lvl_tot: int = t1_officers_lvl_tot + player["level"]
                t1_officers_count: int = t1_officers_count + 1
            elif player["team"] == "axis":
                t2_officers_lvl_tot: int = t2_officers_lvl_tot + player["level"]
                t2_officers_count: int = t2_officers_count + 1
    if t1_officers_count != 0 and t2_officers_count != 0:
        t1_officers_lvl_avg: float = t1_officers_lvl_tot / t1_officers_count
        t2_officers_lvl_avg: float = t2_officers_lvl_tot / t2_officers_count
    else:
        t1_officers_lvl_avg: float = 0
        t2_officers_lvl_avg: float = 0

    # Discord embed title
    avg_diff_ratio: float = max(t1_lvl_avg, t2_lvl_avg) / min(t1_lvl_avg, t2_lvl_avg)
    embed_title: str = f"{TRANSL['ratio'][config.LANG]} : {str(round(avg_diff_ratio, 2))}"

    # Average level (all players) : title
    all_lvl_avg: float = (t1_lvl_avg + t2_lvl_avg) / 2
    all_lvl_avg_title: str = f"{TRANSL['level'][config.LANG]} ({TRANSL['avg'][config.LANG]}) : {round(all_lvl_avg)}"

    all_lvl_graph: str = level_cursor(
        t1_lvl_avg = t1_lvl_avg,
        t2_lvl_avg = t2_lvl_avg
    )

    # Average level (officers) : title
    if t1_officers_count != 0 and t2_officers_count != 0 :
        all_officers_lvl_avg: float = (t1_officers_lvl_tot + t2_officers_lvl_tot) / (t1_officers_count + t2_officers_count)
        all_officers_lvl_avg_title: str = f"{TRANSL['level'][config.LANG]} {TRANSL['officers'][config.LANG]} ({TRANSL['avg'][config.LANG]}) : {round(all_officers_lvl_avg)}"

        all_officers_lvl_graph: str = level_cursor(
            t1_lvl_avg = t1_officers_lvl_avg,
            t2_lvl_avg = t2_officers_lvl_avg
        )

    # level population : title
    all_lvl_pop_title: str = f"{TRANSL['level'][config.LANG]} {TRANSL['distribution'][config.LANG]}"

    # Teams stats
    all_lvl_pop_text: str = level_pop_distribution(
        all_players = all_players,
        t1_count = t1_count,
        t2_count = t2_count
    )

    # col1
    col1_embed_title: str = f"{TRANSL['stats'][config.LANG]}"
    transl_tot_moy: str = f"({TRANSL['tot'][config.LANG]}/{TRANSL['avg'][config.LANG]})"
    col1_embed_text: str = (
        f"{TRANSL['players'][config.LANG]}\n\n"
        f"{TRANSL['kills'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['deaths'][config.LANG]} {transl_tot_moy}\n\n"
        f"{TRANSL['combat'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['offense'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['defense'][config.LANG]} {transl_tot_moy}\n"
        f"{TRANSL['support'][config.LANG]} {transl_tot_moy}"
    )

    # col2
    # col3
    t1_kills_str, t2_kills_str = common_functions.bold_the_highest(t1_kills, t2_kills)
    t1_deaths_str, t2_deaths_str = common_functions.bold_the_highest(t1_deaths, t2_deaths)
    t1_combat_str, t2_combat_str = common_functions.bold_the_highest(t1_combat, t2_combat)
    t1_off_str, t2_off_str = common_functions.bold_the_highest(t1_off, t2_off)
    t1_def_str, t2_def_str = common_functions.bold_the_highest(t1_def, t2_def)
    t1_support_str, t2_support_str = common_functions.bold_the_highest(t1_support, t2_support)

    # col2
    col2_embed_title: str = TRANSL["allies"][config.LANG]
    col2_embed_text: str = (
        f"{str(t1_count)}\n\n"
        f"{t1_kills_str} / {str(round(team_avg(all_players, 'allies', 'kills', t1_count)))}\n"
        f"{t1_deaths_str} / {str(round(team_avg(all_players, 'allies', 'deaths', t1_count)))}\n\n"
        f"{t1_combat_str} / {str(round(team_avg(all_players, 'allies', 'combat', t1_count)))}\n"
        f"{t1_off_str} / {str(round(team_avg(all_players, 'allies', 'offense', t1_count)))}\n"
        f"{t1_def_str} / {str(round(team_avg(all_players, 'allies', 'defense', t1_count)))}\n"
        f"{t1_support_str} / {str(round(team_avg(all_players, 'allies', 'support', t1_count)))}\n"
    )

    # col3
    col3_embed_title: str = TRANSL["axis"][config.LANG]
    col3_embed_text: str = (
        f"{str(t2_count)}\n\n"
        f"{t2_kills_str} / {str(round(team_avg(all_players, 'axis', 'kills', t2_count)))}\n"
        f"{t2_deaths_str} / {str(round(team_avg(all_players, 'axis', 'deaths', t2_count)))}\n\n"
        f"{t2_combat_str} / {str(round(team_avg(all_players, 'axis', 'combat', t2_count)))}\n"
        f"{t2_off_str} / {str(round(team_avg(all_players, 'axis', 'offense', t2_count)))}\n"
        f"{t2_def_str} / {str(round(team_avg(all_players, 'axis', 'defense', t2_count)))}\n"
        f"{t2_support_str} / {str(round(team_avg(all_players, 'axis', 'support', t2_count)))}\n"
    )

    # Log
    logger.info(
        "%s : %s - %s : (%s) %s ; (%s) %s - %s : (%s) %s ; (%s) %s",
            TRANSL['ratio'][config.LANG],
            str(round(avg_diff_ratio, 2)),
            TRANSL['players'][config.LANG],
            TRANSL['allies'][config.LANG],
            str(round(t1_lvl_avg, 2)),
            TRANSL['axis'][config.LANG],
            str(round(t2_lvl_avg, 2)),
            TRANSL['officers'][config.LANG],
            TRANSL['allies'][config.LANG],
            str(round(t1_officers_lvl_avg, 2)),
            TRANSL['axis'][config.LANG],
            str(round(t2_officers_lvl_avg, 2))
    )

    # Create and send discord embed
    webhook = discord.SyncWebhook.from_url(discord_webhook)
    embed = discord.Embed(
        title=embed_title,
        url=common_functions.DISCORD_EMBED_AUTHOR_URL,
        color=int(
            common_functions.green_to_red(value=avg_diff_ratio, min_value=1, max_value=2),
            base=16
        )
    )
    embed.set_author(
        name=config.BOT_NAME,
        url=common_functions.DISCORD_EMBED_AUTHOR_URL,
        icon_url=common_functions.DISCORD_EMBED_AUTHOR_ICON_URL
    )
    embed.add_field(name=all_lvl_avg_title, value=all_lvl_graph, inline=False)
    if t1_officers_count != 0 and t2_officers_count != 0 :
        embed.add_field(
            name=all_officers_lvl_avg_title, value=all_officers_lvl_graph, inline=False
        )
    embed.add_field(name=all_lvl_pop_title, value=all_lvl_pop_text, inline=False)
    embed.add_field(name=col1_embed_title, value=col1_embed_text, inline=True)
    embed.add_field(name=col2_embed_title, value=col2_embed_text, inline=True)
    embed.add_field(name=col3_embed_title, value=col3_embed_text, inline=True)

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
