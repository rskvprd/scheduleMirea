import sqlite3 as sql
from Student import Student


def st_to_tup(st: Student):
    tup = (
        str(st.user_id), st.group, st.my_file, int(st.everyPairSub), int(st.everyDaySub), int(st.everyWeekSub)
    )
    return tup


class SQLiteManager:
    def __init__(self, file='scheduleBot.db'):
        self.file = file
        from os import listdir
        if file not in listdir('resources'):
            open(f'resources/{file}', 'bw')
        self.file = f'resources/{file}'
        self.__connect = sql.connect(self.file)
        self.__cursor = self.__connect.cursor()
        self.__cursor.execute("""
                                create table if not exists students(
                                    userid text primary key,
                                    myGroup text,
                                    file text,
                                    pair int,
                                    day int,
                                    week int
                                );
                                """)
        self.__connect.commit()

    def add_student(self, st: Student):
        st = st_to_tup(st)
        self.__cursor.execute("""insert into students(userid, myGroup, file, pair, day, week)
                                values(?, ?, ?, ?, ?, ?)""", st)
        self.__connect.commit()

    def rm_student(self, userid):
        self.__cursor.execute(f'delete from students where userid={userid}')
        self.__connect.commit()

    def get_students(self):
        self.__cursor.execute('select * from students;')
        sts = self.__cursor.fetchall()
        students = []
        for st in sts:
            students.append(
                Student(
                    user_id=st[0], group=st[1], file=st[2], pair=bool(st[3]), day=bool(st[4]), week=bool(st[5])
                )
            )
        return students
