# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401
# isort: skip_file
# --- Do not remove these libs ---
import numpy as np  # noqa
import pandas as pd  # noqa
from pandas import DataFrame
from typing import Optional, Union

from freqtrade.strategy import (
    BooleanParameter,
    CategoricalParameter,
    DecimalParameter,
    IStrategy,
    IntParameter,
)

# --------------------------------
# Add your lib to import here
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib


# This class is a sample. Feel free to customize it.
import logging
from functools import reduce
import talib.abstract as ta
from pandas import DataFrame
from freqtrade.strategy import IStrategy, informative
from freqtrade.constants import DATETIME_PRINT_FORMAT
import numpy as np

logger = logging.getLogger(__name__)

class RLStrategy(IStrategy):
    process_only_new_candles = True
    #stoploss = -0.05
    use_exit_signal = True
    # this is the maximum period fed to talib (timeframe independent)
    startup_candle_count: int = 240
    stoploss = -0.10
    can_short = True
    timeframe = "1m"

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe = self.freqai.start(dataframe, metadata, self)
        return dataframe
    

    def populate_entry_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        
        logger.debug(f"populate_entry_trend start: {df.iloc[0]['date'].strftime(DATETIME_PRINT_FORMAT)}")
        logger.debug(f"populate_entry_trend stop: {df.iloc[-1]['date'].strftime(DATETIME_PRINT_FORMAT)}")

        enter_long_conditions = [df["do_predict"] == 1, df["&-action"] == 1]

        if enter_long_conditions:
            df.loc[
                reduce(lambda x, y: x & y, enter_long_conditions), ["enter_long", "enter_tag"]
            ] = (1, "long")

        enter_short_conditions = [df["do_predict"] == 1, df["&-action"] == 3]

        if enter_short_conditions:
            df.loc[
                reduce(lambda x, y: x & y, enter_short_conditions), ["enter_short", "enter_tag"]
            ] = (1, "short")
        
        return df


    def populate_exit_trend(self, df: DataFrame, metadata: dict) -> DataFrame:
        
        logger.debug(f"populate_exit_trend start: {df.iloc[0]['date'].strftime(DATETIME_PRINT_FORMAT)}")
        logger.debug(f"populate_exit_trend stop: {df.iloc[-1]['date'].strftime(DATETIME_PRINT_FORMAT)}")

        exit_long_conditions = [df["do_predict"] == 1, df["&-action"] == 2]
        if exit_long_conditions:
            df.loc[reduce(lambda x, y: x & y, exit_long_conditions), "exit_long"] = 1

        exit_short_conditions = [df["do_predict"] == 1, df["&-action"] == 4]
        if exit_short_conditions:
            df.loc[reduce(lambda x, y: x & y, exit_short_conditions), "exit_short"] = 1

        return df
    

    def feature_engineering_expand_all(self, dataframe: DataFrame, period, **kwargs) -> DataFrame:
        dataframe["%-ema-period"] = ta.EMA(dataframe, timeperiod=period)
        
        logger.debug(f"feature_engineering_expand_all tf/period: ")
        logger.debug(f"feature_engineering_expand_all {kwargs['metadata']['tf']}/{period} start: {dataframe.iloc[0]['date'].strftime(DATETIME_PRINT_FORMAT)}")
        logger.debug(f"feature_engineering_expand_all {kwargs['metadata']['tf']}/{period} end: {dataframe.iloc[-1]['date'].strftime(DATETIME_PRINT_FORMAT)}")

        return dataframe
    

    def feature_engineering_expand_basic(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        dataframe["%-pct-change"] = dataframe["close"].pct_change()
        dataframe["%-raw_volume"] = dataframe["volume"]
        dataframe["%-raw_price"] = dataframe["close"]
        return dataframe
    

    def feature_engineering_standard(self, dataframe: DataFrame, **kwargs) -> DataFrame:
        dataframe[f"%-raw_close"] = dataframe["close"]
        dataframe[f"%-raw_open"] = dataframe["open"]
        dataframe[f"%-raw_high"] = dataframe["high"]
        dataframe[f"%-raw_low"] = dataframe["low"]
        dataframe["%-day_of_week"] = (dataframe["date"].dt.dayofweek + 1) / 7
        dataframe["%-hour_of_day"] = (dataframe["date"].dt.hour + 1) / 25

        return dataframe
    

    def set_freqai_targets(self, dataframe, **kwargs) -> DataFrame:
        dataframe["&-action"] = 0
        
        logger.debug(f"set_freqai_targets start: {dataframe.iloc[0]['date'].strftime(DATETIME_PRINT_FORMAT)}")
        logger.debug(f"set_freqai_targets stop: {dataframe.iloc[-1]['date'].strftime(DATETIME_PRINT_FORMAT)}")

        return dataframe
