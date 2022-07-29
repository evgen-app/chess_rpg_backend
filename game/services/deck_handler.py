import random

from game.models import Deck, Player, HeroTypes, Hero, HeroInDeck


def create_first_deck(player: Player):
    deck = Deck.objects.create(player=player)
    positions = []

    for x in range(1, 9):
        for y in range(1, 3):
            positions.append((x, y))
    positions.remove((4, 1))
    positions.remove((5, 1))
    random.shuffle(positions)

    types = ["KING", "WIZARD"] + ["ARCHER" for _ in range(4)] + ["WARRIOR" for _ in range(6)]

    for _ in range(4):
        t = random.choice(HeroTypes.choices[:3])[0]
        if t == "WIZARD" and types.count("WIZARD") > 1:
            t = random.choice(HeroTypes.choices[:2])[0]
        types.append(t)

    counter = 0
    for t in types:
        hero = Hero()
        hero.player = player
        hero.type = t

        # set random position on deck for heroes
        if t == "KING":
            pos_x = 5
            pos_y = 1
        elif t == "WIZARD":
            pos_x = 4
            pos_y = 1
        else:
            pos_x = positions[counter][0]
            pos_y = positions[counter][1]

            counter += 1

        hero.health = random.randint(0, 10)
        hero.attack = random.randint(0, 10)
        hero.speed = random.randint(0, 10)

        hero.save()
        HeroInDeck.objects.create(deck=deck, hero=hero, x=pos_x, y=pos_y)
