import random
import json
import os


class Card:
    def __init__(self, name=None, url=None, img=None, probabilities=None):
        self.name = name
        self.url = url
        self.img = img
        self.probabilities = probabilities

    def __repr__(self):
        return "Card({}, {}, {}, {})".format(self.name, self.url, self.img, self.probabilities)

    def __str__(self):
        return "{}".format(self.name)


class PackSimulator:

    def __init__(self, packID):
        '''Initializes a PackSimulator object
        packID = ID of the expansion
        ex: SV10001 for Shadowverse's Standard Expansion
        '''
        self.packID = str(packID)

    @property
    def path(self):
        '''Path of the data file'''
        script_dir = os.path.dirname(__file__)
        rel_path = "data/" + self.packID + '.txt'
        return os.path.join(script_dir, rel_path)
        
    @property
    def parsed(self):
        '''Returns a list containing json objects(dicts)'''
        with open(self.path, 'r') as f:
            return json.loads(f.read())

    def openPack(self, amount=0, specialDraws=0):
        '''Returns a list of Card objects'''
        # Gathering the card names and probabilities:
        cards = []
        cardProbabilities = []
        specialProbabilities = []
        amount = amount - specialDraws

        for jsonObj in self.parsed:
            card = Card()
            card.name = jsonObj['name']
            card.url = jsonObj['url']
            card.img = jsonObj['img']
            card.probabilities = jsonObj['%']
            cardProbabilities.append(jsonObj['%'][0])
            if specialDraws:
                specialProbabilities.append(jsonObj['%'][1:])  # Append all the 'special' % (lists)
            cards.append(card)

        # Since specialProbabilities is now a list of lists in the form [[1,4,...],[2,5,...],[3,6,...],...],
        # let's reformat it to [(1,2,3,...),(4,5,6,...),...] where each tuple correspond to one
        # set of 'special probabilities':
        specialProbabilities = list(zip(*specialProbabilities))

        myPack = random.choices(cards, weights=cardProbabilities, k=amount)

        # Open x amount of special draws, associated to their corresponding set of special probabilities
        for i in range(specialDraws):
            specialDraw = random.choices(cards, weights=specialProbabilities[i], k=1)
            myPack += specialDraw
        
        return myPack


if __name__ == '__main__':
    print([repr(card) for card in PackSimulator('SV10003').openPack(amount=8, specialDraws=1)])
