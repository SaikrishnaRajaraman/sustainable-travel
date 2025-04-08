from django.shortcuts import render, HttpResponse
from rest_framework import viewsets,generics
from rest_framework.response import Response
from .models import FlightData,Airport
from .serializers import FlightDataSerializer
from rest_framework.decorators import api_view, parser_classes
from django.views.decorators.csrf import csrf_exempt
# from .langchain import process_query,process_bulk_csv
from .tasks import process_query_async, process_bulk_csv_async
from rest_framework.parsers import MultiPartParser
import pandas as pd
from .calculate_miles import calculate_distance, DistanceUnit
from .cache import clear_route_cache
import os
from celery.result import AsyncResult

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
    """
    Process a query for flights from source to destination
    
    Request body:
        {
            "source": "Source airport code",
            "dest": "Destination airport code",
            "force_refresh": false  # Optional, default is false
        }
    """
    try:
        data = request.data
        print(data)
        source = data.get('source', '')
        dest = data.get('destination', '')
        force_refresh = data.get('force_refresh', False)
        
        if not source or not dest:
            return Response({"error": "Source and destination are required"}, status=400)
        
        # Process the query with optional force refresh
        # force_refresh=force_refresh
        # result = process_query(source, dest)
        task = process_query_async.delay(source,dest)
        
        return Response({
            "task_id": task.id,
            "status": "processing",
            "message": "Query is being processed asynchronously"
        })
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
@parser_classes([MultiPartParser])
def upload_csv_file(request):
    """Handles CSV upload and calculates miles for all routes using stored airport coordinates."""
    try:
        if "file" not in request.FILES:
            return Response({"error": "No file uploaded"}, status=400)

        file = request.FILES["file"]

        # Read CSV using pandas
        try:
            df = pd.read_csv(file)

            if "Air Origin Code" not in df.columns or "Air Destination Code" not in df.columns:
                return Response({"error": "CSV must contain 'source' and 'destination' columns"}, status=400)

                    # Remove Null Air Leg
            df = df.dropna(subset=["Air Leg"])
            # currently only considering the amount >0
            df = df[df["Amount"] >= 0]

            # Remove the rows which have airport codes XXX

            # data = data[data['Air Origin Code'] == 'XXX']
            df = df[
                (df["Air Origin Code"] != "XXX") & 
                (df["Air Destination Code"] != "XXX") & 
                (~df["Item Description"].str.contains("agent fee|baggage fee", case=False, na=False))  # Case-insensitive partial match
            ]

            print(df.info())
            print("\nSummary statistics:")
            print(df.describe(include="all"))

            num_columns = df.shape[0]
            print(f"Number of rows left after filtering: {num_columns}")

            print("\nShape of DataFrame (rows, columns):", df.shape)

            

            routes = df.rename(columns={"Air Origin Code": "source", "Air Destination Code": "destination"})[["source", "destination"]].dropna().to_dict(orient="records")

        except Exception as e:
            return Response({"error": f"Error processing CSV with pandas: {str(e)}"}, status=400)

        # Call the new bulk processing function
        result = process_bulk_csv(routes)

        return Response(result, status=200)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@csrf_exempt
@api_view(['POST'])
def clear_cache(request):
    """
    Clear cached route data
    
    Request body:
        {
            "source": "Source airport code",  # Optional
            "dest": "Destination airport code"  # Optional
        }
    
    If neither source nor dest is provided, all route caches will be cleared.
    If only source is provided, all routes from that source will be cleared.
    If only dest is provided, all routes to that destination will be cleared.
    If both are provided, only the specific route will be cleared.
    """
    try:
        data = request.data
        source = data.get('source', None)
        dest = data.get('dest', None)
        
        deleted_count = clear_route_cache(source, dest)
        
        if deleted_count > 0:
            return Response({"message": f"Successfully cleared {deleted_count} cache entries"})
        else:
            return Response({"message": "No cache entries found matching the criteria"})
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    
@csrf_exempt
@api_view(['GET'])
def get_task_status(request, task_id):
    """
    Get the status and result of an asynchronous task
    
    URL parameters:
        task_id: The ID of the task to check
    """
    try:
        task_result = AsyncResult(task_id)
        print(f"Task {task_id} status: {task_result.status}")
        
        response_data = {
            'task_id': task_id,
            'status': task_result.status,
        }
        
        if task_result.ready():
            if task_result.successful():
                result = task_result.get()
                response_data['status'] = result.get('status', 'SUCCESS')
                if 'result' in result:
                    response_data['result'] = result['result']
                if 'error' in result:
                    response_data['error'] = result['error']
            else:
                response_data['status'] = 'FAILURE'
                response_data['error'] = str(task_result.result)
        
        return Response(response_data)
    except Exception as e:
        print(f"Error checking task status: {str(e)}")
        return Response({"error": str(e)}, status=500)

def home(request):
    return HttpResponse("Hello, world.")
