"""
The DataSource interface and an implementation for MetaTrader5
"""

import abc
import importlib
import logging
import MetaTrader5
import wxconfig


class DataSource:
    """
    The interface for applications datasources
    """

    name = None  # The name of the datasource
    _params = None  # Connection params. Protected (_) as params will need to be accessed by subclasses.

    def __init__(self, name: str, params: dict) -> None:
        """
        Construct the connection and store the connection params
        :param params:
        """
        self.name = name
        self._params = params

    @staticmethod
    def instance(name: str):
        """
        Get the DataSource instance specified by the name. Class ana params configured in applications config.
        :param name:
        :return:
        """
        params = wxconfig.Config().get(f"datasources.{name}")
        fullclasspath = params['class']
        poslastdot = fullclasspath.rfind('.')
        modulename = fullclasspath[0:poslastdot]
        classname = fullclasspath[poslastdot + 1:]

        module = importlib.import_module(modulename)
        clazz = getattr(module, classname)

        return clazz(name, params)

    @staticmethod
    def all_instances():
        """
        Retruns a list of all DataSources
        :return:
        """
        all_ds_names = wxconfig.Config().get("datasources")

        all_datasources = []
        for ds_name in all_ds_names:
            all_datasources.append(DataSource.instance(ds_name))

        return all_datasources

    @abc.abstractmethod
    def get_symbols(self):
        """
        Returns list of symbol names from data source
        :return:
        """
        raise NotImplementedError


class MT5DataSource(DataSource):
    """
    MetaTrader 5 DataSource
    """
    def __init__(self, name, params):
        # Super
        DataSource.__init__(self, name=name, params=params)

        # Connect to MetaTrader5. Opens if not already open.

        # Logger
        self.__log = logging.getLogger(__name__)

        # Open MT5 and log error if it could not open
        if not MetaTrader5.initialize():
            self.__log.error("initialize() failed")
            MetaTrader5.shutdown()

        # Print connection status
        self.__log.debug(MetaTrader5.terminal_info())

        # Print data on MetaTrader 5 version
        self.__log.debug(MetaTrader5.version())

    def __del__(self):
        # shut down connection to the MetaTrader 5 terminal
        MetaTrader5.shutdown()

    def get_symbols(self):
        """
        Gets list of symbols from MT5
        :return: list of symbol names
        """

        all_symbols = MetaTrader5.symbols_get()

        # Are we returning MarketWatch symbols only
        market_watch_only = self._params['market_watch_only']

        # We are only returning the symbol names
        symbol_names = []

        # Iterate all symbols, and populate symbol names, taking into account visible flag if we are returning market
        # watch symbols only.
        for symbol in all_symbols:
            if market_watch_only is False or (market_watch_only is True and symbol.visible):
                symbol_names.append(symbol.name)

        # Log symbol counts
        total_symbols = MetaTrader5.symbols_total()
        num_selected_symbols = len(symbol_names)
        self.__log.debug(f"{num_selected_symbols} of {total_symbols} returned. market_watch_only={market_watch_only}.")

        return symbol_names
