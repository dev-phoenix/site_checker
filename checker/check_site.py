# check_site.py
#
# Author: WSD
# Author site: https://homdy.ru
# Author on kwork.ru: https://kwork.ru/user/phoenix_way
# Created: 2025.06.14

"""
It's allows you to check is site available and notice by sms if is not
"""

import os
import sqlite3
import requests
from datetime import datetime as dt

from dotenv import load_dotenv

from smsc_api import SMSC
from check_db import check_last_status

load_dotenv()

# ==============================

# Список проверяемых сайтов:
urls_tocheck = []
urls_tocheck.append("https://ezdy.ru/")
urls_tocheck.append("https://chus-info.ru/")

# ==============================

# Имя базы, в которой хранятся данные
DB_NAME = "site_checker.db"
SHOW_SUMMARY = True
USE_DEBUG = False
USE_DEBUG_SILENTS = False


def _print(*args, **kwargs):
    """controlled print func"""
    # if no debug
    if not USE_DEBUG:
        return
    print(*args, **kwargs)


class SiteChecker:
    """
    It's allows you to check is site available and notice by sms if is not
    """

    urls = []
    dbname = ''
    num = -1
    con = False
    cur = False
    status_changed = []
    ids_changed = []
    time = 0
    time_ok = 0
    time_fail = 0

    def __init__(self, urls, dbname) -> None:
        self.urls = urls
        self.dbname = dbname

    def main(self):
        """Main process function"""
        self.con = sqlite3.connect(self.dbname)
        self.cur = self.con.cursor()
        try:
            self.cur.execute(
                "CREATE TABLE site_status"
                + "(url, status, time_check, time_change, time_ok, time_fail)"
            )
        except sqlite3.IntegrityError as e:
            # Capture and log the exception, maintaining user awareness
            if USE_DEBUG_SILENTS:
                _print(f'Integrity error occurred: {e}')
        except sqlite3.OperationalError as e:
            # Handle operational issues decisively
            if USE_DEBUG_SILENTS:
                _print(f'Operational error occurred: {e}')

        for url in self.urls:
            self.num += 1
            _print()
            _print("=" * 10)
            _print(url)
            self.time = "{:%s}".format(dt.now())
            self.time_ok = self.time
            self.time_fail = self.time

            query = f"select * from site_status where url = '{url}' "
            res = self.cur.execute(query)
            url_data = res.fetchone()

            last_status = "-1"
            last_time_check = self.time
            last_time_change = self.time
            current_status = "-1"

            query_create = "INSERT INTO site_status VALUES ('{url}', '{status}', \
                '{time}', '{time_changed}', '{time_ok}', '{time_fail}')"

            query_update_ok = "update site_status set status = '{status}', \
                time_check = '{time}', time_ok = '{time_ok}' where url = '{url}'"
            query_update_ok_changed = "update site_status set status = '{status}', \
                time_check = '{time}', time_change = '{time_changed}', \
                time_ok = '{time_ok}' where url = '{url}'"

            query_update_fail = "update site_status set status = '{status}', \
                time_check = '{time}', time_fail = '{time_fail}' where url = '{url}'"
            query_update_fail_changed = "update site_status set status = '{status}', \
                time_check = '{time}', time_change = '{time_changed}', \
                time_fail = '{time_fail}' where url = '{url}'"

            is_new = True
            if url_data:
                is_new = False
                last_status = url_data[1]
                last_time_check = url_data[2]
                last_time_change = url_data[3]

                _print(
                    f" row {url} is_new={is_new} last_status={last_status} \
        last_time_check={last_time_check} last_time_change={last_time_change}"
                )

            status = "-1"
            try:
                Response = "no result"
                Response = requests.get(url)
                status = str(Response.status_code)
                mess = f"status: {status}"
                _print(mess)
            except Exception as e:
                _print(Response)
                _print(e)
                status = "fail"

            # if new record
            if status == "200":
                self.time_fail = 0
            else:
                self.time_ok = 0

            _print()
            _print("=" * 5)
            _print(url, status, type(status))

            _status_changed = False
            time_changed = 0
            if is_new:
                query = query_create
            else:
                if status == "200":
                    query = query_update_ok
                    if last_status != status:
                        # _status_changed = True # only if fail
                        time_changed = self.time
                        query = query_update_ok_changed
                else:
                    query = query_update_fail
                    if last_status != status:
                        _status_changed = True
                        time_changed = self.time
                        query = query_update_fail_changed

            # _status_changed = True # for test

            _print(f"{last_status} != {status}  >> {_status_changed}")

            _print(
                f" row 2 {url} is_new={is_new} new_status={status} \
        last_time_check={last_time_check} last_time_change={last_time_change}"
            )
            _print()
            # save resul to sqlite
            _print(query)
            query = query.format(
                status=status,
                time=self.time,
                time_changed=time_changed,
                time_ok=self.time_ok,
                time_fail=self.time_fail,
                url=url,
            )
            _print(query)
            self.cur.execute(query)
            self.con.commit()

            # check is status changed
            if _status_changed:
                self.ids_changed.append(str(self.num))
                _status = {"url": url, "status": str(status)}
                self.status_changed.append(_status)

        # check if have changesd and send sms
        if self.status_changed:
            # build message

            count_changed = len(self.status_changed)
            fist_site_name = self.status_changed[0]["url"]
            status = self.status_changed[0]["status"]
            ids = ""

            if status == "200":
                status = "работает"
            else:
                status = "не работает"

            if count_changed > 1:
                _print(self.ids_changed)
                ids = ",".join(self.ids_changed)
                ids = f" [{ids}]"
                count_changed = f"Обновились {count_changed} сайтов: {ids}"
            else:
                count_changed = ""

            mess = f"Сайт {fist_site_name} {status}. {count_changed}"

            # send message
            _print()
            _print("*" * 10)
            _print(mess)

            phonenum = os.getenv('TARGET_PHONE_NUMBER')
            sms_text = mess
            smsc = SMSC()
            r = smsc.send_sms(phonenum, sms_text)  # , sender=sender)
            # Сообщение отправлено успешно.
            # ID: 5708, всего SMS: 1, стоимость: 0, баланс: 116.392


if __name__ == "__main__":
    checker = SiteChecker(urls_tocheck, DB_NAME)
    checker.main()

    if SHOW_SUMMARY:
        check_last_status()
