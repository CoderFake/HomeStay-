from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from django.http import JsonResponse
import requests


class BadRequestView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'bad_request.html'

    def get(self, request):
        return Response(template_name=self.template_name, status=400)


class NotFoundView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'not_found.html'

    def get(self, request):
        return Response(template_name=self.template_name,  status=404)


class GetLocationsView(APIView):

    def get(self, request, *args, **kwargs):
        type_ = request.GET.get('type')
        parent_id = request.GET.get('parentId', '')
        api_url = "https://member.lazada.vn/locationtree/api/getSubAddressList?countryCode=VN"

        if type_ in ['district', 'ward']:
            api_url += f"&addressId={parent_id}"

        response = requests.get(api_url)
        locations = response.json().get('module', [])
        return Response(locations, status=status.HTTP_200_OK)

def bad_request_view(request, exception=None):
    view = BadRequestView.as_view()
    return view(request)


def not_found_view(request, exception=None):
    view = NotFoundView.as_view()
    return view(request)