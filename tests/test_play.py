from play import Nine

def test_deal():
    game = Nine()
    game.deal()
    game2 = Nine()
    game2.deal()
    assert game.cards != game2.cards

