from typing import Any, Dict
from django.urls import reverse
from rest_framework import status
from django.http.response import HttpResponse
from rest_framework.test import APITestCase


class RestAPITestCase(APITestCase):
    base_url = ''
    serializer = None

    def __init__(self, x) -> None:
        super().__init__(x)
        self.list_url = f'{self.base_url}-list'
        self.detail_url = f'{self.base_url}-detail'
        self.model = self.serializer.Meta.model

    def receive_get_response(self) -> HttpResponse:
        url = reverse(self.list_url)
        return self.client.get(url)

    def receive_post_response(self, object_data: dict) -> HttpResponse:
        url = reverse(self.list_url)
        return self.client.post(url, object_data, format='json')

    def receive_get_detail_response(self, pk: object) -> HttpResponse:
        url = reverse(self.detail_url, kwargs={'pk': pk})
        return self.client.get(url)

    def receive_put_response(self,
                             pk: object, object_data: dict) -> HttpResponse:
        url = reverse(self.detail_url, kwargs={'pk': pk})
        return self.client.put(url, object_data, format='json')

    def receive_patch_response(self,
                               pk: object, object_data: dict) -> HttpResponse:
        url = reverse(self.detail_url, kwargs={'pk': pk})
        return self.client.patch(url, object_data, format='json')

    def receive_delete_response(self, pk: object) -> HttpResponse:
        url = reverse(self.detail_url, kwargs={'pk': pk})
        return self.client.delete(url)

    def get_all_instance_data(self) -> list:
        all = self.model.objects.all()
        return [self.serializer(x).data for x in all]

