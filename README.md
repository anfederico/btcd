# btcd
Web scraper to grab bitcoin dominance history  

Specify how many of the top coins (limit = 2000) to include in the calculation and provide a free API key from [https://coinmarketcap.com/api/](https://coinmarketcap.com/api/).  If your connection is interrupted, the program will pick up where it left off.  *Please only use the provided key for initial testing ;)*

```bash
git clone https://github.com/anfederico/btcd
cd btcd
python3 scrape.py \
        top=500 \
        apikey=8fd0b0e4-a44e-4311-8468-ecaf68a810db

tail BTCD.csv
```

```
date,BTC,ALT,BTCD
2019-08-07,213330426789.0,95066098906.0,0.691740694251468
2019-08-08,213788089212.0,94073760844.0,0.6944286509455848
2019-08-09,211961319133.0,90185914523.0,0.7015166631454972
2019-08-10,202890020455.0,90107325891.0,0.6924636792287108
2019-08-11,205941632235.0,93019986922.0,0.6888564251682405
2019-08-12,203441494985.0,91529416570.0,0.6897001942073413
```
**If you want to refresh the data in the future, simply delete the cache.**