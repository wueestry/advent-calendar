from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Door:
    day: int
    suid: str
    title: str
    subtitle: str
    content: str
    image: str | None = None
    image_alt: str | None = None
    video: str | None = None
    youtube_embed: str | None = None


DOORS: tuple[Door, ...] = (
    Door(
        day=1,
        suid="a9f3c7e1b402",
        title="Die erste Kerze",
        subtitle="1. Dezember — Der Countdown beginnt",
        content=(
            "Willkommen beim ersten Türchen des Adventskalenders! Zünden Sie eine "
            "warme Kerze an, giessen Sie sich eine Tasse heisse Schokolade ein und "
            "geniessen Sie den Start in die besinnliche Zeit."
        ),
        image="day1-candle.svg",
        image_alt="Leuchtende Adventskerze",
    ),
    Door(
        day=2,
        suid="d4e8b2109c7a",
        title="Lebkuchen",
        subtitle="2. Dezember — Duft aus der Küche",
        content=(
            "Heute gibt es frisch gebackene Lebkuchen mit Zimt, Nelken, Muskatnuss "
            "und einem Hauch Honig. Am besten schmecken sie noch lauwarm."
        ),
    ),
    Door(
        day=3,
        suid="7c15f90ae3d8",
        title="Erster Frost",
        subtitle="3. Dezember — Klarer Wintermorgen",
        content=(
            "Feine Eiskristalle zeichnen Farnmuster an die Fensterscheibe. Ziehen "
            "Sie den wärmsten Schal an, bevor Sie nach draussen treten."
        ),
    ),
    Door(
        day=4,
        suid="e6204b8fd193",
        title="Barbarazweige",
        subtitle="4. Dezember — Kirschblüten im Winter",
        content=(
            "Der Tradition nach schneidet man heute einen Zweig vom Kirschbaum ab "
            "und stellt ihn ins Wasser. Blüht er bis Heiligabend, bringt das Glück."
        ),
    ),
    Door(
        day=5,
        suid="3b9d74c20fa6",
        title="Sternenlaternen",
        subtitle="5. Dezember — Leuchtende Papiersterne",
        content=(
            "Gefaltete Papiersterne, von innen beleuchtet, verbreiten in der frühen "
            "Abenddämmerung ein warmes, goldenes Licht."
        ),
    ),
    Door(
        day=6,
        suid="8f01e5a6c7b4",
        title="Nikolaustag",
        subtitle="6. Dezember — Geputzte Stiefel vor der Tür",
        content=(
            "Schauen Sie heute Morgen in Ihre Stiefel! Mandarinen, geröstete "
            "Erdnüsse, Schokoladentaler und Marzipan warten auf Sie."
        ),
    ),
    Door(
        day=7,
        suid="c3a792f418e0",
        title="Tannenzapfen-Girlande",
        subtitle="7. Dezember — Waldige Dekoration",
        content=(
            "Gesammelte Tannenzapfen, leicht mit Schnee bestäubt, ergeben eine "
            "rustikale Girlande für das Kaminsims."
        ),
    ),
    Door(
        day=8,
        suid="5d40b8e73a19",
        title="Heisse Marroni",
        subtitle="8. Dezember — Wärme auf dem Marktplatz",
        content=(
            "Eine Papiertüte mit heissen Marroni wärmt die kalten Finger, während "
            "Sie an den hölzernen Marktständen vorbeischlendern."
        ),
    ),
    Door(
        day=9,
        suid="1e8c63a9f52b",
        title="Wintermelodie",
        subtitle="9. Dezember — Ruhige Klänge",
        content=(
            "Nehmen Sie sich heute zehn stille Minuten Zeit und hören Sie Ihr "
            "liebstes winterliches Instrumentalstück, während der Himmel dunkler wird."
        ),
    ),
    Door(
        day=10,
        suid="9b24d7e0c68f",
        title="Zimtsterne",
        subtitle="10. Dezember — Backtag für Zimtsterne",
        content=(
            "Mandelmeringue-Plätzchen mit weisser Glasur und duftendem Ceylon-Zimt "
            "sind ein echter Winterklassiker."
        ),
    ),
    Door(
        day=11,
        suid="6f51a3c8d902",
        title="Verschneite Tannen",
        subtitle="11. Dezember — Stiller Waldweg",
        content=(
            "Nichts ist schöner als die Stille eines Tannenwaldes direkt nach dem "
            "ersten Schneefall, wenn jeder Zweig die Schritte dämpft."
        ),
    ),
    Door(
        day=12,
        suid="b0e94c712f5d",
        title="Halbzeit bis Heiligabend",
        subtitle="12. Dezember — Zwölf Türchen geschafft",
        content=(
            "Sie haben die Mitte des Adventskalenders erreicht! Gönnen Sie sich "
            "einen gemütlichen Abend am Feuer."
        ),
    ),
    Door(
        day=13,
        suid="4a7d18f3b6e9",
        title="Fest des Lichts",
        subtitle="13. Dezember — Luciafest",
        content=(
            "Safranbrötchen und leuchtende Umzüge bringen Licht in eine der "
            "dunkelsten Nächte des Jahres."
        ),
    ),
    Door(
        day=14,
        suid="d832c509e17a",
        title="Glühmost",
        subtitle="14. Dezember — Köchelnde Gewürze",
        content=(
            "Lassen Sie Apfelmost mit Orangenschale, Sternanis und einer Zimtstange "
            "sanft ziehen — sofort entsteht eine wohlige Atmosphäre."
        ),
    ),
    Door(
        day=15,
        suid="2c96f0b4a83e",
        title="Handgeschriebene Karten",
        subtitle="15. Dezember — Warme Worte verschicken",
        content=(
            "Schreiben Sie einer Person, von der Sie lange nichts gehört haben, "
            "ein paar Zeilen von Hand — rechtzeitig für die Weihnachtspost."
        ),
    ),
    Door(
        day=16,
        suid="7e14a9d5c06b",
        title="Lesestunde am Feuer",
        subtitle="16. Dezember — Ein Kapitel unter der Decke",
        content=(
            "Nehmen Sie das Buch vom Nachttisch und lesen Sie ein Kapitel bei einer "
            "Tasse Kräutertee."
        ),
    ),
    Door(
        day=17,
        suid="f5b820e63d41",
        title="Vanillekipferl",
        subtitle="17. Dezember — Buttrige Halbmonde",
        content=(
            "Mürbe Nusshörnchen, noch warm aus dem Ofen in Vanillezucker gewälzt — "
            "ein Duft wie aus der Kindheit."
        ),
    ),
    Door(
        day=18,
        suid="0a63d4f98b27",
        title="Funkelnder Kranz",
        subtitle="18. Dezember — Tannengrün und Beeren",
        content=(
            "Frische Tannenzweige mit Stechpalmenbeeren und Lichterketten "
            "verwandeln die Haustür in einen festlichen Empfang."
        ),
    ),
    Door(
        day=19,
        suid="c749e1a25f80",
        title="Sternklarer Himmel",
        subtitle="19. Dezember — Der Orion steigt",
        content=(
            "Klare Winternächte bieten die schärfste Sicht auf den Orion und die "
            "Plejaden. Treten Sie kurz vor die Tür und schauen Sie nach oben."
        ),
    ),
    Door(
        day=20,
        suid="8d10b6c47e93",
        title="Geschenkpapier und Schleifen",
        subtitle="20. Dezember — Liebevoll verpackt",
        content=(
            "Braunes Packpapier, Kordel und ein Zweig Rosmarin machen auch aus dem "
            "einfachsten Geschenk ein kleines Kunstwerk."
        ),
    ),
    Door(
        day=21,
        suid="3f68a2e1d95c",
        title="Wintersonnenwende",
        subtitle="21. Dezember — Die längste Nacht",
        content=(
            "Heute ist die Wintersonnenwende. Ab morgen schenkt uns jeder Tag wieder "
            "ein paar Minuten mehr Licht."
        ),
    ),
    Door(
        day=22,
        suid="a1c579f04e82",
        title="Nussknacker-Suite",
        subtitle="22. Dezember — Tschaikowskis Magie",
        content=(
            "Vom Tanz der Zuckerfee bis zum Blumenwalzer — lassen Sie sich von der "
            "klassischen Musik in Weihnachtsstimmung bringen."
        ),
    ),
    Door(
        day=23,
        suid="5e92d3b71a46",
        title="Der Abend davor",
        subtitle="23. Dezember — Ruhige Vorfreude",
        content=(
            "Die Einkäufe sind erledigt, die Lichter gedimmt, und das Haus füllt "
            "sich mit stiller Vorfreude auf morgen."
        ),
    ),
    Door(
        day=24,
        suid="e047f8c39b15",
        title="Heiligabend",
        subtitle="24. Dezember — Das letzte Türchen",
        content=(
            "Herzlichen Glückwunsch, Sie haben alle 24 Türchen geöffnet! Ich wünsche "
            "Ihnen Frieden, Freude, Wärme und wunderbare Gesellschaft in dieser "
            "Festzeit."
        ),
    ),
)

DOORS_BY_SUID: dict[str, Door] = {door.suid: door for door in DOORS}
DOORS_BY_DAY: dict[int, Door] = {door.day: door for door in DOORS}


def get_door_by_suid(suid: str) -> Door | None:
    return DOORS_BY_SUID.get(suid)


def get_door_by_day(day: int) -> Door | None:
    return DOORS_BY_DAY.get(day)
