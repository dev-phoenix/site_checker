# site_checker
It's allows you to check is site available and notice by sms if is not

### start:
```
git clone https://github.com/dev-phoenix/site_checker.git
cd checker
```

### create file `.env` and fill variables:
```
SMSC_LOGIN = ""
SMSC_PASSWORD = ""
```

### check is site status = 200 ad send sms if not:
```sh
python3 check_site.py
```

### look current sites statuses and last check date:
```sh
python3 check_db.py 
```