"""
The database connection class
"""

import logging

import pandas as pd
import sqlalchemy as sal
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
import wxconfig as cfg

from algotrader.model.base import Base, DataSource, DataSourceSymbol, Symbol


class Database:
    """
    A class to handle applications interaction with its database
    """

    connected = False  # Has the connection to the database been established?

    __engine = None  # SQLAlchemy engine
    __log = None

    def __init__(self, dialect: str, host: str, database: str, username: str, password: str) -> None:
        """
        Constructs the database instance
        :param dialect:
        :param host:
        :param database:
        :param username:
        :param password:
        """
        # Create logger
        self.__log = logging.getLogger(__name__)

        # Create engine and test
        self.__engine = sal.create_engine(f'{dialect}://{username}:{password}@{host}/{database}')

        # Test
        try:
            con = self.__engine.connect()
            con.close()
            self.connected = True
        except SQLAlchemyError as ex:
            self.__log.warning(f"Could not connect to database. Application cannot be used. {ex}")

        # Configure the database, creating any tables that don't already exist and populating DataSources
        self.__configure_db()

    def get_datasource_symbols(self) -> pd.DataFrame:
        """
        Returns a dataframe containing all symbols for the specified datasources
        :return: Dataframe containing all symbols for all datasources
        """
        data = None
        if self.connected:
            try:
                con = self.__engine.connect()
                data = pd.read_sql_table(table_name=DataSourceSymbol.__tablename__, con=con)
                con.close()
            except SQLAlchemyError as ex:
                self.__log.warning(f"Could not retrieve data from database. {ex}")

        return data

    def update_datasource_symbols(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Updates datasource_symbols table with provided dataframe. Appends new rows and updates modified rows.
        :param: A dataframe containing all symbols for all databases
        :return: Updated dataframe included generated primary keys
        """
        new_records = data[data['id'].isna()].drop(labels='id', axis=1)  # For insert. Remove ids
        other_records = data[~data['id'].isna()]  # For update
        new_symbols = [Symbol(name=symbol_name) for symbol_name in new_records['symbol_name'] if symbol_name not in
                       other_records['symbol_name']]

        if self.connected:
            with Session(self.__engine) as session:
                # Bulk insert new symbols. Flush and commit before we insert the new DataSourceSymbol's
                session.add_all(new_symbols)
                session.flush()
                session.commit()

                # Bulk insert datasource_symbols and bulk update existing datasource_symbols
                session.bulk_insert_mappings(DataSourceSymbol, new_records.to_dict(orient='records'))
                session.bulk_update_mappings(DataSourceSymbol, other_records.to_dict(orient='records'))

                # Flush the session and commit
                session.flush()
                session.commit()

        return self.get_datasource_symbols()

    def __configure_db(self) -> None:
        """
        Creates all required tables in the database if they don't already exist. Updates DataSource table to ensure that
        it contains a record for every configured DataSource.
        :return:
        """
        if self.connected:
            Base.metadata.create_all(self.__engine)

            # Get all datasources from db and get all from config. In db, create any from config that don't exist in db.
            config_datasources = cfg.Config().get('datasources')
            with Session(self.__engine) as session:
                # Get all db datasource names
                datasources = session.query(DataSource).all()
                db_ds_names = []
                for ds in datasources:
                    db_ds_names.append(ds.name)

                for ds in config_datasources:
                    # If it doesn't exist in datasources then create it.
                    if ds not in db_ds_names:
                        new_db_ds = DataSource(name=ds)
                        session.add(new_db_ds)

                # Flush the session and commit
                session.flush()
                session.commit()




