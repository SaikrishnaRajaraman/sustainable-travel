from django.shortcuts import render, HttpResponse
from rest_framework import viewsets,generics
from rest_framework.response import Response
from .models import FlightData
from .serializers import FlightDataSerializer
from rest_framework.decorators import api_view
# from ardf.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from .langchain import process_query
import asyncio
from asgiref.sync import sync_to_async

# Create your views here.

class FlightDataViewSet(viewsets.ModelViewSet):
    queryset = FlightData.objects.all()
    serializer_class = FlightDataSerializer
    
    def list(self, request):
        # You can add pagination here if needed
        queryset = self.get_queryset()
        serializer = FlightDataSerializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        })

@csrf_exempt
@api_view(['POST'])
def langchain_query(request):
    try:
        data = request.data  # DRF handles JSON parsing automatically
        print(data)
        if not data:
            return Response({"error": "Query is required"}, status=400)

        # Call the LangChain function in main.py
        result = process_query(data["source"], data["destination"])

        return Response({"response": result}, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

def home(request):
    return HttpResponse("Hello, world.")

