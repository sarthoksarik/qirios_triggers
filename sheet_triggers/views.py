# sheet_triggers/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .tasks import run_external_script

@api_view(['GET'])
def run_script(request):
    run_external_script.delay()
    return Response({
        "message": "Script has been added to the queue and will run in background!!!"
    })
