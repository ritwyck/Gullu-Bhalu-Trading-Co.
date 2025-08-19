import os
from Logic.Strategy.volatility import load_data


def get_stock_files(data_folder):
    return [f for f in os.listdir(data_folder) if f.endswith(".csv")]


def get_symbols(files):
    return [os.path.splitext(f)[0] for f in files]


def load_symbol_data(data_folder, symbol, files):
    file_match = [f for f in files if f.startswith(symbol)]
    if not file_match:
        return None
    # Fix: file_match is a list; we want the first matching file
    return load_data(os.path.join(data_folder, file_match[0]))
