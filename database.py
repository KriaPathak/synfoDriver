import pyodbc



class Database:

    def __init__(self):

        self.db_handle = pyodbc.connect(
            'Driver={SQL Server};'
            'Server=DESKTOP-4LU99N7;'
            'Database=SynfoDriver;'
            'UID=sa;'
            'PWD=Servilink@123;'
        )

        self.mycursor = self.db_handle.cursor()



    def get_single_data(self, table, query_columns_dict):
        selection_list = " AND ".join([
            f"{column_name} {query_columns_dict[column_name][0]} ?"
            for column_name in sorted(query_columns_dict.keys())
        ])

        sql = f"SELECT * FROM {table} WHERE {selection_list}"

        val = tuple(query_columns_dict[column_name][1] for column_name in sorted(query_columns_dict.keys()))

        self.mycursor.execute(sql, val)
        result = self.mycursor.fetchone()

        return result



    def get_multiple_data(self, table, query_columns_dict):
        if query_columns_dict == None:
            sql = f"SELECT * FROM {table}"
            self.mycursor.execute(sql)
        else:
            selection_list = " AND ".join([
                f"{column_name} {query_columns_dict[column_name][0]} ?"
                for column_name in sorted(query_columns_dict.keys())
            ])
            sql = f"SELECT * FROM {table} WHERE {selection_list} "

            val = tuple(query_columns_dict[column_name][1] for column_name in sorted(query_columns_dict.keys()))

            self.mycursor.execute(sql, val)

        result = self.mycursor.fetchall()

        return result
    def get_multiple_data_orderby(self, table, query_columns_dict):
        if query_columns_dict == None:
            sql = f"SELECT * FROM {table}"
            self.mycursor.execute(sql)
        else:
            selection_list = " AND ".join([
                f"{column_name} {query_columns_dict[column_name][0]} ?"
                for column_name in sorted(query_columns_dict.keys())
            ])
            sql = f"SELECT * FROM {table} WHERE {selection_list} order by TagAddress"

            val = tuple(query_columns_dict[column_name][1] for column_name in sorted(query_columns_dict.keys()))

            self.mycursor.execute(sql, val)

        result = self.mycursor.fetchall()

        return result


    def insert_single_data(self, table, query_columns_dict):
        column_names = ",".join([f"{column_name}" for column_name in sorted(query_columns_dict.keys())])
        column_holders = ",".join([f"?" for column_name in sorted(query_columns_dict.keys())])
        sql = f"INSERT INTO {table} ({column_names}) VALUES ({column_holders})"

        val = tuple(query_columns_dict[column_name] for column_name in sorted(query_columns_dict.keys()))

        self.mycursor.execute(sql, val)
        self.db_handle.commit()

        return self.mycursor.rowcount


    def insert_multiple_data(self, table, columns, multiple_data):
        column_names = ",".join(columns)
        column_holders = ",".join([f"?" for column_name in columns])
        sql = f"INSERT INTO {table} ({column_names}) VALUES ({column_holders})"

        self.mycursor.executemany(sql, multiple_data)
        self.db_handle.commit()

        return self.mycursor.rowcount

    def update_single_data(self,table,id,status):
        sql = f"UPDATE {table} SET Active ='{status}' Where DriverDetailID={id}"



        self.mycursor.execute(sql)
        self.db_handle.commit()

        return self.mycursor.rowcount