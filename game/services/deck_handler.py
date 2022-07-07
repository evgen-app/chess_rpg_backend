import random

from game.models import Deck, Player, HeroTypes, Hero, HeroInDeck


def create_first_deck(player: Player):
    deck = Deck.objects.create(player=player)
    positions = [
        [None, None, None, None, None, None, None, None],
        [None, None, None, None, None, None, None, None],
    ]
    types = (
        ["KING"]
        + ["ARCHER" for _ in range(4)]
        + ["WARRIOR" for _ in range(6)]
        + ["WIZARD" for _ in range(2)]
        + [random.choice(HeroTypes.choices[:2])[0] for _ in range(3)]
    )
    for t in types:
        hero = Hero()
        hero.player = player
        hero.type = t

        # set random position on deck for heroes
        if t == "KING":
            pos_x = 4
            pos_y = 0
            positions[0][4] = hero
        else:
            pos_x = random.randint(0, 7)
            pos_y = random.randint(0, 1)
            while positions[pos_y][pos_x] is not None:
                pos_x = random.randint(0, 7)
                pos_y = random.randint(0, 1)

            positions[pos_y][pos_x] = hero

        hero.health = random.randint(0, 10)
        hero.attack = random.randint(0, 10)
        hero.speed = random.randint(0, 10)

        hero.save()
        HeroInDeck.objects.create(deck=deck, hero=hero, x=pos_x + 1, y=pos_y + 1)
