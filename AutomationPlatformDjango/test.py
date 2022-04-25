#!/usr/bin/python
# -*- coding: <encoding name> -*-
import sqlite3

db_file = 'db.sqlite3'
conn = sqlite3.connect(db_file)
cur = conn.cursor()


def inser(sql):
    # sql = '''insert into api_role values(1,'superadmin')'''
    cur.execute(sql)
    conn.commit()


def select(sql):
    cur.execute(sql)
    res = cur.fetchall()
    print(res)
    return res
# sql = '''insert into api_role values(2,'admin')'''
# inser(sql)
sql = ''' select * from sqlite_master'''
res=select(sql)
for i in res:
    print(i)
# res= cur.fetchall()
# for i in res:
#     print(i)
# print(res)

# import requests
#
# url = 'http://localhost:9527/v1/v1/api/user/add'
# data = {
#     "is_active": "true",
#     "nickname":"lizj40",
#     "password":"123456",
#     "phone":"1",
#     "role_id":1,
#     "user_id":"",
#     "user_name":"123"
# }
# res = requests.post(url,data)
# print(res)
