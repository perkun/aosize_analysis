import re
from aosize_anal.database import Database
import os.path


class Model:
    def __init__(self):
        self.lam = 0
        self.beta = 0
        self.gamma = 0
        self.jd_g0 = 0
        self.period = 0
        self.target = ""
        self.method = ""
        self.filename = ""

    def __str__(self):
        return f"{self.lam}, {self.beta}, {self.gamma}, {self.jd_g0}, {self.period}, {self.method}, {self.target}"

    def read_from_obj(self, filename):
        self.filename = filename
        f = open(filename, "r")
        while True:
            line = f.readline()
            if not line:
                break

            m = re.compile('^# ([^:]*): (.*)').match(line)
            if m:
                key = m.group(1)
                value = m.group(2)
                if key == "target":
                    self.target = value
                if key == "method":
                    self.method = value
                if key == "period[h]":
                    self.period = float(value)
                if key == "lambda":
                    self.lam = float(value)
                if key == "beta":
                    self.beta = float(value)
                if key == "gamma":
                    self.gamma = float(value)
                if key == "jd_gamma0":
                    self.jd_g0 = float(value)

        f.close()

    def update_table(self, database):
        database.clear_table("Model")
        database.execute("INSERT INTO Model(filename, target, method, "
                         "period, lambda, beta, gamma, jd_g0) "
                         "VALUES("
                         f"'{os.path.abspath(self.filename)}', '{self.target}', "
                         f"'{self.method}', {self.period}, {self.lam}, "
                         f"{self.beta}, {self.gamma}, {self.jd_g0})")
        database.commit()
