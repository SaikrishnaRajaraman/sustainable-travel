from django.shortcuts import render, HttpResponse
from rest_framework import viewsets,generics
from rest_framework.response import Response
from .models import FlightData,Airport
from .serializers import FlightDataSerializer
from rest_framework.decorators import api_view, parser_classes
from django.views.decorators.csrf import csrf_exempt
from .langchain import process_query,process_bulk_csv,get_airport_iata_codes
from rest_framework.parsers import MultiPartParser
import pandas as pd
from .calculate_miles import calculate_distance, DistanceUnit
from .cache import clear_route_cache

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
        result = process_query(source, dest, force_refresh=force_refresh)
        
        return Response(result)
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
@api_view(['GET'])
def airports(request):

    try:
        result = get_airport_iata_codes()
        return Response({"response": result}, status=200)

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

def home(request):
    return HttpResponse("Hello, Sustainable world.")

