# CryptoDataExport
Export your data from popular cryptocurrency exchanges as CSV files

# Usage

Export your trades and balances from kraken using the provided API Key and Secret (get this from Kraken), between Oct. 19th 2018 (inclusive) and Oct. 20th 2018 (exclusive) using UTC time boundaries:

    python3 download.py --exchange kraken --apiKey "" --apiSecret "" --pair XLM/USD --start 2018-10-19 --end 2018-10-20

Export your trades and balances from kraken using the provided API Key and Secret (get this from Kraken), between Oct. 19th 2018 (inclusive) and Oct. 20th 2018 (exclusive) using PST time boundaries:

    python3 download.py --exchange kraken --apiKey "" --apiSecret "" --pair XLM/USD --start 2018-10-19 --end 2018-10-20 --pst
