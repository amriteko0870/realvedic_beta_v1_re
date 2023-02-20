from import_statements import *

# Create your views here.

@api_view(['GET'])
def index(request):
    return Response('hello')