import aiohttp
from bs4 import BeautifulSoup as BS
import json
import asyncio
import time


class SVScraper:

    @staticmethod
    async def _getCardsInfo(session: aiohttp.ClientSession, url):
            '''Coroutine. Returns tuple(gen(cardNames), gen(cardProbabilities))'''
            async with session.get(url) as response:
                pageBS = BS(await response.text(), 'html.parser')
                containers = [container.text for container in pageBS.findAll('td')]  # The Card Info is contained in the text of a td tag
                # Names are contained in the even-numbered indexes td tags
                # Probabilities are in the odd-numbered indexes td tags
                # We don't want to use containers[::2] and containers[1::2]
                # list slicing here because they create shallow copies
                containers_length = len(containers)
                cardNames = (containers[i] for i in range(0, containers_length, 2))
                cardProbabilities = (containers[i] for i in range(1, containers_length, 2))
                return cardNames, cardProbabilities

    @staticmethod
    def _filter(cardNames, cardProbabilities):
        '''Returns a tuple of(dict_keys([names,...]), dict_values([[%1, %2],...]))
        that are iterable'''
        # NOTE: The website has duplicate of certain card names because
        # the 8th card drawn in the pack contains no Bronze cards.
        # To accomodate this, we'll create a dict {name:[%]} where:
        # [%][0] = % for the first seven draws
        # [%][1] = % for the 8th draw
        filtered = {}
        for name, probability in zip(cardNames, cardProbabilities):
            
            value = filtered.get(name, [0, 0])
            
            # First occurance of the name, we create the % for the first seven draws:
            if not value[0]:
                value[0] = (float(probability[:-1]))  # remove the % char at the end of the probability string
            
            # If it occurs another time, we create the % for the 8th draw.
            # Note: Bronze card won't appear twice, thus their % will stay as 0.
            else:
                value[1] = (float(probability[:-1]))
            # Logically, %2 (i.e. % of the 8th draw) should be bigger than %1. Thus
            # we should switch the two elements around if theyre not sorted.
            # However, we should also make sure that the switch does not happen if
            # %2 = 0, since that is the case when the card is of Bronze rarity.
            if (value[1] != 0) and (value[0] > value[1]):
                value[0], value[1] = value[1], value[0]
            
            filtered[name] = value
        
        return filtered.keys(), filtered.values()

    @staticmethod
    def _getCardUrl(cardName):
        '''Returns the corresponding gamepress url of a card'''
        url = 'https://shadowverse.gamepress.gg/card/'
        nameFixed = cardName.lower().replace(',', "").replace("'", "").replace(".", " ").split()
        nameFixed = list(filter(lambda x: x not in ['at', 'with', 'in', 'of', 'the', 'to', 'into', 'from'], nameFixed))
        nameFixed = "-".join(nameFixed)
        url = url + nameFixed
        return url

    @staticmethod
    async def _getImgUrl(session: aiohttp.ClientSession, url):
        '''Coroutine. Returns the corresponding gamepress image url of a card'''
        async with session.get(url) as response:
            try:
                pageBS = BS(await response.text(), 'html.parser')
                containers = pageBS.findAll('div', {'class': 'unevolved-section-image'})
                if not containers:
                    containers = pageBS.findAll('div', {'class': 'non-follower-image'})
                imgRelPath = str(containers[0].img['src'])
                return "https://shadowverse.gamepress.gg" + imgRelPath
            except:
                # Animated Daria art for unavailable images
                print('[Not found] : ' + url)
                return 'https://shadowverse.gamepress.gg/sites/shadowverse/files/styles/medium/public/2016-12/Daria%2C%20Dimensional%20Witch%20Evolved_0.png?itok=q0s7W05W'

    @staticmethod
    def _writeJsonFile(CardList, packID):
        '''Writes the card list to a file packID.txt in json format'''
        jsonCardsList = json.dumps(CardList)
        with open('./data/SV' + str(packID) + '.txt', 'w') as f:
            f.write(jsonCardsList)

    @classmethod
    async def getData(cls, packID):
        '''Gets the data from the ID and writes it to a file as a list of json
        objects'''
        async with aiohttp.ClientSession() as session:  # 'async with' is needed because closing the session is an asynchronous operation

            url = "https://shadowverse.com/drawrates/?pack_id=" + str(packID)

            # Create two lists containing names and probabilities respectively
            cardNames, cardProbabilities = await cls._getCardsInfo(session=session, url=url)
            
            # The website has duplicate of certain card names because the 8th card drawn in the pack contains no Bronze cards
            filteredNames, filteredProbabilities = cls._filter(cardNames, cardProbabilities)

            # Create a list of gamepress.gg urls:
            cardUrls = [cls._getCardUrl(name) for name in filteredNames]

            # Create a list of gamepress.gg image urls:
            imgUrls = [await cls._getImgUrl(session=session, url=url) for url in cardUrls]

            # Create a list of json objects and write it to a file:
            CardList = []
            for data in zip(filteredNames, filteredProbabilities, cardUrls, imgUrls):
                jsonCardInfo = {"name": data[0],
                                "%": data[1],
                                "url": data[2],
                                "img": data[3]
                                }
                CardList.append(jsonCardInfo)
            
            cls._writeJsonFile(CardList, packID)
            

if __name__ == '__main__':
    # Gathering the data:
    loop = asyncio.get_event_loop()
    t0 = time.time()

    # Do all:
    # tasks = [loop.create_task(SVScraper.getData(i)) for i in range(10001, 10008)]
    # loop.run_until_complete(asyncio.gather(*tasks))
    
    # Manually one at a time:
    # loop.run_until_complete(SVScraper.getData(10001)) #std
    # loop.run_until_complete(SVScraper.getData(10002)) #dark
    # loop.run_until_complete(SVScraper.getData(10003)) #baha
    # loop.run_until_complete(SVScraper.getData(10004)) #temp
    # loop.run_until_complete(SVScraper.getData(10005)) #wond
    # loop.run_until_complete(SVScraper.getData(10006)) #star
    loop.run_until_complete(SVScraper.getData(10007)) #chrono

    loop.close()
    t1 = time.time()
    print('Took {:1f} seconds'.format(t1 - t0))