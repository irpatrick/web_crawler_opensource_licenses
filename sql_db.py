import sqlite3
from LinkModel import Link
import ast

class Database:
   
    def __init__(self) -> None:
        self.connection = sqlite3.connect('./dbs/links.db')
        self.c = self.connection.cursor()
        # Create table link if it does not exist
        self.c.execute(""" CREATE TABLE IF NOT EXISTS link 
                                    (name TEXT, data TEXT, 
                                    hash_value TEXT PRIMARY KEY, 
                                    description TEXT, category TEXT, 
                                    type TEXT, tags TEXT, isPrivate INTEGER, 
                                    organization TEXT,
                                    date_of_creation DATETIME DEFAULT CURRENT_TIMESTAMP,
                                    published INTEGER DEFAULT 0 )""")

    def check_if_db_isempty (self):
        self.c.execute("SELECT count(hash_value) FROM link")
        return self.c.fetchone()[0]

    def add_link (self, data, name, hash_value, description, type, organization, tags, isPrivate, category):
        # cahge list to string to be able to store it in a string column
        tags = str(tags)
        # change boolean to int to be able to store it in a INTEGER column
        isPrivate = int(isPrivate)
        with self.connection:
            self.c.execute(""" INSERT INTO link  (data, name, hash_value,
                                                         description, type, organization, 
                                                        tags, isPrivate, category) 
                                                        VALUES (?,?,?,?,?,?,?,?,?)""", (data, name, hash_value, 
                                                                                 description, type, organization, 
                                                                                 tags, isPrivate, category))
        # self.connection.commit()

    def check_if_exist(self, hash_value):
        self.c.execute(""" SELECT count(hash_value) FROM link WHERE hash_value=?""", (hash_value,))
        if self.c.fetchone()[0] == 1:
            return True
        else:
            return False

    def get_all_links(self):
        self.c.execute("SELECT * FROM link")

        return self.c.fetchall()

    def get_all_links_by_publishment_status(self, published=0, count=10):
        self.c.execute("SELECT name, data, category, tags, organization, description FROM link WHERE published=? LIMIT ?",(published, count))
        links_list = self.c.fetchall()

        return self.normalizer(links_list)
    
    # To specify that a dataset was  visited
    def mark_as_visited(self, hash_value):
        with self.connection:
            self.c.execute(f"UPDATE link SET published=1 WHERE hash_value='{hash_value}'")

    #  a fuction to fetch 
    def close_connection(self):
        self.connection.close()

    # Normalize an sql query response to fit the Link object
    def normalizer(self, response):
        list_of_link = []
        for link in response:
            l = Link(
                name=link[0],
                data=link[1],
                category=link[2],
                tags=ast.literal_eval(link[3]),
                organization=link[4],
                description=link[5]
            )
            list_of_link.append(l)
        return list_of_link
    
