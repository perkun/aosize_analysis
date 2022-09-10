import sqlite3


class Database:
    def __init__(self, db_filename):
        self.db_filename = db_filename
        self.con = sqlite3.connect(db_filename)
        self.cur = self.con.cursor()

    def __del__(self):
        self.con.commit()
        self.con.close()

    def create_model_table(self):
        self.cur.execute("DROP TABLE IF EXISTS Model")
        self.cur.execute("CREATE TABLE IF NOT EXISTS Model("

                         "filename TEXT, "
                         "target TEXT, "
                         "method TEXT, "
                         "period DOUBLE, "
                         "lambda DOUBLE, "
                         "beta DOUBLE, "
                         "gamma DOUBLE, "
                         "jd_g0 DOUBLE)")

    def create_images_table(self):
        self.cur.execute("DROP TABLE IF EXISTS Images")
        self.cur.execute("CREATE TABLE IF NOT EXISTS Images("
                         "id INTEGER PRIMARY KEY, "
                         "deq_min DOUBLE, "
                         "deq_max DOUBLE, "
                         "deq_nominal DOUBLE, "
                         "radius_min DOUBLE, "
                         "radius_max DOUBLE, "
                         "radius_nominal DOUBLE, "
                         "scale INT, "
                         "jd DOUBLE, "
                         "asteroid_x DOUBLE, "
                         "asteroid_y DOUBLE, "
                         "asteroid_z DOUBLE, "
                         "earth_x DOUBLE, "
                         "earth_y DOUBLE, "
                         "earth_z DOUBLE, "
                         "aspect DOUBLE, "
                         "phase DOUBLE, "
                         "kmppx DOUBLE, "
                         "filename TEXT)")


    def create_results_table(self):
        self.cur.execute("DROP TABLE IF EXISTS Results")
        self.cur.execute("CREATE TABLE IF NOT EXISTS Results("
                         "id INTEGER PRIMARY KEY, "
                         "deq_nominal DOUBLE, "
                         "deq_min DOUBLE, "
                         "deq_max DOUBLE, "
                         "deq_plus DOUBLE, "
                         "deq_minus DOUBLE)")
        self.cur.execute("INSERT INTO Results VALUES(1,0,0,0,0,0)")



    def create(self):
        self.create_images_table()
        self.create_model_table()
        self.create_results_table()


    def speedup(self):
        self.cur.execute('pragma journal_mode=memory')
        self.cur.execute('pragma synchronous=off')
        self.cur.execute('pragma temp_store=memory')

    def clear_autoinc_table(self, tablename):
        self.cur.execute(f"DELETE FROM {tablename}")
        self.cur.execute(
            f"DELETE FROM `sqlite_sequence` WHERE `name` = '{tablename}'")
        self.cur.execute("COMMIT")

    def clear_table(self, tablename):
        self.cur.execute(f"DELETE FROM {tablename}")
        self.cur.execute("COMMIT")

    def execute(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def commit(self):
        self.con.commit()
