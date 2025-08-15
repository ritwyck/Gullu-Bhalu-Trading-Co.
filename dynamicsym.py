import yfinance as yf
import tkinter as tk
import pandas as pd
import numpy as np
from tkinter import messagebox, Listbox, Scrollbar


def search_symbols(query):
    try:
        results = yf.Ticker(query)  # attempt to create ticker
        # If valid, return symbol as suggestion
        return [query.upper()]
    except:
        return []


def fetch_ohlc(symbol):
    try:
        df = yf.download(symbol, period="1mo", interval="1d")
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if df.empty:
            messagebox.showerror("Error", f"No data for {symbol}")
        else:
            print(df[['Open', 'High', 'Low', 'Close']].tail())
            messagebox.showinfo(
                "Success", f"Fetched OHLC for {symbol} (see console).")
    except Exception as e:
        messagebox.showerror("Error", f"Failed: {e}")


def on_keyrelease(event):
    value = entry.get()
    if value == '':
        listbox_for_suggestions.delete(0, tk.END)
    else:
        suggestions = search_symbols(value)
        listbox_for_suggestions.delete(0, tk.END)
        for s in suggestions:
            listbox_for_suggestions.insert(tk.END, s)


def on_select(event):
    widget = event.widget
    index = widget.curselection()[0]
    value = widget.get(index)
    entry.delete(0, tk.END)
    entry.insert(0, value)
    listbox_for_suggestions.delete(0, tk.END)
    fetch_ohlc(value)


# Tkinter UI
root = tk.Tk()
root.title("Yahoo Finance OHLC Fetcher")

entry = tk.Entry(root, width=30)
entry.pack()
entry.bind("<KeyRelease>", on_keyrelease)

listbox_for_suggestions = Listbox(root, width=30, height=5)
listbox_for_suggestions.pack()
listbox_for_suggestions.bind("<<ListboxSelect>>", on_select)

root.mainloop()
