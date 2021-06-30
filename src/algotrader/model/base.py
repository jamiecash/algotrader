"""
The base datamodel for collecting price candles including Symbol and Candle
"""
from sqlalchemy import Column, Integer, String, Boolean, BigInteger, Numeric, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DataSource(Base):
    """
    A datasource to retrieve data from
    """
    __tablename__ = 'datasource'

    # The datasource key as defined in application config
    name = Column(String(20), primary_key=True)

    def __repr__(self):
        return f"DataSource(name={self.name})"


class Symbol(Base):
    """
    A financial Symbol. e.g. GBPUSD
    """
    __tablename__ = 'symbol'

    # Name of the symbol. Should be the industry standard name not datasoruce / broker specific name. Any datasoruce
    # specific name for the symbol will be specified in the DataSourceSymbol table.
    name = Column(String(20), primary_key=True)

    def __repr__(self):
        return f"Symbol(name={self.name})"


class DataSourceSymbol(Base):
    """
    The mapping between data sources and symbols, including any specific name for the symbol from the datasource and a
    flag to determine whether price data will be retrieved from that datasource for the symbol.
    """
    __tablename__ = 'datasource_symbol'

    id = Column(Integer, primary_key=True, autoincrement=True)

    datasource_name = Column(String(20), ForeignKey('datasource.name'))
    symbol_name = Column(String(20), ForeignKey('symbol.name'))

    # Flag to determine whether price data will be retrieved for this datasource / symbol combination
    retrieve_price_data = Column(Boolean)

    def __repr__(self):
        return f"DataSourceSymbol(id={self.id}, datasource_name={self.datasource_name}, symbol_name={self.symbol_name}, " \
               f"retrieve_price_data={self.retrieve_price_data})"


class Candle(Base):
    """
    1 Second OHLC candles for the Symbol retrieved from the DataSource
    """
    __tablename__ = 'candle'

    id = Column(BigInteger, primary_key=True)

    # The datasource that this was retrieved from and the symbol that it is for
    datasource_symbol_id = Column(Integer, ForeignKey('datasource_symbol.id'))

    # OHLC columns for bid and ask
    bid_open = Column(Numeric(12, 6))
    bid_high = Column(Numeric(12, 6))
    bid_low = Column(Numeric(12, 6))
    bid_close = Column(Numeric(12, 6))
    ask_open = Column(Numeric(12, 6))
    ask_high = Column(Numeric(12, 6))
    ask_low = Column(Numeric(12, 6))
    ask_close = Column(Numeric(12, 6))

    # Volume of ticks that made up candle
    volume = Column(Integer)

    def __repr__(self):
        return f"Candle(id={self.id}, datasource_symbol_id={self.datasource_symbol_id}, " \
               f"bid_open={self.bid_open}, bid_high={self.bid_high}, bid_low={self.bid_low}, " \
               f"bid_close={self.bid_close}, ask_open={self.ask_open}, ask_high={self.ask_high}, " \
               f"ask_low={self.ask_low}, ask_close={self.ask_close}, volume={self.volume})"


