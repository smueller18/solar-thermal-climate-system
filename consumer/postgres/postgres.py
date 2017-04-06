#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import datetime


import psycopg2
import psycopg2.extras

__author__ = u'Stephan Müller'
__copyright__ = u'2017, Stephan Müller'
__license__ = u'MIT'


logger = logging.getLogger(__name__)


_data_types = {
    bytes: "bytea",
    float: "real",
    int: "bigint",
    bool: "bool",
    str: "text"
}


class Connector(object):

    def __init__(self, host, port, database, user, password):
        self._host = host
        self._port = port
        self._database = database
        self._user = user
        self._password = password

        try:
            self.con = psycopg2.connect(host=host, port=port, database=database, user=user, password=password)
            self.con.autocommit = True
        except Exception as e:
            raise e

    def table_exists(self, table_name):
        cur = self.con.cursor()
        sql = cur.mogrify("""
                          SELECT 1
                          FROM information_schema.tables
                          WHERE table_name=%s;
                          """, (table_name,))
        cur.execute(sql)

        result = cur.fetchall()
        if len(result) == 1:
            return True
        return False

    def create_table(self, table_name, keys, values):

        cur = self.con.cursor()

        column_names = list()
        column_sql = ""

        data = {**keys, **values}
        for column_name in data:
            column_names.append(column_name)

            if column_name.startswith("timestamp"):
                data_type = "TIMESTAMP WITH TIME ZONE"
            else:
                try:
                    data_type = _data_types[type(data[column_name])]

                except KeyError:
                    data_type = _data_types[str]

            column_sql += column_name + " " + data_type + ","

        column_sql += " PRIMARY KEY (" + ", ".join(keys) + ")"

        sql = """
              CREATE TABLE IF NOT EXISTS %s (
                %s
              );
              """ % (table_name, column_sql)

        try:
            cur.execute(sql)
            self.con.commit()

        except psycopg2.DatabaseError as de:
            logger.error(de.pgcode + " " + de.pgerror.replace("\n", " "))

    def insert_values(self, table_name, data):

        cur = self.con.cursor()

        keys = list()
        values = list()
        value_placeholders = list()

        for key in data:
            keys.append(key)

            if key.startswith("timestamp"):
                values.append(data[key] / 1000)
                value_placeholders.append("to_timestamp(%s)")
            else:
                values.append(data[key])
                value_placeholders.append("%s")

        sql = cur.mogrify("INSERT INTO " + table_name + " (" + ', '.join(keys) + ")"
                          " VALUES (" + ", ".join(value_placeholders) + ");", values)

        try:
            cur.execute(sql)
            self.con.commit()

        except psycopg2.OperationalError as e:
            raise e

        except psycopg2.DatabaseError as e:

            if e.pgcode == "23505":
                logger.warning(e.pgcode + " " + e.pgerror.replace("\n", " "))
                self.con.commit()
            elif e.pgcode is not None and e.pgerror is not None:
                logger.error(e.pgcode + " " + e.pgerror.replace("\n", " "))
            else:
                logger.exception(e)

            raise e
