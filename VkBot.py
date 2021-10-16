from random import randrange
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class VkBot:
    def __init__(self, token_group):
        self.vk = vk_api.VkApi(token=token_group)
        self.longpoll = VkLongPoll(self.vk)

    def start(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button('Start', VkKeyboardColor.PRIMARY)
        self.write_msg(user_id, "Давайте начнем, нажмите 'Start'", keyboard)

    def write_msg(self, user_id, message, keyboard=None, attachment=None):
        params = {
            'user_id': user_id,
            'message': message,
            'random_id': randrange(10 ** 7),
        }
        if keyboard is not None:
            params['keyboard'] = keyboard.get_keyboard()
        if attachment is not None:
            params['attachment'] = attachment
        self.vk.method('messages.send', params)

    def listen_event(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                yield [event.text.lower(), event.user_id]

    def city(self, u_id, fu, user_city):
        keyboard = VkKeyboard()
        if user_city:
            keyboard.add_button(f'{user_city}', VkKeyboardColor.PRIMARY)
        keyboard.add_button('Меню', VkKeyboardColor.NEGATIVE)
        self.write_msg(u_id, "Укажите город:", keyboard)

        for request, user_id in self.listen_event():
            city_dict = fu(request)
            if request == 'меню':
                return 0
            elif city_dict.get('count') != 0:
                return city_dict.get('items')[0].get('id')
            else:
                self.write_msg(user_id, "Попробуйте еще раз или пропустите")

    def sex(self, user_id):
        keyboard = VkKeyboard()
        keyboard.add_button('М', VkKeyboardColor.PRIMARY)
        keyboard.add_button('Ж', VkKeyboardColor.PRIMARY)
        keyboard.add_button('Меню', VkKeyboardColor.NEGATIVE)
        self.write_msg(user_id, "Укажите пол:", keyboard)

        for request, user_id in self.listen_event():
            if request == 'меню':
                return 0
            request_dict = {'ж': 1, 'м': 2}
            response = request_dict.get(request, 0)
            if response:
                return response
            self.write_msg(user_id, "Выберите вариант")
            continue

    def age_from_to(self, user_id):
        keyboard = VkKeyboard()
        keyboard.add_button('18-23', VkKeyboardColor.PRIMARY)
        keyboard.add_button('24-29', VkKeyboardColor.PRIMARY)
        keyboard.add_button('30-35', VkKeyboardColor.PRIMARY)
        keyboard.add_button('35-39', VkKeyboardColor.PRIMARY)
        keyboard.add_button('Меню', VkKeyboardColor.NEGATIVE)
        self.write_msg(user_id, "Выберите вариант или введите свой диапазон. От:", keyboard)

        age_from = self.age()
        if not age_from:
            return 0
        if type(age_from) is list:
            return age_from

        self.write_msg(user_id, "До:", keyboard)
        age_to = self.age()
        if not age_to:
            return 0

        return [age_from, age_to]

    def age(self):
        for request, user_id in self.listen_event():
            if request == 'меню':
                return 0
            request_dict = {'18-23': [18, 23], '24-29': [24, 29], '30-35': [30, 35], '35-39': [35, 39]}
            response = request_dict.get(request, 0)
            if response:
                return response
            try:
                request = int(request)
                if request < 14 or request > 80:
                    raise ValueError
            except ValueError:
                self.write_msg(user_id, "Пожалуйста введите число от 14 до 80 или выберите вариант")
                continue
            return request

    def status(self, user_id):
        keyboard = VkKeyboard(one_time=True)
        status = """
        Отправь цифру статуса:
        
        1 — не женат (не замужем);
        2 — встречается;
        3 — помолвлен(-а);
        4 — женат (замужем);
        5 — всё сложно;
        6 — в активном поиске;
        7 — влюблен(-а);
        8 — в гражданском браке.
    """
        keyboard.add_button('В активном поиске', VkKeyboardColor.PRIMARY)
        keyboard.add_button('Меню', VkKeyboardColor.NEGATIVE)
        self.write_msg(user_id, status, keyboard)

        for request, user_id in self.listen_event():
            if request == 'меню':
                return 0
            elif request == 'в активном поиске':
                return 6
            elif request in list(map(str, range(1, 9))):
                return int(request)
            else:
                self.write_msg(user_id, "Отправь цифру статуса")

    def new_next_user(self, name, user_id, person_id, photo_info):
        keyboard = VkKeyboard()
        keyboard.add_button('Next', VkKeyboardColor.PRIMARY)
        keyboard.add_button('Stop', VkKeyboardColor.NEGATIVE)
        message = f"{name} (https://vk.com/id{person_id})"
        attachment = f"photo{',photo'.join(photo_info)}"
        self.write_msg(user_id, message=message, attachment=attachment)
        self.write_msg(user_id, "Смотреть дальше - 'Next'. Остановить - Stop", keyboard)

        for request, user_id in self.listen_event():
            if request == 'next':
                return 1
            elif request == 'stop':
                return 0
            else:
                self.write_msg(user_id, "Нет такой команды")

    def menu(self, user_id, num=0):
        keyboard = VkKeyboard()
        keyboard.add_button('Start', VkKeyboardColor.PRIMARY)
        keyboard.add_button('Stop', VkKeyboardColor.NEGATIVE)
        if num == 1:
            self.write_msg(user_id, "Давайте начнем, нажмите Start", keyboard)
        elif num == 2:
            self.write_msg(user_id, "К сожалению больше людей не нашлось(", keyboard)
        else:
            self.write_msg(user_id, "Приходите к нам еще)", keyboard)
