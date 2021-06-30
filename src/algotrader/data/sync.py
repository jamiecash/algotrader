"""
A module for synchronising data between datasources and the applications database
"""
from typing import List

import pandas as pd

from algotrader.connections.ds import DataSource
from algotrader.connections.db import Database


class Sync:
    """
    Copies all symbols from all datasources to applications database
    """
    @staticmethod
    def sync_symbols(datasources: List[DataSource], database: Database) -> pd.DataFrame:
        """
        Copies all symbols from specified datasources to the database where they don't already exist.
        :param datasources: A list of datasources
        :type datasources: list[DataSource]
        :param database: The database to populate
        :type database: Database
        :return: The updated dataframe of symbols
        """

        # Get the data from the database
        data = database.get_datasource_symbols()

        # Get all symbols from all datasources, and if they don't exist in the data, add them
        for ds in datasources:
            symbols = ds.get_symbols()

            for symbol in symbols:
                exists = len(data[(data['datasource_name'] == ds.name) & (data['symbol_name'] == symbol)]) > 0
                if not exists:
                    # Add. Exclude first column in column list as it is index
                    data = data.append(pd.DataFrame(data=[[ds.name, symbol, True]], columns=data.columns[1:]))

        # Update database
        data = database.update_datasource_symbols(data)

        return data

