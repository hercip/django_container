from django.urls.base import reverse
from rest_framework_addons.tests import RestAPITestCase
from manager.serializers import MenuItemSerializer
from manager.serializers import AppUserSerializer
from rest_framework.authtoken.models import Token
from manager.models import AppUser
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

WRONG_EMAIL = 'no_email_format'
NOT_EXISTING_USER_ID = 999 # just an ID that does not exist
KIND_USER = 1
KIND_ADMIN = 0
EMAIL = 'new@email.com'
BASE_USER_DATA = dict(
    username='b_username',
    password='b_password',
    email='b_mail@email.com',
    first_name='b_Prenume',
    last_name='b_Nume',
    phone='1234567',
    avatar='http://a.b.c/m',
    gender='M',
    kind=KIND_USER)
INITIAL_USER_DATA = dict(
    username='i_username',
    password='i_password',
    email='i_mail@email.com',
    first_name='i_Prenume',
    last_name='i_Nume',
    phone='1234567',
    avatar='http://a.b.c/f',
    gender='F',
    kind=KIND_ADMIN)
USER_DATA = dict(
    username='username',
    password='password',
    email='mail@email.com',
    first_name='Prenume',
    last_name='Nume',
    phone='1234567',
    kind=KIND_USER)
INITIAL_MENU_ITEM = dict(
    name='Menu1',
    icon='image1',
    link='/test/1')
MENU_ITEM_DATA = dict(
    name='Menu2',
    icon='image2',
    link='/test/2')


class APILogedInByTokenTestCase(RestAPITestCase):
    def setUp(self):
        def get_a_test_token():
            user = AppUser.objects.create_user(**BASE_USER_DATA)
            permission = Permission.objects.all()
            user.user_permissions.add(*permission)
            return Token.objects.create(user=user)

        token = get_a_test_token()
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

    def get_login_response(self, user_data) -> None:
        return self.client.post(reverse('login'), user_data, format='json')


class APILoginTests(APITestCase):
    def setUp(self):
        AppUser.objects.create_user(**INITIAL_USER_DATA)

    def test__can_login(self):
        response = self.client.post(reverse('login'), INITIAL_USER_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        return response.data['token']

    def test__can_logout(self):
        token = self.test__can_login()
        username = INITIAL_USER_DATA['username']
        token_key = Token.objects.filter(user__username=username).first().key
        self.assertEqual(token, token_key)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.delete(reverse('logout'), format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        tokens = Token.objects.filter(user__username=username)
        self.assertEqual(tokens.exists(), False)


class APIAppUserTests(APILogedInByTokenTestCase):
    base_url = 'app-user'
    serializer = AppUserSerializer

    def setUp(self):
        super().setUp()
        self.user_data = INITIAL_USER_DATA.copy()
        self.extra_set_up()
        self.user = self.model.objects.create_user(**self.user_data)
        self.user_data = self.serializer(self.user).data

    def test__create_a_user(self) -> None:
        user_data = USER_DATA.copy()
        self.extra_create_a_user(user_data)
        response = self.receive_post_response(user_data)
        user_data.pop('password')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.check_extra(response.data, user_data)
        self.assertDictContainsSubset(user_data, response.data)

    def test__create_a_user_then_login(self) -> int:
        self.test__create_a_user()
        response = self.client.post(reverse('login'), USER_DATA, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test__receive_a_user(self) -> None:
        response = self.receive_get_detail_response(self.user.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        up_keys = [x for x in self.serializer.Meta.fields if x != 'password']
        self.assertListEqual(list(response.data.keys()), up_keys)

    def test__forbid_duplicate_users_creation(self) -> None:
        response = self.receive_post_response(INITIAL_USER_DATA)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__delete_user(self) -> None:
        response = self.receive_delete_response(self.user.pk)
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)
        u = self.model.objects.filter(pk=self.user.pk).first()
        self.assertEquals(u, None)

    def test__receive_a_list_of_users(self) -> None:
        response = self.receive_get_response()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data, self.get_all_instance_data())

    def test__update_user_email(self) -> None:
        self.user_data['email'] = EMAIL
        response = self.update_user()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, self.user_data)

    def test__update_user_name(self) -> None:
        self.user_data['first_name'] = EMAIL
        response = self.update_user()
        self.user_data['name'] = '{} {}'.format(
            self.user_data['first_name'],
            self.user_data['last_name']
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictContainsSubset(self.user_data, response.data)

    def test__forbid_updating_a_usr_email_with_an_existing_email(self) -> None:
        username = BASE_USER_DATA['username']
        email = self._get_base_email(username)
        self.user_data['email'] = email
        response = self.update_user()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__forbid_creating_a_usr_email_with_an_existing_email(self) -> None:
        username = INITIAL_USER_DATA['username']
        email = self.model.objects.get(username=username).email
        user_data = USER_DATA.copy()
        user_data['email'] = email
        response = self.receive_post_response(user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test__remove_a_user(self) -> None:
        user_data = USER_DATA.copy()
        self.extra_create_a_user(user_data)
        user_id = self.receive_post_response(user_data).data['id']
        response = self.receive_delete_response(user_id)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def update_user(self):
        return self.receive_put_response(self.user.id, self.user_data)

    def _get_base_email(self, username):
        return AppUser.objects.get(username=username).email

    def extra_set_up(self) -> None:
        pass

    def extra_create_a_user(self, user_data) -> None:
        pass

    def check_extra(self, user_data, response_data) -> None:
        pass


class BaseNestedTests(APILogedInByTokenTestCase): # MenuItemTest
    base_url = 'menuitem'
    serializer = MenuItemSerializer
    main_field = 'name'
    INITIAL_INSTANCE_DATA = INITIAL_MENU_ITEM
    INSTANCE_DATA = MENU_ITEM_DATA

    def setUp(self):
        super().setUp()
        instance_data = self.INITIAL_INSTANCE_DATA.copy()
        instance_data = self.before_create(instance_data)
        self.model.objects.create(**instance_data)
        self.instance = self.model.objects.first()
        self.instance_data = self.serializer(self.instance).data

    def test__can_create_an_instance(self, key='id'):
        instance_data = self.INSTANCE_DATA.copy()
        response = self.receive_post_response(instance_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        if key in response.data and key not in instance_data:
            response.data.pop(key)
        data = self.check_nested(response.data, instance_data)
        self.assertEqual(data, instance_data)

    def test__can_delete_an_instance(self):
        instance_pk = self.instance.pk
        response = self.receive_delete_response(instance_pk)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        instance = self.model.objects.filter(pk=instance_pk).first()
        self.assertEqual(instance, None)

    def test__can_get_an_instance(self):
        response = self.receive_get_detail_response(self.instance.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.instance_data)

    def test__can_get_all_instances(self):
        self.test__can_create_an_instance()
        self.serializer = self.change_list_serializer()
        response = self.receive_get_response()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.model.objects.count())
        self.assertListEqual(response.data, self.get_all_instance_data())

    def test__can_update_an_instance(self):
        key = self.main_field
        instance_pk = self.instance.pk
        self.instance_data[key] = self.INSTANCE_DATA[key]
        response = self.receive_put_response(instance_pk, self.instance_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.instance_data)

    def test__can_partial_update_an_instance(self):
        key = self.main_field
        instance_pk = self.instance.pk
        self.instance_data[key] = self.INSTANCE_DATA[key]
        response = self.receive_patch_response(instance_pk, self.instance_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.data, self.instance_data)

    def before_create(self, instance_data) -> dict:
        return instance_data

    def check_nested(self, response_data, instance_data) -> any:
        return response_data

    def change_list_serializer(self):
        return self.serializer


class RegisterTests(TestCase):
    base_url = 'register'
    model = AppUser

    def setUp(self):
        self.user_data = INITIAL_USER_DATA.copy()
        self.user_updated = USER_DATA.copy()

    def test__create_user_without_token(self):
        response = self.client.post(reverse(self.base_url),self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
