import wxconfig as cfg
import unittest

from unittest.mock import patch

import definitions
import algotrader.connections.ds as ds


class TestDataSource(unittest.TestCase):
    def setUp(self) -> None:
        # Setup config
        cfg.Config().load(fr"{definitions.ROOT_DIR}\tests\testconfig.yaml")

    def test_instance(self):
        # Test that we get an instance of MetaTrader5 datasource from its configured name mt5
        datasource = ds.DataSource.instance('mt5')
        self.assertTrue(isinstance(datasource, ds.MT5DataSource), "DataSource should be an instance of MetaTrader5")


class Symbol:
    """ A Mock symbol class returned to test MT5 as MT5 returns Symbol object with name and visible properties"""
    name = None
    visible = None

    def __init__(self, name, visible):
        self.name = name
        self.visible = visible


class TestMT5DataSource(unittest.TestCase):
    __mock_symbols = [Symbol(name='SYMBOL1', visible=True),
                      Symbol(name='SYMBOL2', visible=True),
                      Symbol(name='SYMBOL3', visible=False),
                      Symbol(name='SYMBOL4', visible=True),
                      Symbol(name='SYMBOL5', visible=True)]

    def setUp(self) -> None:
        # Setup config
        cfg.Config().load(fr"{definitions.ROOT_DIR}\tests\testconfig.yaml")

    @patch('algotrader.connections.ds.MetaTrader5')
    def test_get_symbols(self, mock):
        # Mock return values
        mock.symbols_get.return_value = self.__mock_symbols
        mock.symbols_total.return_value = len(self.__mock_symbols)

        # Get the MT5 datasource
        datasource = ds.DataSource.instance('mt5')

        # Call get_symbols
        symbols = datasource.get_symbols()

        # There should be 4 as 1 is not visible in market watch
        self.assertTrue(len(symbols) == 4, "There should be 4 symbols. 5 Returned from MT5, 1 of which is not visible.")

