import argparse
import sys
import ccxt
import json
import csv

def inputArgs():
    parser = argparse.ArgumentParser(description='Download Crypto Data')
    parser.add_argument('--exchange', default=None, help='exchange name (kraken, binance, etc.)')
    parser.add_argument('--apiKey', default=None, help='API key')
    parser.add_argument('--apiSecret', default=None, help='API secret')
    parser.add_argument("--start", default=None, help='start date (inclusive), example: 2018-10-19')
    parser.add_argument('--end', default=None, help='end date (exclusive), example: 2018-10-20')
    parser.add_argument('--pst', action='store_true', default=False, help='use the PST timezone')
    parser.add_argument('--limit', type=int, default=1000, help='max number of trades to fetch on every API request')
    parser.add_argument('-v', action='store_true', default=False, help='verbose exchange logging')
    args = parser.parse_args()

    if not args.exchange or not args.apiKey or not args.apiSecret or not args.start or not args.end:
        parser.print_help()
        sys.exit(1)
    return args

def makeExchange(name, apiKey, apiSecret, verbose=False):
    if name == "kraken":
        exchange = ccxt.kraken({
            'apiKey': apiKey,
            'secret': apiSecret,
            'verbose': verbose,
        })
    else:
        raise Exception("invalid exchange argument", name)
    return exchange

def convertTimebounds(exchange, start, end, usePst):
    timeStr = 'T00:00:00.000Z'
    if usePst:
        # use +0800 instead of -0800 because kraken offsets this in a weird manner
        timeStr = 'T00:00:00.000+0800'

    startInt = exchange.parse8601(start + timeStr)
    endInt = exchange.parse8601(end + timeStr)

    if startInt >= endInt:
        raise Exception("invalid time bounds, end date needs to be greater than start date")
    return startInt, endInt

def main():
    symbol="XLM/USD"
    args = inputArgs()
    exchange = makeExchange(args.exchange, args.apiKey, args.apiSecret, args.v)
    since, endTimestampExclusive = convertTimebounds(exchange, args.start, args.end, args.pst)
    tzStr = 'UTC'
    if args.pst:
        tzStr = 'PST'
    print('using', tzStr, 'timezone')
    filename = args.exchange + '_' + args.start + '_' + args.end + '_' + tzStr + '_trades.csv'

    if not exchange.has['fetchTrades']:
        raise Exception("function missing")

    processTrades(exchange, symbol, filename, since, endTimestampExclusive, args.limit)
    print('done')

def processTrades(exchange, symbol, filename, since, endTimestampExclusive, limit):
    with open(filename, mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['currency_pair', 'ID', 'timestamp', 'side', 'price', 'amount', 'fee', 'fee_currency', 'cost'])

        while since < endTimestampExclusive:
            print('fetching the next', limit, 'trades since', since)
            # returns the trades in sorted order
            trades_json = exchange.fetch_my_trades(symbol=symbol, since=since, limit=limit, params={})
            if len(trades_json) == 0:
                break

            for trade in trades_json:
                if trade['timestamp'] >= endTimestampExclusive:
                    break

                # write directly for now instead of introducing batching logic until that is needed
                csv_writer.writerow([trade['symbol'], trade['id'], trade['timestamp'], trade['side'], trade['price'], trade['amount'], trade['fee']['cost'], trade['fee']['currency'], trade['cost']])

            # add 1 to so we don't repeat trades
            since = trades_json[-1]['timestamp'] + 1

if __name__ == "__main__":
    main()
