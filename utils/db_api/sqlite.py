import sqlite3


class Database:
    def __init__(self, path_to_db="data/sqlite.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data

    def create_table(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Films (
            id int NOT NULL,
            Name varchar(255) NOT NULL,
            ToWatch varchar(255),
            Watched varchar(255),
            Recension varchar(255)
            );
"""
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, name: str):
        return self.execute("INSERT INTO Films(id, Name) VALUES(?, ?)", parameters=(self.count_films()[-1], name),
                            commit=True)

    def add_film(self, id: int, name: str, title: str, watched: bool = False):
        if watched:
            sql = f"""
            INSERT INTO Films(id, Name, Watched) VALUES(?, ?, ?);
            """
        else:
            sql = f"""
            INSERT INTO Films(id, Name, ToWatch) VALUES(?, ?, ?);
            """
        return self.execute(sql, parameters=(id, name, title), commit=True)

    def select_column(self, column: str = None, everyone: bool = False):  # все фильмы из всех таблиц, вернет 2 списка
        if everyone:
            return self.execute(f"SELECT * FROM Films", fetchall=True)
        else:
            sql = f"""
            SELECT {column} FROM Films;
            """
            return self.execute(sql, fetchall=True)

    def select_film(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        if kwargs:
            sql = f"SELECT * FROM Films WHERE "
            sql, parameters = self.format_args(sql, kwargs)
            return self.execute(sql, parameters=parameters, fetchone=True)
        else:
            return self.execute("SELECT * FROM Films;", fetchall=True)

    def count_films(self):  # вернет какой-то кортеж, надо брать последний элемент
        return self.execute("SELECT COUNT (*) FROM Films;", fetchall=True)

    def update_recension(self, name, recension, title):  # рецензия на ПРОСМОТРЕННЫЙ фильм
        sql = f"""
        UPDATE Films SET Recension=? WHERE Name=? AND Watched=?
        """
        return self.execute(sql, parameters=(recension, name, title), commit=True)

    def delete_film(self, name: str = None, column: str = None):
        if name and column:
            sql = f"DELETE FROM Films WHERE Name=? AND {column}=?"
            self.execute(sql, parameters=(name, column), commit=True)
            return
        elif name:
            sql = f"DELETE FROM Films WHERE Name=?"
            self.execute(sql, parameters=(name,), commit=True)
        else:
            self.execute("DELETE FROM Users WHERE TRUE", commit=True)

    def change_column(self, name, film):
        watched_list = self.select_column(column="Watched")
        to_watch_list = self.select_column(column="ToWatch")
        if film in [str(number) for film in watched_list for number in film]:
            sql = f"DELETE FROM Films WHERE Name=? AND Watched=?"
            self.execute(sql, parameters=(name, film), commit=True)
            sql = f"INSERT INTO Films(id, Name, ToWatch) VALUES (?, ?, ?)"
            self.execute(sql, parameters=(len(self.select_film())+1, name, film), commit=True)
            return "from_watched"
        elif film in [str(number) for film in to_watch_list for number in film]:
            sql = f"DELETE FROM Films WHERE Name=? AND ToWatch=?"
            self.execute(sql, parameters=(name, film), commit=True)
            sql = f"INSERT INTO Films(id, Name, Watched) VALUES (?, ?, ?)"
            self.execute(sql, parameters=(len(self.select_film())+1, name, film), commit=True)
            return "from_to_watch"
        else:
            return False




def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")


