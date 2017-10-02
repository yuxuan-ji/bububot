import unittest
from unittest.mock import patch
from SVScraper import SVScraper
import asyncio
import aiohttp


class TestSVScraper(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print('setupClass')
        
    @classmethod
    def tearDownClass(cls):
        print('teardownClass')
        
    def setUp(self):
        print('setUp')
    
    def tearDown(self):
        print('tearDown\n')

    def test_filter(self):
        print('test_filter')
        filtered = SVScraper._filter(['Gabriel','Gabriel','Bob'], ['0.06%', '0.06%', '0.06%'])
        self.assertEqual(filtered, (['Gabriel', 'Bob'], [[0.06, 0.06], [0.06, 0]]))

    def test_getCardUrl(self):
        print('test_getCardUrl')
        cardName = SVScraper._getCardUrl('Baalt, King of the Elves')
        self.assertEqual(cardName, 'https://shadowverse.gamepress.gg/card/baalt-king-elves')

if __name__ == '__main__':
    unittest.main()