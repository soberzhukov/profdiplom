import vk_api


class MyVkApi:

    def __init__(self, token):
        self.vk = vk_api.VkApi(token=token)

    def users_get_method(self, user_id):
        params = {
            'user_ids': user_id,
            'fields': 'city, relation, sex'
        }
        user_info = self.vk.method('users.get', values=params)
        return user_info

    def get_user_city(self, u_id):
        u_info = self.users_get_method(u_id)
        u_city = u_info[0].get('city', {}).get('title', 0)
        return u_city

    def users_search_method(self, count=1000, offset=0, age_from=0, age_to=0, sex=0, city=0, status=0):
        params = {
            'count': count,
            'has_photo': 1,
            'fields': 'city, relation, sex'
        }
        if offset:
            params['offset'] = offset
        if age_from or age_to:
            params['age_from'] = age_from
            params['age_to'] = age_to
        if sex:
            params['sex'] = sex
        if city:
            params['city'] = city
        if status:
            params['status'] = status
        users_list = self.vk.method('users.search', values=params)['items']
        return [user for user in users_list if user['can_access_closed'] is True]

    def photos_get_method(self, user_id, album='profile', number=3):
        params = {
            'owner_id': user_id,
            'album_id': album,
            'extended': 1,  # доп поля likes, comments,
            'photo_sizes': 1,
            'rev': 1  # хронологический порядок
        }
        result = self.vk.method('photos.get', values=params)['items']
        if len(result) >= number:
            return MyVkApi.favorite_photo(result, number)

    def city_dict(self, request):
        params = {
            'country_id': 1,
            'q': request,
        }
        return self.vk.method('database.getCities', values=params)

    @classmethod
    def favorite_photo(cls, photo_list, number):
        likes_dict = dict()
        for photo in photo_list:
            likes_dict[f"{photo['owner_id']}_{photo['id']}"] = photo['likes']['count'] + photo['comments']['count']
        return sorted(likes_dict, key=likes_dict.get, reverse=True)[:number]
