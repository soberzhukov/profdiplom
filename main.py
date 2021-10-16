from MyVkApi import MyVkApi
from VkBot import VkBot
from DB import DB
from TOKENS import TOKEN_GROUP, TOKEN_USER


def get_parameters(u_id):
    params_dict = dict()

    u_city = MyVkApi_user_1.get_user_city(u_id)
    params_dict['city'] = VkBot_user_1.city(u_id, fu=MyVkApi_user_1.city_dict, user_city=u_city)
    if not params_dict.get('city', 0):
        return 0

    params_dict['sex'] = VkBot_user_1.sex(u_id)
    if not params_dict.get('sex', 0):
        return 0

    age_list = VkBot_user_1.age_from_to(u_id)
    if not age_list:
        return 0
    params_dict['age_from'], params_dict['age_to'] = age_list[0], age_list[1]

    params_dict['status'] = VkBot_user_1.status(u_id)
    if not params_dict.get('status', 0):
        return 0

    return params_dict


def search_people(params_dict, u_id):
    for age in range(params_dict['age_from'], params_dict['age_to']+1):
        old_people, count = DB.check_db(u_id, params_dict, age)
        new_people = MyVkApi_user_1.users_search_method(offset=count, age_from=age, age_to=age,
                                                        sex=params_dict['sex'],
                                                        city=params_dict['city'], status=params_dict['status'])
        if old_people:
            yield [[i for i in new_people if i['id'] not in old_people], age]
        else:
            yield [new_people, age]


def parse_people_list(u_id, p_list, age, params):
    db_list = list()
    for num, people_dict in enumerate(p_list):
        name = f"{people_dict['first_name']} {people_dict['last_name']}"
        people_id = people_dict['id']
        photo_info_list = MyVkApi_user_1.photos_get_method(people_id, 'profile')
        if photo_info_list is None:
            continue

        db_list.append({'name': name, 'people_id': people_id, 'photo': photo_info_list})

        result = VkBot_user_1.new_next_user(name, u_id, people_id, photo_info_list)
        if not result:
            DB.write_db(u_id, params, age, db_list)
            return 0

    DB.write_db(u_id, params, age, db_list)
    return 1


def main():
    for req, user_id in VkBot_user_1.listen_event():

        if req == 'start':

            search_params = get_parameters(user_id)
            if not search_params:
                VkBot_user_1.menu(user_id)
                continue

            VkBot_user_1.write_msg(user_id, "Подбираем для Вас пару...")

            for people_list, age in search_people(search_params, user_id):

                if not parse_people_list(user_id, people_list, age, search_params):
                    VkBot_user_1.menu(user_id, 0)
                    break
            else:
                VkBot_user_1.menu(user_id, 2)

        elif req == 'stop':
            continue

        else:
            VkBot_user_1.menu(user_id, 1)


if __name__ == '__main__':
    MyVkApi_user_1, VkBot_user_1 = MyVkApi(TOKEN_USER), VkBot(TOKEN_GROUP)
    main()
