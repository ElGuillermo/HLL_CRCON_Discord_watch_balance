"""
custom_translations.py

Common translation set for HLL CRCON custom plugins
(see : https://github.com/MarechJ/hll_rcon_tool)

Source : https://github.com/ElGuillermo

Feel free to use/modify/distribute, as long as you keep this note in your code
"""

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
    "play_as": ["● Play as", "● A pris le rôle", "● Spiele als"],
    "engaged_action": ["● Engaged action :", "● Action souhaitée :", "● Engagierte Aktion"],
    "reason": ["● Reason :", "● Raison :", "● Ursache :"],
    "action_result": ["● Action result :", "● Résultat de l'action :", "● Ergebnis der Aktion"],
    "success": ["✅ Success", "✅ Réussite", "✅ Erfolg"],
    "failure": ["❌ Failure", "❌ Échec", "❌ Versagen"],
    "unknown_action": ["❓ Misconfigured action", "❓ Action mal configurée", "❓ Falsch konfigurierte Aktion"],
    "testmode": ["🧪 Test mode (no action)", "🧪 Mode test (aucune action)", "🧪 Testmodus (keine Aktion)"]
}
