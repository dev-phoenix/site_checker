# check_site.py
#
# Author: WSD
# Author site: https://homdy.ru
# Author on kwork.ru: https://kwork.ru/user/phoenix_way
# Created: 2025.06.14

import sqlite3
import requests
from datetime import datetime as dt

from smsc_api import *

# ==============================

# Список проверяемых сатов:
urls = []
urls.append('https://ezdy.ru/')
urls.append('https://chus-info.ru/')

# ==============================

# Имя базы, в которой хранятся данные
db_name = "site_checker.db"


def _print(*args, **kwargs):
    # if no debug
    if 10:
        return 
    print(*args, **kwargs)

con = sqlite3.connect(db_name)
cur = con.cursor()
try:
    cur.execute("CREATE TABLE site_status(url, status, time_check, time_change, time_ok, time_fail)")
except Exception as e:
    # _print(e)
    ...

status_changed = []
ids_changed = []
num = -1
for url in urls:
    num += 1
    _print()
    _print('='*10)
    _print(url)
    time = '{:%s}'.format(dt.now())
    time_ok = time
    time_fail = time

    query = f"select * from site_status where url = '{url}' "
    res = cur.execute(query)
    url_data = res.fetchone()
    
    last_status = '-1'
    last_time_check = time
    last_time_change = time
    current_status = '-1'
    
    query_create = "INSERT INTO site_status VALUES ('{url}', '{status}', '{time}', '{time_changed}', '{time_ok}', '{time_fail}')"

    query_update_ok = "update site_status set status = '{status}', time_check = '{time}', time_ok = '{time_ok}' where url = '{url}'"
    query_update_ok_changed = "update site_status set status = '{status}', time_check = '{time}', time_change = '{time_changed}', time_ok = '{time_ok}' where url = '{url}'"

    query_update_fail = "update site_status set status = '{status}', time_check = '{time}', time_fail = '{time_fail}' where url = '{url}'"
    query_update_fail_changed = "update site_status set status = '{status}', time_check = '{time}', time_change = '{time_changed}', time_fail = '{time_fail}' where url = '{url}'"



    is_new = True
    if url_data:
        is_new = False
        last_status = url_data[1]
        last_time_check = url_data[2]
        last_time_change = url_data[3]

        _print(f' row {url} is_new={is_new} last_status={last_status} last_time_check={last_time_check} last_time_change={last_time_change}')

    status = '-1'
    try:
        Response = 'no result'
        Response = requests.get(url)
        status = str(Response.status_code)
        mess = f'status: {status}'
        _print(mess)
    except Exception as e:
        _print(Response)
        _print(e)
        status = 'fail'

    # if new record
    if status == '200':
        time_fail = 0
    else:
        time_ok = 0
    
    _print()
    _print('='*5)
    _print(url, status, type(status))

    _status_changed = False
    time_changed = 0
    if is_new:
        query = query_create
    else:
        if status == '200':
            query = query_update_ok
            if last_status != status:
                # _status_changed = True # only if fail
                time_changed = time
                query = query_update_ok_changed
        else:
            query = query_update_fail
            if last_status != status:
                _status_changed = True
                time_changed = time
                query = query_update_fail_changed

    # _status_changed = True # for test
    
    _print(f'{last_status} != {status}  >> {_status_changed}')

    _print(f' row 2 {url} is_new={is_new} new_status={status} last_time_check={last_time_check} last_time_change={last_time_change}')
    _print()
    # save resul to sqlite
    _print(query)
    query = query.format( status=status, time=time, time_changed = time_changed, time_ok = time_ok, time_fail = time_fail, url=url)
    _print(query)
    cur.execute(query)
    con.commit()

    # check is status changed
    if _status_changed:
        ids_changed.append(str(num))
        _status = {"url": url, "status": str(status)}
        status_changed.append(_status)

# check if have changesd and send sms
if status_changed:
    # build message

    count_changed = len(status_changed)
    fist_site_name = status_changed[0]["url"]
    status = status_changed[0]["status"]
    ids = ''

    if status == '200':
        status = f"работает"
    else: 
        status = f"не работает"

    if count_changed > 1:
        _print(ids_changed)
        ids = ','.join(ids_changed)
        ids = f' [{ids}]'
        count_changed = f"Обновились {count_changed} сайтов: {ids}"
    else:
        count_changed = ''
    
    mess = f"Сайт {fist_site_name} {status}. {count_changed}"

    # send message
    _print()
    _print('*'*10)
    _print(mess)

    phonenum = '79124904314'
    sms_text = mess
    smsc = SMSC()
    r = smsc.send_sms(phonenum, sms_text) # , sender=sender)
    # Сообщение отправлено успешно. ID: 5708, всего SMS: 1, стоимость: 0, баланс: 116.392