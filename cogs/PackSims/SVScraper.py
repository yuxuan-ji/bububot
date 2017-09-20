import aiohttp
from bs4 import BeautifulSoup as BS
import json
import asyncio
import time


class SVScraper:

    @staticmethod
    async def getData(packID):
        '''Gets the data from the ID and writes it to a file as a list of json
        objects'''

        async def _getCardInfo(session: aiohttp.ClientSession, url):
            '''Coroutine. Returns tuple(list(cardNames), list(cardProbabilities))'''
            async with session.get(url) as response:
                pageBS = BS(await response.text(), 'html.parser')
                containers = [container.text for container in pageBS.findAll('td')]  # The Card Info is contained in the text of a td tag
                # Names are contained in the even-numbered indexes td tags
                # Probabilities are in the odd-numbered indexes td tags
                cardNames = containers[::2]
                cardProbabilities = containers[1::2]
                return cardNames, cardProbabilities

        def _filter(cardNames, cardProbabilities):
            '''Returns a tuple ((names,...), ([%1, %2],...))'''
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
            
            return list(filtered.keys()), list(filtered.values())

        def _getCardUrl(cardName):
            '''Returns the corresponding gamepress url of a card'''
            url = 'https://shadowverse.gamepress.gg/card/'
            nameFixed = cardName.lower().replace(',', "").replace("'", "").replace(".", " ").split()
            nameFixed = list(filter(lambda x: x not in ['at', 'with', 'in', 'of', 'the', 'to', 'into'], nameFixed))
            nameFixed = "-".join(nameFixed)
            url = url + nameFixed
            return url

        async def _getImgUrl(session: aiohttp.ClientSession, url):
            '''Coroutine. Returns the corresponding gamepress image url of a card'''
            async with session.get(url) as response:
                try:
                    pageBS = BS(await response.text(), 'html.parser')
                    containers = pageBS.findAll('section', {'id': 'content'})
                    imgRelPath = str(containers[0].img['src'])
                    return "https://shadowverse.gamepress.gg" + imgRelPath
                except:
                    return 'Unavailable image url'

        # START OF THE FUNCTION:
        with aiohttp.ClientSession() as session:

            url = "https://shadowverse.com/drawrates/?pack_id=" + str(packID)

            # Create two lists containing names and probabilities respectively
            cardNames, cardProbabilities = await _getCardInfo(session=session, url=url)
            
            # The website has duplicate of certain card names because the 8th card drawn in the pack contains no Bronze cards
            filteredNames, filteredProbabilities = _filter(cardNames, cardProbabilities)

            # Create a list of gamepress.gg urls:
            cardUrls = [_getCardUrl(name) for name in filteredNames]

            # Create a list of gamepress.gg image urls:
            imgUrls = [await _getImgUrl(session=session, url=url) for url in cardUrls]

            # Create a list of json objects and write it to a file:
            CardList = []
            for data in zip(filteredNames, filteredProbabilities, cardUrls, imgUrls):
                jsonCardInfo = {"name": data[0], "%": data[1], "url": data[2], "img": data[3]}
                CardList.append(jsonCardInfo)
    
            jsonCardsList = json.dumps(CardList)
    
            with open('./data/SV' + str(packID) + '.txt', 'w') as f:
                f.write(jsonCardsList)


if __name__ == '__main__':
    # Gathering the data:
    loop = asyncio.get_event_loop()
    t0 = time.time()
    # Do all:
    tasks = [loop.create_task(SVScraper.getData(i)) for i in range(10001, 10005)]
    loop.run_until_complete(asyncio.gather(*tasks))
    # Manually one at a time:
    # loop.run_until_complete(SVScraper.getData(10001))
    # loop.run_until_complete(SVScraper.getData(10002))
    # loop.run_until_complete(SVScraper.getData(10003))
    # loop.run_until_complete(SVScraper.getData(10004))
    # loop.run_until_complete(SVScraper.getData(10005))
    t1 = time.time()
    print('Took {:1f} seconds'.format(t1 - t0))