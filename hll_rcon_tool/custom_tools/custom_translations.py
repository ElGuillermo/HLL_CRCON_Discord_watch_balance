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
    "armycommander": ["commander", "commandant", "Kommandant"],
    "officer": ["squad leader", "officier", "Offizier"],
    "rifleman": ["rifleman", "fusilier", "Schütze"],
    "assault": ["assault", "assault", "Sturmangreifer"],
    "automaticrifleman": ["automatic rifleman", "fusilier automatique", "Automatikgewehrschütze"],
    "medic": ["medic", "médecin", "Sanitäter"],
    "support": ["support", "soutien", "Unterstützung"],
    "heavymachinegunner": ["heavy machinegunner", "mitrailleur", "Maschinengewehrschütze"],
    "antitank": ["antitank", "antichar", "Panzerabwehr"],
    "engineer": ["engineer", "ingénieur", "Pionier"],
    "tankcommander": ["tank commander", "commandant de char", "Panzerkommandant"],
    "crewman": ["crewman", "équipier", "Besatzungsmitglied"],
    "spotter": ["spotter", "observateur", "Späher"],
    "sniper": ["sniper", "sniper", "Scharfschütze"],

    # Teams
    "allies": ["Allies", "Alliés", "Alliierte"],
    "axis": ["Axis", "Axe", "Achsenmächte"],

    # Stats
    "level": ["level", "niveau", "Level"],
    "lvl": ["lvl", "niv", "Lvl"],
    "combat": ["combat", "combat", "Kampfeffektivität"],
    "offense": ["attack", "attaque", "Angriff"],
    "defense": ["defense", "défense", "Verteidigung"],
    "kills": ["kills", "kills", "Kills"],
    "deaths": ["deaths", "morts", "Deaths"],

    # Units
    "years": ["years", "années", "Jahre"],
    "monthes": ["monthes", "mois", "Monate"],
    "weeks": ["weeks", "semaines", "Wochen"],
    "days": ["days", "jours", "Tage"],
    "hours": ["hours", "heures", "Stunden"],
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
    "avg": ["avg", "moy", "avg"],
    "distribution": ["distribution", "distribution", "Verteilung"],
    "players": ["players", "joueurs", "Spieler"],
    "score": ["score", "score", "Punktzahl"],
    "stats": ["stats", "stats", "Statistiken"],
    "total": ["total", "total", "Summe"],
    # "totals": ["totals", "totaux", "Gesamtsummen"],
    "tot": ["tot", "tot", "sum"],
    # "difference": ["difference", "différence", "unterschied"],
    "lastusedweapons": ["last used weapon(s)", "dernière(s) arme(s) utilisée(s)", "Zuletzt verwendete Waffe(n)"],
    "officers": ["officers", "officiers", "Offiziere"],
    "punishment": ["punishment", "punition", "Bestrafung"],
    "ratio": ["ratio", "ratio", "Verhältnis"],
    "victim": ["victim", "victime", "Opfer"],

    # automod_forbid_role.py
    "play_as": ["● Play as", "● A pris le rôle", "● Spiele als"],
    "engaged_action": ["● Engaged action :", "● Action souhaitée :", "● Laufende Aktion"],
    "reason": ["● Reason :", "● Raison :", "● Ursache :"],
    "action_result": ["● Action result :", "● Résultat de l'action :", "● Ergebnis der Aktion"],
    "success": ["✅ Success", "✅ Réussite", "✅ Erfolg"],
    "failure": ["❌ Failure", "❌ Échec", "❌ Fehler"],
    "unknown_action": ["❓ Misconfigured action", "❓ Action mal configurée", "❓ Falsch konfigurierte Aktion"],
    "testmode": ["🧪 Test mode (no action)", "🧪 Mode test (aucune action)", "🧪 Testmodus (keine Aktion)"]
}
