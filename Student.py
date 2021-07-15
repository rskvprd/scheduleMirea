import pandas as pd
from datetime import datetime

NUMBER_DAY = {0: '📅ПОНЕДЕЛЬНИК', 1: '📅ВТОРНИК', 2: '📅СРЕДА', 3: '📅ЧЕТВЕРГ', 4: '📅ПЯТНИЦА', 5: '📅СУББОТА'}
DAY_NUMBER = {'ПОНЕДЕЛЬНИК': 0, 'ВТОРНИК': 1, 'СРЕДА': 2, 'ЧЕТВЕРГ': 3, 'ПЯТНИЦА': 4, 'СУББОТА': 5}
SHORT_DAY_NUMBER = {'ПН': 0, 'ВТ': 1, 'СР': 2, 'ЧТ': 3, 'ПТ': 4, 'СБ': 5}


class Student:

    def __init__(self, user_id='228', group='ИВБО-06-19', file='ИИТ_2к_20-21_весна.xlsx',
                 pair=False, day=False, week=False):
        self.group = group
        self.user_id = str(user_id)
        self.my_file = file
        self.everyDaySub = day
        self.everyWeekSub = week
        self.everyPairSub = pair
        self.week_is_even = datetime.now().isocalendar()[1] % 2 == 1

    def __str__(self):
        return f'group = {self.group}, user_id = {self.user_id}, ' \
               f'file = {self.my_file}'

    def get_this_week_schedule(self):
        data_frame = pd.read_excel('resources/' + self.my_file)
        for j in range(len(data_frame.iloc[0])):
            if str(self.group) in str(data_frame.iloc[0][j]):
                index = j
                break
        return [[data_frame.iloc[i][index] for index in range(index, index + 4)] for i in range(len(data_frame) - 16)
                if i > 1]

    def reformat_week_schedule(self, schedule, half=True):
        """From raw week schedule data to readable schedule"""
        monday = schedule[0:12]
        tuesday = schedule[12:24]
        wednesday = schedule[24:36]
        thursday = schedule[36:48]
        friday = schedule[48:60]
        saturday = schedule[60:72]
        days = [monday, tuesday, wednesday, thursday, friday, saturday]
        pair_time = ['\n⏱9:00-10:30⏱\n', '\n⏱10:40-12:10⏱\n', '\n⏱12:40-14:10⏱\n', '\n⏱14:20-15:50⏱\n',
                     '\n⏱16:20-17:50⏱\n', '\n⏱18:00-19:30⏱\n', '--//--', '--//--']
        # цикл по дням

        for day in days:
            i = 0
            stop = len(day)
            pair_is_even = False
            pair_number = pair_time[0]
            # цикл по парам
            while i != stop:
                if half and pair_is_even and not self.week_is_even:
                    del day[i]
                    stop -= 1
                    pair_is_even = not pair_is_even
                    pair_number = pair_time[pair_time.index(pair_number) + 1]
                elif half and not pair_is_even and self.week_is_even:
                    del day[i]
                    stop -= 1
                    pair_is_even = not pair_is_even
                elif type(day[i][0]) is float:
                    del day[i]
                    stop -= 1
                    if pair_is_even:
                        pair_number = pair_time[pair_time.index(pair_number) + 1]
                    pair_is_even = not pair_is_even
                else:
                    #: day[i][0] - название пары
                    #: day[i][1] - тип пары
                    #: day[i][2] - препод
                    #: day[i][3] - аудитория
                    day[i][1] = ' - ' + str(day[i][1]) + '\n'
                    day[i].insert(0, str(pair_number))
                    day[i][3] = str(day[i][3]) + '\n'
                    if not half:
                        if pair_is_even:
                            day[i].insert(0, 'I')
                        else:
                            day[i].insert(0, 'II')
                    pair_is_even = not pair_is_even
                    pair_number = pair_time[pair_time.index(pair_number) + int(not pair_is_even)]
                    i += 1

        monday.insert(0, '\n📅ПОНЕДЕЛЬНИК')
        tuesday.insert(0, '\n📅ВТОРНИК')
        wednesday.insert(0, '\n📅СРЕДА')
        thursday.insert(0, '\n📅ЧЕТВЕРГ')
        friday.insert(0, '\n📅ПЯТНИЦА')
        saturday.insert(0, '\n📅СУББОТА')
        for day in days:
            if len(day) == 1:
                day.insert(1, '\nВЫХОДНОЙ')
        out = '\n'.join(map(str, days))
        return out.replace('[', '\n').replace(',', ' ').replace('nan', '   ').replace(']', '').replace('\'', '') \
            .replace('\\n', '\n\t').replace(' Д ', ' Дистанционно ').replace(' Д\n', ' Дистанционно ')

    def reformat_day_schedule(self, schedule, day):
        week_schedule = self.reformat_week_schedule(schedule).split('\n')
        day_name = NUMBER_DAY[day]
        res = []
        if day < 5:
            next_day_name = NUMBER_DAY[day + 1]
            for line in week_schedule:
                if day_name in line:
                    i = week_schedule.index(line)
                    while next_day_name not in week_schedule[i]:
                        res.append(week_schedule[i])
                        i += 1
                    return '\n'.join(res)
        if day == 5:
            for line in week_schedule:
                if day_name in line:
                    for i in range(week_schedule.index(line), len(week_schedule)):
                        res.append(week_schedule[i])
                        i += 1
                    return '\n'.join(res)
