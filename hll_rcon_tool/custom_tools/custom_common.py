"""
custom_common.py

Common tools and parameters set for HLL CRCON custom plugins
(see : https://github.com/MarechJ/hll_rcon_tool)

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

import json
import logging
from datetime import datetime, timezone, timedelta
import requests  # type: ignore
import discord  # type: ignore
from rcon.rcon import Rcon
from rcon.steam_utils import get_steam_api_key
from rcon.user_config.rcon_server_settings import RconServerSettingsUserConfig


# Configuration (you should review/change these !)
# -----------------------------------------------------------------------------

# Discord embeds strings translations
# Available : 0 for english, 1 for french, 2 for german
LANG = 0


# Miscellaneous (you don't have to change these)
# ----------------------------------------------

# Discord : embed author icon
DISCORD_EMBED_AUTHOR_ICON_URL = (
    "https://styles.redditmedia.com/"
    "t5_3ejz4/styles/communityIcon_x51js3a1fr0b1.png"
)

# Discord : default avatars
DEFAULT_AVATAR_STEAM = (
    "https://steamcdn-a.akamaihd.net/"
    "steamcommunity/public/images/avatars/"
    "b5/b5bd56c1aa4644a474a2e4972be27ef9e82e517e_medium.jpg"
)
DEFAULT_AVATAR_GAMEPASS = (
    "https://sc.filehippo.net/images/t_app-logo-l,f_auto,dpr_auto/p/"
    "2cf512ee-a9da-11e8-8bdc-02420a000abe/3169937124/xbox-game-pass-logo"
)

# Discord : external profile infos urls
STEAM_PROFILE_INFO_URL = "https://steamcommunity.com/profiles/"  # + id
GAMEPASS_PROFILE_INFO_URL = "https://xboxgamertag.com/search/"  # + name (spaces are replaced by -)

# Team related (as set in /settings/rcon-server)
try:
    config = RconServerSettingsUserConfig.load_from_db()
    CLAN_URL = str(config.discord_invite_url)
    DISCORD_EMBED_AUTHOR_URL = str(config.server_url)
except Exception:
    CLAN_URL = ""
    DISCORD_EMBED_AUTHOR_URL = ""

# Lists
# Used by watch_killrate.py
WEAPONS_ARTILLERY = [
    "155MM HOWITZER [M114]",
    "150MM HOWITZER [sFH 18]",
    "122MM HOWITZER [M1938 (M-30)]",
    "QF 25-POUNDER [QF 25-Pounder]"
]


# Translations
# key : english, french, german
# ----------------------------------------------

TRANSL = {
    # Roles
    "armycommander": ["commander", "commandant", "kommandant"],
    "officer": ["squad leader", "officier", "offizier"],
    "rifleman": ["rifleman", "fusilier", "schütze"],
    "assault": ["assault", "assault", "angriff"],
    "automaticrifleman": ["automatic rifleman", "fusilier automatique", "automatischer schütze"],
    "medic": ["medic", "médecin", "arfzt"],
    "support": ["support", "soutien", "unterstützung"],
    "heavymachinegunner": ["heavy machinegunner", "mitrailleur", "schweres maschinengewehr"],
    "antitank": ["antitank", "antichar", "panzerabwehr"],
    "engineer": ["engineer", "ingénieur", "ingenieur"],
    "tankcommander": ["tank commander", "commandant de char", "panzerkommandant"],
    "crewman": ["crewman", "équipier", "besatzungsmitglied"],
    "spotter": ["spotter", "observateur", "aufklärer"],
    "sniper": ["sniper", "sniper", "scharfschütze"],
    # Teams
    "allies": ["Allies", "Alliés", "Alliierte"],
    "axis": ["Axis", "Axe", "Achsenmächte"],
    # Stats
    "level": ["level", "niveau", "ebene"],
    "lvl": ["lvl", "niv", "ebe"],
    "combat": ["combat", "combat", "kampf"],
    "offense": ["attack", "attaque", "angriff"],
    "defense": ["defense", "défense", "verteidigung"],
    "kills": ["kills", "kills", "tötet"],
    "deaths": ["deaths", "morts", "todesfälle"],
    # Units
    "years": ["years", "années", "Jahre"],
    "monthes": ["monthes", "mois", "Monate"],
    "weeks": ["weeks", "semaines", "Wochen"],
    "days": ["days", "jours", "Tage"],
    "hours": ["hours", "heures", "Dienststunden"],
    "minutes": ["minutes", "minutes", "Minuten"],
    "seconds": ["seconds", "secondes", "Sekunden"],
    # !me (hooks_custom_chatcommands.py -> WARNING : circular import)
    # "nopunish": ["None ! Well done !", "Aucune ! Félicitations !", "Keiner! Gut gemacht!"],
    # "firsttimehere": ["first time here", "tu es venu(e) il y a", "zum ersten Mal hier"],
    # "gamesessions": ["game sessions", "sessions de jeu", "Spielesitzungen"],
    # "playedgames": ["played games", "parties jouées", "gespielte Spiele"],
    # "cumulatedplaytime": ["cumulated play time", "temps de jeu cumulé", "kumulierte Spielzeit"],
    # "averagesession": ["average session", "session moyenne", "Durchschnittliche Sitzung"],
    # "punishments": ["punishments", "punitions", "Strafen"],
    # "favoriteweapons": ["favorite weapons", "armes favorites", "Lieblingswaffen"],
    # "victims": ["victims", "victimes", "Opfer"],
    # "nemesis": ["nemesis", "nemesis", "Nemesis"],
    # Various
    "average": ["average", "moyenne", "Durchschnitt"],
    # "averages": ["averages", "moyennes", "Durchschnittswerte"],
    "avg": ["avg", "moy", "mit"],
    "distribution": ["distribution", "distribution", "Verteilung"],
    "players": ["players", "joueurs", "spieler"],
    "score": ["score", "score", "Punktzahl"],
    "stats": ["stats", "stats", "statistiken"],
    "total": ["total", "total", "gesamt"],
    # "totals": ["totals", "totaux", "Gesamtsummen"],
    "tot": ["tot", "tot", "ges"],
    # "difference": ["difference", "différence", "unterschied"],
    "lastusedweapons": ["last used weapon(s)", "dernière(s) arme(s) utilisée(s)", "zuletzt verwendete Waffe(n)"],
    "officers": ["officers", "officiers", "offiziere"],
    "punishment": ["punishment", "punition", "Bestrafung"],
    "ratio": ["ratio", "ratio", "verhältnis"],
    "victim": ["victim", "victime", "Opfer"],
    # automod_forbid_role.py
    "play_as": ["● Play as", "● A pris le rôle", "Spiele als"],
    "engaged_action": ["● Engaged action :", "● Action souhaitée :", "● Engagierte Aktion"],
    "reason": ["● Reason :", "● Raison :", "● Ursache :"],
    "action_result": ["● Action result :", "● Résultat de l'action :", "● Ergebnis der Aktion"],
    "success": ["✅ Success", "✅ Réussite", "✅ Erfolg"],
    "failure": ["❌ Failure", "❌ Échec", "❌ Versagen"],
    "unknown_action": ["❓ Misconfigured action", "❓ Action mal configurée", "❓ Falsch konfigurierte Aktion"],
    "testmode": ["🧪 Test mode (no action)", "🧪 Mode test (aucune action)", "🧪 Testmodus (keine Aktion)"]
}


# (End of configuration)
# -----------------------------------------------------------------------------


def bold_the_highest(
    first_value: int,
    second_value: int
) -> str:
    """
    Returns two strings, the highest formatted in bold
    """
    if first_value > second_value:
        return f"**{first_value}**", str(second_value)  # type: ignore
    if first_value < second_value:
        return str(first_value), f"**{second_value}**"  # type: ignore
    return str(first_value), str(second_value)  # type: ignore


def get_avatar_url(
    player_id: str
):
    """
    Returns the avatar url from a player ID
    Steam players can have an avatar
    GamePass players will get a default avatar
    """
    if len(player_id) == 17:
        try:
            return get_steam_avatar(player_id)
        except Exception:
            return DEFAULT_AVATAR_STEAM
    return DEFAULT_AVATAR_STEAM


def get_steam_avatar(
    player_id: str,
    avatar_size: str = "avatarmedium"
) -> str:
    """
    Returns the Steam avatar image url, according to desired size
    Available avatar_size :
        "avatar" : 32x32 ; "avatarmedium" : 64x64 ; "avatarfull" : 184x184
    """
    try:
        steam_api_key = get_steam_api_key()
        if not steam_api_key or steam_api_key == "":
            return DEFAULT_AVATAR_STEAM
    except Exception:
        return DEFAULT_AVATAR_STEAM

    steam_api_url = (
        "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        f"?key={steam_api_key}"
        f"&steamids={player_id}"
    )
    try:
        steam_api_json = requests.get(steam_api_url, timeout=10)
        steam_api_json_parsed = json.loads(steam_api_json.text)
        return steam_api_json_parsed["response"]["players"][0][avatar_size]
    except Exception:
        return DEFAULT_AVATAR_STEAM


def get_external_profile_url(
    player_id: str,
    player_name: str,
) -> str:
    """
    Constructs the external profile url for Steam or GamePass
    """
    if len(player_id) == 17:
        ext_profile_url = f"{STEAM_PROFILE_INFO_URL}{player_id}"
    elif len(player_id) > 17:
        gamepass_pseudo_url = player_name.replace(" ", "-")
        ext_profile_url = f"{GAMEPASS_PROFILE_INFO_URL}{gamepass_pseudo_url}"
    return ext_profile_url


def seconds_until_start(schedule) -> int:
    """
    Outside scheduled activity :
        Returns the number of seconds until the next scheduled active time
    During scheduled activity :
        Returns 0

    schedule example :
    Hours are in UTC (heure d'hiver : UTC = FR-1 ; heure d'été : UTC = FR-2)
    ie part time : "0: (4, 30, 21, 15)" means "active on mondays, from 4:30am to 9:15pm
    ie full time : "3: (0, 0, 23, 59)" means "active on thursdays, from 0:00am to 11:59pm"

    SCHEDULE = {
        0: (3, 1, 21, 0),  # Monday
        1: (3, 1, 21, 0),  # Tuesday
        2: (3, 1, 21, 0),  # Wednesday
        3: (3, 1, 21, 0),  # Thursday
        4: (3, 1, 21, 0),  # Friday
        5: (3, 1, 21, 0),  # Saturday
        6: (3, 1, 21, 0)  # Sunday
    }
    """
    # Get the user config
    now = datetime.now(timezone.utc)
    (
        today_start_hour,
        today_start_minute,
        today_end_hour,
        today_end_minute
    ) = schedule[now.weekday()]

    # Build a timestamp for today's start time
    today_dt = datetime.today()
    today_start_str = (
        f"{today_dt.day}"
        f" {today_dt.month}"
        f" {today_dt.year}"
        f" {today_start_hour}"
        f" {today_start_minute}+0000"
    )
    today_start_dt = datetime.strptime(today_start_str, "%d %m %Y %H %M%z")

    # Build a timestamp for tomorrow's start time
    tomorrow_dt = datetime.today() + timedelta(days=1)
    if now.weekday() == 6:  # Today is sunday
        tomorrow_start_hour, tomorrow_start_minute, _, _ = schedule[0]
    else:
        tomorrow_start_hour, tomorrow_start_minute, _, _ = schedule[now.weekday()+1]
    tomorrow_start_str = (
        f"{tomorrow_dt.day}"
        f" {tomorrow_dt.month}"
        f" {tomorrow_dt.year}"
        f" {tomorrow_start_hour}"
        f" {tomorrow_start_minute}+0000"
    )
    tomorrow_start_dt = datetime.strptime(tomorrow_start_str, "%d %m %Y %H %M%z")

    # Evaluate the seconds to wait until the next activity time
    if (
        today_start_hour - now.hour > 0 or (
            today_start_hour - now.hour == 0 and today_start_minute - now.minute > 0
        )
    ):
        return_value = int((today_start_dt - now).total_seconds())
    elif (
        today_start_hour - now.hour < 0 and (
            (today_end_hour - now.hour == 0 and today_end_minute - now.minute <= 0)
            or today_end_hour - now.hour < 0
        )
    ):
        return_value = int((tomorrow_start_dt - now).total_seconds())
    else:
        return_value = 0

    return return_value


def green_to_red(
        value: float,
        min_value: float,
        max_value: float
    ) -> str:
    """
    Returns an string value
    corresponding to a color
    from plain green 00ff00 (value <= min_value)
    to plain red ff0000 (value >= max_value)
    You will have to convert it in the caller code :
    ie for a decimal Discord embed color : int(hex_color, base=16)
    """
    if value < min_value:
        value = min_value
    elif value > max_value:
        value = max_value
    range_value = max_value - min_value
    ratio = (value - min_value) / range_value
    red = int(255 * ratio)
    green = int(255 * (1 - ratio))
    hex_color = f"{red:02x}{green:02x}00"
    return hex_color


def send_discord_embed(
    bot_name: str,
    embed_title: str,
    embed_title_url: str,
    steam_avatar_url: str,
    embed_desc_txt: str,
    embed_color,
    discord_webhook: str
):
    """
    Sends an embed message to Discord
    """
    webhook = discord.SyncWebhook.from_url(discord_webhook)
    embed = discord.Embed(
        title=embed_title,
        url=embed_title_url,
        description=embed_desc_txt,
        color=embed_color
    )
    embed.set_author(
        name=bot_name,
        url=DISCORD_EMBED_AUTHOR_URL,
        icon_url=DISCORD_EMBED_AUTHOR_ICON_URL
    )
    embed.set_thumbnail(url=steam_avatar_url)
    embeds = []
    embeds.append(embed)
    webhook.send(embeds=embeds, wait=True)


def team_view_stats(rcon: Rcon):
    """
    Get the get_team_view data
    and gather the infos according to the squad types and soldier roles
    """
    all_teams = []
    all_players = []
    all_commanders = []
    all_infantry_players = []
    all_armor_players = []
    all_infantry_squads = []
    all_armor_squads = []

    try:
        get_team_view: dict = rcon.get_team_view()
    except Exception as error:
        logger = logging.getLogger('rcon')
        logger.error("Command failed : get_team_view()\n%s", error)
        return (
            all_teams,
            all_players,
            all_commanders,
            all_infantry_players,
            all_armor_players,
            all_infantry_squads,
            all_armor_squads
        )

    for team in ["allies", "axis"]:

        if team in get_team_view:

            # Commanders
            if get_team_view[team]["commander"] is not None:
                all_players.append(get_team_view[team]["commander"])
                all_commanders.append(get_team_view[team]["commander"])

            for squad in get_team_view[team]["squads"]:

                squad_data = get_team_view[team]["squads"][squad]
                squad_data["team"] = team  # Injection du nom de team dans la branche de la squad

                # Infantry
                if (
                    squad_data["type"] == "infantry"
                    or squad_data["type"] == "recon"
                ):
                    all_players.extend(squad_data["players"])
                    all_infantry_players.extend(squad_data["players"])
                    squad_data.pop("players", None)
                    all_infantry_squads.append({squad: squad_data})

                # Armor
                elif (
                    squad_data["type"] == "armor"
                ):
                    all_players.extend(squad_data["players"])
                    all_armor_players.extend(squad_data["players"])
                    squad_data.pop("players", None)
                    all_armor_squads.append({squad: squad_data})

            # Teams global stats
            team_data = get_team_view[team]
            team_data.pop("squads", None)
            team_data.pop("commander", None)
            all_teams.append({team: team_data})

    return (
        all_teams,
        all_players,
        all_commanders,
        all_infantry_players,
        all_armor_players,
        all_infantry_squads,
        all_armor_squads
    )
