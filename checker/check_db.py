# check_db.py
#
# Author: WSD
# Author site: https://homdy.ru
# Author on kwork.ru: https://kwork.ru/user/phoenix_way
# Created: 2025.06.14

import sqlite3
from datetime import datetime as dt


# Имя базы, в которой хранятся данные
DB_NAME = "site_checker.db"


def checkLastStatus():
    """
    look current sites statuses and last check date
    """

    def _print(*args, **kwargs):
        # if no debug
        if 0:
            return 
        print(*args, **kwargs)


    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    res = cur.execute("SELECT * FROM site_status")
    data = res.fetchall()


    fields = (
    "url", 
    "status", 
    "time_check", 
    "time_change", 
    "time_ok", 
    "time_fail" 
    )

    fields = (
    "url", 
    "status", 
    "проверено", 
    "изменено", 
    "последнее 200", 
    "последнее fail" 
    )
    fields_row = ["{:^18}".format(f) for f in fields]
    fields_row[0] = "{:^28}".format(fields[0])
    fields_row[1] = "{:^8}".format(fields[1])
    fields_row = ' '.join(fields_row)
    print(fields_row)
    print('-' * len(fields_row))

    for row in data:
        row = [f for f in row]

        rnum = 2
        if int(row[rnum]) > 0:
            dt_obj = dt.fromtimestamp(int(row[rnum]))
            # row[2] = dt_obj.strftime("%b %d %Y %H:%M:%S")
            row[rnum] = dt_obj.strftime("%Y-%m-%d %H:%M")

        rnum = 3
        if int(row[rnum]) > 0:
            dt_obj = dt.fromtimestamp(int(row[rnum]))
            row[rnum] = dt_obj.strftime("%Y-%m-%d %H:%M")

        rnum = 4
        if int(row[rnum]) > 0:
            dt_obj = dt.fromtimestamp(int(row[rnum]))
            row[rnum] = dt_obj.strftime("%Y-%m-%d %H:%M")

        rnum = 5
        if int(row[rnum]) > 0:
            dt_obj = dt.fromtimestamp(int(row[rnum]))
            row[rnum] = dt_obj.strftime("%Y-%m-%d %H:%M")

        fields_row = ["{:<18}".format(f) for f in row]
        fields_row[0] = "{:<28}".format(row[0])
        fields_row[1] = "{:<8}".format(row[1])
        fields_row = ' '.join(fields_row)
        print(fields_row)


if __name__ == "__main__":
    checkLastStatus()