import vk_api
from vk_api.utils import get_random_id
from Student import *
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import main
import enum
from SQLiteManager import SQLiteManager

ADMIN_ID = 556317586
token = '4094458ea0a9ff184809db5a025ed12d4d68566661f0779c0852970d9789dc680c7878ffbbc0b1ec91b55'
vk_session = vk_api.VkApi(token=token)
longpoll = VkLongPoll(vk_session, wait=0)
vk = vk_session.get_api()
users = 'resources/users.txt'
Students = []
FEATURES = ['СЕГОДНЯ', 'ЗАВТРА', 'НЕДЕЛЯ', *DAY_NUMBER, *SHORT_DAY_NUMBER, 'СМЕНИТЬ ГРУППУ', 'КОМАНДЫ', 'ДЕНЬ НЕДЕЛИ',
            'ПОДПИСКИ', 'ЕЖЕНЕДЕЛЬНО', 'ЕЖЕПАРНО', 'ЕЖЕДНЕВНО', 'СМЕНИТЬ НЕДЕЛЮ']
RING_SCHEDULE = ['8:55', '10:35', '12:35', '14:15', '16:15', '17:55']

sql = SQLiteManager(file='scheduleBot.db')
start = VkKeyboard(one_time=False, inline=False)
start.add_button('Сегодня', color=VkKeyboardColor.PRIMARY)
start.add_button('Завтра', color=VkKeyboardColor.PRIMARY)
start.add_line()
start.add_button('Неделя', color=VkKeyboardColor.PRIMARY)
start.add_line()
start.add_button('День недели', color=VkKeyboardColor.SECONDARY)
start.add_line()
start.add_button('Подписки', color=VkKeyboardColor.PRIMARY)
start.add_line()
start.add_button('Сменить группу', color=VkKeyboardColor.NEGATIVE)
start.add_line()
start.add_button('Сменить неделю', color=VkKeyboardColor.NEGATIVE)

weekdays = VkKeyboard(one_time=False, inline=False)
weekdays.add_button('пн', color=VkKeyboardColor.PRIMARY)
weekdays.add_button('вт', color=VkKeyboardColor.PRIMARY)
weekdays.add_button('ср', color=VkKeyboardColor.PRIMARY)
weekdays.add_line()
weekdays.add_button('чт', color=VkKeyboardColor.PRIMARY)
weekdays.add_button('пт', color=VkKeyboardColor.PRIMARY)
weekdays.add_button('сб', color=VkKeyboardColor.PRIMARY)


def init_users():
    for st in sql.get_students():
        Students.append(st)


def main_fork(event, cur_student: Student):
    message = event.message.upper()
    if message in FEATURES:
        # Диалог с расписанием
        if message == 'ОБНОВИТЬ' and event.user_id == ADMIN_ID:
            vk.messages.send(
                user_id=event.user_id,
                message='Обновление.',
                random_id=get_random_id(),
                keyboard=VkKeyboard.get_empty_keyboard()
            )
            main.init()
            vk.messages.send(
                user_id=event.user_id,
                message='Обновление завершено.',
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'СМЕНИТЬ НЕДЕЛЮ' and event.user_id == ADMIN_ID:
            cur_student.week_is_even = not cur_student.week_is_even
            vk.messages.send(
                user_id=event.user_id,
                message='Неделя изменена.',
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'СМЕНИТЬ ГРУППУ':
            sql.rm_student(cur_student.user_id)
            vk.messages.send(
                user_id=event.user_id,
                message='Введи новую группу.',
                random_id=get_random_id(),
                keyboard=start.get_empty_keyboard()
            )
            del Students[Students.index(cur_student)]
        elif message == 'СЕГОДНЯ':
            today = datetime.now().weekday()
            if today == 6:
                today = 0
            vk.messages.send(
                user_id=event.user_id,
                message=cur_student.reformat_day_schedule(cur_student.get_this_week_schedule(), today),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'ЗАВТРА':
            today = datetime.now().weekday()
            if today >= 5:
                tomorrow = 0
            else:
                tomorrow = today + 1
            vk.messages.send(
                user_id=event.user_id,
                message=cur_student.reformat_day_schedule(cur_student.get_this_week_schedule(), tomorrow),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'КОМАНДЫ':
            vk.messages.send(
                user_id=event.user_id,
                message='Список навыков:\n',
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'НЕДЕЛЯ':
            vk.messages.send(
                user_id=event.user_id,
                message=cur_student.reformat_week_schedule(cur_student.get_this_week_schedule(), True),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'ДЕНЬ НЕДЕЛИ':
            vk.messages.send(
                user_id=event.user_id,
                message='Выберите день недели.',
                random_id=get_random_id(),
                keyboard=weekdays.get_keyboard()
            )
        elif message == 'ПОДПИСКИ':
            sub = VkKeyboard(one_time=False, inline=False)
            if cur_student.everyDaySub:
                sub.add_button('ежедневно', color=VkKeyboardColor.NEGATIVE)
            else:
                sub.add_button('ежедневно', color=VkKeyboardColor.POSITIVE)
            sub.add_line()

            if cur_student.everyPairSub:
                sub.add_button('ежепарно', color=VkKeyboardColor.NEGATIVE)
            else:
                sub.add_button('ежепарно', color=VkKeyboardColor.POSITIVE)
            sub.add_line()

            if cur_student.everyWeekSub:
                sub.add_button('еженедельно', color=VkKeyboardColor.NEGATIVE)
            else:
                sub.add_button('еженедельно', color=VkKeyboardColor.POSITIVE)
            vk.messages.send(
                user_id=event.user_id,
                message='Кликайте на кнопки для управления подписками\n'
                        '🍎 - выключить подписку\n'
                        '🍏 - подключить подписку',
                random_id=get_random_id(),
                keyboard=sub.get_keyboard()
            )
        elif message == 'ЕЖЕНЕДЕЛЬНО':
            cur_student.everyWeekSub = not cur_student.everyWeekSub
            mess = 'Еженедельная подписка подключена' if cur_student.everyWeekSub else 'Еженедельная подписка отключена'
            vk.messages.send(
                user_id=event.user_id,
                message=mess,
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'ЕЖЕДНЕВНО':
            cur_student.everyDaySub = not cur_student.everyDaySub
            mess = 'Ежедневная подписка подключена' if cur_student.everyDaySub else 'Ежедневная подписка отключена'
            vk.messages.send(
                user_id=event.user_id,
                message=mess,
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message == 'ЕЖЕПАРНО':
            cur_student.everyPairSub = not cur_student.everyPairSub
            mess = 'Ежепарная подписка подключена' if cur_student.everyPairSub else 'Ежепарная подписка отключена'
            vk.messages.send(
                user_id=event.user_id,
                message=mess,
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message in DAY_NUMBER:
            vk.messages.send(
                user_id=event.user_id,
                message=cur_student.reformat_day_schedule(cur_student.get_this_week_schedule(),
                                                          DAY_NUMBER[message]),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
        elif message in SHORT_DAY_NUMBER:
            vk.messages.send(
                user_id=event.user_id,
                message=cur_student.reformat_day_schedule(cur_student.get_this_week_schedule(),
                                                          SHORT_DAY_NUMBER[message]),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )
    else:
        vk.messages.send(
            user_id=event.user_id,
            message='Такой команды нет.',
            random_id=get_random_id(),
            keyboard=start.get_keyboard()
        )


class StudentState(enum.Enum):
    group_checked = 0
    group_unchecked = 1


def check_group_in_group_file(group):
    with open('resources/group-department.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if group in line:
                return line.split('.xlsx')[0] + '.xlsx'
    return False


def everyDaySub():
    today = datetime.now().weekday()
    if today >= 5:
        tomorrow = 0
    else:
        tomorrow = today + 1
    for st in Students:
        st: Student
        if st.everyDaySub:
            vk.messages.send(
                user_id=st.user_id,
                message=st.reformat_day_schedule(st.get_this_week_schedule(), tomorrow),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )


def everyPairSub():
    today = datetime.now().weekday()
    if today == 6:
        today = 0
    for st in Students:
        st: Student
        if st.everyPairSub:
            vk.messages.send(
                user_id=st.user_id,
                message=st.reformat_day_schedule(st.get_this_week_schedule(), today),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )


def everyWeekSub():
    for st in Students:
        st: Student
        st.week_is_even = not st.week_is_even
        if st.everyWeekSub:
            vk.messages.send(
                user_id=st.user_id,
                message=st.reformat_week_schedule(st.get_this_week_schedule()),
                random_id=get_random_id(),
                keyboard=start.get_keyboard()
            )


def main_dialog():
    """Основной диалоговый цикл бота
    В бесконечном цикле передаются longpoll запросы от vk к программе

    :return: None
    """
    pair_flag = True
    day_flag = True
    week_flag = True
    while True:
        try:
            now = datetime.now()
            time = str(now.time())[:5]
            if time in RING_SCHEDULE and pair_flag:
                everyPairSub()
                pair_flag = False
            if time not in RING_SCHEDULE and not pair_flag:
                pair_flag = True
            if time == '21:00' and day_flag and now.weekday() != 6:
                everyDaySub()
                day_flag = False
            if time == '21:01' and not day_flag:
                day_flag = True
            if time == '21:00' and now.weekday() == 6 and week_flag:
                everyWeekSub()
                week_flag = False
            if time == '21:01' and not week_flag:
                day_flag = True
            for event in longpoll.check():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    print('Someone text me.')
                    cur_student = False
                    if event.message.lower() == 'обама':
                        for st in Students:
                            sql.add_student(st)
                        print('обама')
                    # поиск в идентифицированных студентах
                    flag = StudentState.group_unchecked
                    for student in Students:
                        if str(event.user_id) == str(student.user_id):
                            cur_student = student
                            flag = StudentState.group_checked

                    # студент с найденной группой
                    if flag is StudentState.group_checked:
                        main_fork(event, cur_student)

                    # студент с ненайденной группой
                    elif flag is StudentState.group_unchecked:
                        group = event.message.upper()
                        file = check_group_in_group_file(group)
                        if file:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Я тебя запомнил',
                                random_id=get_random_id(),
                                keyboard=start.get_keyboard()
                            )
                            st = Student(group=group, user_id=str(event.user_id), file=file)
                            Students.append(st)
                            sql.add_student(st)
                        else:
                            vk.messages.send(
                                user_id=event.user_id,
                                message='Группа не найдена. Не забывайте тире и нули.',
                                random_id=get_random_id(),
                                keyboard=VkKeyboard.get_empty_keyboard()
                            )
        except Exception as e:
            print(e)


print('Let\'s start!')
init_users()
main_dialog()

