#!/usr/bin/env python2.7
# -*-coding:utf-8 -*-
__author__ = 'yin'
import os
import sys
import time
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

'''
需要检测数据库
'''
#SQL_CON_SRC = {'host': '127.0.0.1', 'user': 'yqc', 'password': 'yqc2014'}
SQL_CON_SRC = {'host': '192.168.1.199', 'user': 'root', 'password': 'lh'}
'''
对比数据库
'''
SQL_CON_DES = {'host': '192.168.1.233', 'user': 'yqc', 'password': 'yqc2014'}


def compare_field(table, db):
    " compare field "

    global SESSION_DES
    global SESSION_SRC

    try:
        filed_src = SESSION_SRC.execute('show columns from `%s`' % table).fetchall()
        filed_des = SESSION_DES.execute('show columns from `%s`' % table).fetchall()
    except Exception, e:
        err_str = '*********** SHOW COLUMNS FORM %s %s ' % table, e
        write_file(db_name=db, err_str=err_str)
        return

    for filed in filed_des:
        if len(filed) >= 1:
            if filed not in filed_src:
                write_file(db_name=db, table_name=table, field_name=filed[0])


def compare_tables(db):
    "compare tables"
    global SESSION_DES
    global SESSION_SRC
    global FILE_CMP
    try:
        SESSION_SRC.execute('use %s' % db)
        SESSION_DES.execute('use %s' % db)
        list_src = SESSION_SRC.execute('show tables').fetchall()
        list_des = SESSION_DES.execute('show tables').fetchall()
    except Exception, e:
        err_str = '*********** SHOW TABLES %s %s ' % list_des[0], e
        write_file(db_name=db, err_str=err_str)
        return

    for tables in list_des:
        if tables in list_src:
            compare_field(tables[0], db)
        else:
            write_file(db_name=db, table_name=tables[0])


def write_file(db_name, table_name=None, field_name=None, err_str=None):

    file_cmp = file('db_compare.txt', 'a')
    print db_name, table_name, field_name, err_str
    w_str = ''
    if err_str is not None:
        w_str += '%s ' % err_str
    else:
        w_str = 'database:::%s ' % db_name
        if table_name is not None:
            w_str += ' tables::%s ' % table_name
        if field_name is not None:
            w_str += ' filed:%s ' % field_name
    global FILE_CMP
    file_cmp.write('%s %s is not exsit' % (w_str, os.linesep))
    file_cmp.close()


def main(arg_v):

    db_connect_src = 'mysql+mysqldb://%s:%s@%s/yiqiding_ktv?charset=utf8' % (SQL_CON_SRC['user'], SQL_CON_SRC['password'], SQL_CON_SRC['host'])
    db_connect_des = 'mysql+mysqldb://%s:%s@%s/yiqiding_ktv?charset=utf8' % (SQL_CON_DES['user'], SQL_CON_DES['password'], SQL_CON_DES['host'])

    engine_src = create_engine(db_connect_src)
    engine_des = create_engine(db_connect_des)

    session_src = sessionmaker(bind=engine_src)
    session_des = sessionmaker(bind=engine_des)

    global SESSION_SRC
    global SESSION_DES
    SESSION_SRC = session_src()
    SESSION_DES = session_des()

    lists_src = []
    for lists in SESSION_SRC.execute('show databases').fetchall():
        lists_src.append(lists[0])

    database_list = []
    if len(arg_v) > 1:
        for arg in arg_v[1:len(arg_v)]:
            tables_list = arg.split('-')
            if tables_list >= 2:
                ##字段
                if tables_list[0] in lists_src:
                    for table in tables_list:
                        compare_field(table, tables_list[0])
                else:
                    write_file(tables_list[0])
                print tables_list[1], tables_list[0]
            elif tables_list == 1:
                database_list.append(arg)
    else:
        database_list = ['yiqiding', 'yiqiding_ktv', 'yiqiding_info', 'yqcchaindb', 'yqcdb']

    # filename = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
    # filename = filename + u'_db.txt'
    if database_list > 1:
        for database in database_list:
            if database in lists_src:
                print ' database name : %s ' % database
                compare_tables(database)
            else:
                write_file(database)


if __name__ == '__main__':
    main(sys.argv)



# lists_src = SESSION_SRC.execute('show databases').fetchall()
# lists_des = SESSION_DES.execute('show databases').fetchall()

# filename = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())
# filename = filename + u'_db.txt'
# global file_cmp
# file_cmp = file('db_compare.txt', 'a')
#
# for sig_lis in lists_des:
#     if sig_lis[0] != u'mysql' and sig_lis[0] != u'information_schema' and sig_lis[0] != u'performance_schema':
#         if sig_lis in lists_src:
#             print ' database name : %s ' % sig_lis[0]
#             compare_tables(databaseN=sig_lis[0])
#         else:
#             file_com.write('database::: %s is not exist %s' % (sig_lis[0], os.linesep))
#             pass
#
# file_com.close()
