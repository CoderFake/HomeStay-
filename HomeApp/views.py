from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer


class HomeAppView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'homeapp/index.html'

    def get(self, request):
        return Response(template_name=self.template_name)
