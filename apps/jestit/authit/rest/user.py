from jestit.decorators import http as jd
from django.http import JsonResponse

@jd.GET("hell")
def hello_world(request):
    return JsonResponse(dict(data="hello back"))


@jd.GET("hello2")
def hello_world2(request):
    return JsonResponse(dict(data="good bye"))
