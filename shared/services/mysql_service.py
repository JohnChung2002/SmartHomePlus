import mysql.connector

class MySQLService:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def close(self):
        if self.connection is not None:
            self.connection.close()

    def __enter__(self):
        self.connect()
    
    def __exit__(self, type, value, traceback):
        self.connection.close() # type: ignore

    def join_param_string(self, param_list:list):
        return ', '.join([('%s = %%s' %(key)) for key in param_list])
    
    def join_and_param_string(self, param_list:list):
        return ' AND '.join([('%s = %%s' %(key)) for key in param_list])

    def get_all(self, table_name: str):
        cursor = self.connection.cursor(dictionary=True) # type: ignore
        cursor.execute(f"SELECT * FROM {table_name}")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_by_id(self, table_name: str, primary_fields: list, data: list):
        cursor = self.connection.cursor(dictionary=True, buffered=True) # type: ignore
        cursor.execute(f"SELECT * FROM {table_name} WHERE {self.join_and_param_string(primary_fields)}", data)
        result = cursor.fetchone()
        cursor.close()
        return result

    def insert(self, table_name: str, fields: list, data: list):
        cursor = self.connection.cursor() # type: ignore
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({', '.join(['%s'] * len(fields))})", data)
        self.connection.commit() # type: ignore
        cursor.close()

    def update(self, table_name: str, modifying_fields: list, primary_fields: list, data: list):
        cursor = self.connection.cursor() # type: ignore
        cursor.execute(f"UPDATE {table_name} SET {self.join_param_string(modifying_fields)} WHERE {self.join_and_param_string(primary_fields)}", data)
        self.connection.commit() # type: ignore
        cursor.close()

    def delete_by_id(self, table_name: str, primary_fields: list, data: list):
        cursor = self.connection.cursor() # type: ignore
        cursor.execute(f"DELETE FROM {table_name} WHERE {self.join_and_param_string(primary_fields)}", data)
        self.connection.commit() # type: ignore
        cursor.close()

    def get_last_entry(self, table_name: str, primary_field: str):
        cursor = self.connection.cursor(dictionary=True) # type: ignore
        cursor.execute(f"SELECT * FROM {table_name} ORDER BY {primary_field} DESC LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def get_last_entry_by_id(self, table_name: str, primary_fields: list, order_field: str, data: list):
        cursor = self.connection.cursor(dictionary=True) # type: ignore
        cursor.execute(f"SELECT * FROM {table_name} WHERE {self.join_and_param_string(primary_fields)} ORDER BY {order_field} DESC LIMIT 1", data)
        result = cursor.fetchone()
        cursor.close()
        return result
    
    def increment_field(self, table_name: str, primary_fields: list, increment_field: str, data: list):
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE {table_name} SET {increment_field} = {increment_field} + 1 WHERE {self.join_and_param_string(primary_fields)}", data)
        self.connection.commit() # type: ignore
        cursor.close()

    def decrement_field(self, table_name: str, primary_fields: list, decrement_field: str, data: list):
        cursor = self.connection.cursor()
        cursor.execute(f"UPDATE {table_name} SET {decrement_field} = {decrement_field} - 1 WHERE {self.join_and_param_string(primary_fields)}", data)
        self.connection.commit()
        cursor.close()

    def get_env_data(self, date: str):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("""
        SELECT DATE_FORMAT(created_on, '%Y-%m-%d %H:00:00') AS hour,
        AVG(temperature) AS avg_temperature,
        AVG(brightness) AS avg_brightness,
        AVG(wetness) AS avg_wetness
        FROM environment_data
        WHERE DATE_FORMAT(created_on, '%Y-%m-%d') = %s
        GROUP BY hour
        """ , (date,))
        result = cursor.fetchall()
        cursor.close()
        return result
    
    def get_appliance_uptime(self, month: int, year: int):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(f"SELECT appliance_id, date, (SUM(uptime)/60) AS uptime FROM appliance_uptime WHERE MONTH(date) = %s AND YEAR(date) = %s GROUP BY appliance_id, date", (month, year))
        result = cursor.fetchall()
        cursor.close()
        if result is None:
            return []
        return result

    def update_with_feedback(self, table_name: str, modifying_fields: list, primary_fields: list, data: list):
        cursor = self.connection.cursor() # type: ignore
        cursor.execute(f"UPDATE {table_name} SET {self.join_param_string(modifying_fields)} WHERE {self.join_and_param_string(primary_fields)}", data)
        self.connection.commit() # type: ignore
        row_count = cursor.rowcount
        cursor.close()
        return row_count
    
    def get_all_profile(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT profile_id, rfid_id, name, DATE_FORMAT(birthday, '%Y-%m-%d') AS birthday, height, weight, bmi FROM Profile")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_stranger(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT stranger_id, TIME_FORMAT(time, '%H:%i:%s') as time, DATE_FORMAT(date, '%Y-%m-%d') AS date, status FROM Stranger")
        result = cursor.fetchall()
        cursor.close()
        return result

    def get_history(self):
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT history_id, profile_id, TIME_FORMAT(time, '%H:%i:%s') as time, DATE_FORMAT(date, '%Y-%m-%d') AS date, height, weight, bmi, in_house FROM History")
        result = cursor.fetchall()
        cursor.close()
        return result