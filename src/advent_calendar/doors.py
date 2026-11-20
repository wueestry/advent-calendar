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
        title="The First Candle",
        subtitle="December 1 — Let the countdown begin",
        content="Welcome to Day 1 of the Advent Calendar! Light a warm candle, pour a mug of hot cocoa, and enjoy the start of the festive season.",
        image="day1-candle.svg",
        image_alt="Glowing Advent candle illustration",
    ),
    Door(
        day=2,
        suid="d4e8b2109c7a",
        title="Spiced Gingerbread",
        subtitle="December 2 — Kitchen aromas",
        content="Today's treat: freshly baked gingerbread cookies seasoned with cinnamon, cloves, nutmeg, and a touch of molasses.",
    ),
    Door(
        day=3,
        suid="7c15f90ae3d8",
        title="First Frost",
        subtitle="December 3 — Crisp winter morning",
        content="Delicate ice crystals trace fern patterns across the windowpane. Bundle up in your warmest scarf before stepping outside.",
    ),
    Door(
        day=4,
        suid="e6204b8fd193",
        title="Barbara's Branches",
        subtitle="December 4 — Cherry blossoms in winter",
        content="According to tradition, cutting a fruit tree branch today and placing it in water indoors brings luck if it blooms by Christmas Eve.",
    ),
    Door(
        day=5,
        suid="3b9d74c20fa6",
        title="Starlight Lanterns",
        subtitle="December 5 — Glowing paper stars",
        content="Folded paper stars illuminated from within cast a gentle amber glow through the early evening dusk.",
    ),
    Door(
        day=6,
        suid="8f01e5a6c7b4",
        title="St. Nicholas Day",
        subtitle="December 6 — Polished boots by the door",
        content="Check your boots this morning! Mandarins, roasted peanuts, chocolate coins, and marzipan await.",
    ),
    Door(
        day=7,
        suid="c3a792f418e0",
        title="Pinecone Garland",
        subtitle="December 7 — Woodland decorations",
        content="Foraged pinecones dusted with snow make a rustic garland along the mantelpiece.",
    ),
    Door(
        day=8,
        suid="5d40b8e73a19",
        title="Roasted Chestnuts",
        subtitle="December 8 — Market square warmth",
        content="A paper cone of hot roasted chestnuts warms frozen fingers as you stroll past wooden market stalls.",
    ),
    Door(
        day=9,
        suid="1e8c63a9f52b",
        title="Winter Melody",
        subtitle="December 9 — Acoustic carols",
        content="Take ten quiet minutes today to listen to your favorite winter instrumental piece while watching the sky darken.",
    ),
    Door(
        day=10,
        suid="9b24d7e0c68f",
        title="Cinnamon Stars",
        subtitle="December 10 — Zimtsterne baking day",
        content="Almond meringue cookies glazed with crisp white icing and fragrant Ceylon cinnamon—a true winter classic.",
    ),
    Door(
        day=11,
        suid="6f51a3c8d902",
        title="Snowy Pines",
        subtitle="December 11 — Quiet forest trail",
        content="Nothing beats the hush of a pine forest right after fresh snowfall, when every branch cushions the sound of footsteps.",
    ),
    Door(
        day=12,
        suid="b0e94c712f5d",
        title="Halfway to Christmas Eve",
        subtitle="December 12 — Twelve days down, twelve to go",
        content="You have reached the midpoint of the Advent Calendar! Treat yourself to a slow evening by the fire.",
    ),
    Door(
        day=13,
        suid="4a7d18f3b6e9",
        title="Festival of Light",
        subtitle="December 13 — St. Lucia's Day",
        content="Saffron buns (Lussebullar) and glowing processions bring light to one of the darkest nights of the year.",
    ),
    Door(
        day=14,
        suid="d832c509e17a",
        title="Mulled Cider",
        subtitle="December 14 — Simmering spices",
        content="Simmer apple cider with orange peel, star anise, and a cinnamon stick for an instant cozy atmosphere.",
    ),
    Door(
        day=15,
        suid="2c96f0b4a83e",
        title="Handwritten Cards",
        subtitle="December 15 — Sending warm wishes",
        content="Write a short handwritten note to someone you haven't spoken to in a while—it's still in time for the holiday post.",
    ),
    Door(
        day=16,
        suid="7e14a9d5c06b",
        title="Fireside Reading",
        subtitle="December 16 — A chapter under a blanket",
        content="Pick up that book waiting on your nightstand and read a chapter with a cup of herbal tea.",
    ),
    Door(
        day=17,
        suid="f5b820e63d41",
        title="Vanilla Crescents",
        subtitle="December 17 — Vanillekipferl",
        content="Buttery walnut shortbread crescents rolled in vanilla sugar while still warm from the oven.",
    ),
    Door(
        day=18,
        suid="0a63d4f98b27",
        title="Twinkling Wreath",
        subtitle="December 18 — Evergreen & berries",
        content="Fresh fir boughs interwoven with holly berries and fairy lights welcome every guest at the front door.",
    ),
    Door(
        day=19,
        suid="c749e1a25f80",
        title="Starry Night Sky",
        subtitle="December 19 — Orion Rising",
        content="Clear winter nights offer the sharpest view of Orion and the Pleiades. Step out for a quick look at the stars.",
    ),
    Door(
        day=20,
        suid="8d10b6c47e93",
        title="Wrapping Paper & Ribbon",
        subtitle="December 20 — Thoughtful packages",
        content="Brown kraft paper, twine, and a sprig of rosemary turn even the simplest gift into a work of art.",
    ),
    Door(
        day=21,
        suid="3f68a2e1d95c",
        title="Winter Solstice",
        subtitle="December 21 — The longest night",
        content="Tonight is the Winter Solstice. From tomorrow onward, every single day brings back a little more daylight.",
    ),
    Door(
        day=22,
        suid="a1c579f04e82",
        title="Nutcracker Suite",
        subtitle="December 22 — Tchaikovsky's magic",
        content="From the Dance of the Sugar Plum Fairy to the Waltz of the Flowers, let the classic score set the holiday mood.",
    ),
    Door(
        day=23,
        suid="5e92d3b71a46",
        title="The Night Before",
        subtitle="December 23 — Calm anticipation",
        content="The shopping is done, the lights are dimmed, and the house settles into quiet anticipation for tomorrow.",
    ),
    Door(
        day=24,
        suid="e047f8c39b15",
        title="Christmas Eve",
        subtitle="December 24 — The final door",
        content="Congratulations on opening all 24 doors! Wishing you peace, joy, warmth, and wonderful company this holiday season.",
    ),
)

DOORS_BY_SUID: dict[str, Door] = {door.suid: door for door in DOORS}
DOORS_BY_DAY: dict[int, Door] = {door.day: door for door in DOORS}


def get_door_by_suid(suid: str) -> Door | None:
    return DOORS_BY_SUID.get(suid)


def get_door_by_day(day: int) -> Door | None:
    return DOORS_BY_DAY.get(day)
