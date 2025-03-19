from django.shortcuts import render, HttpResponse
from rest_framework import viewsets,generics
from rest_framework.response import Response
from .models import FlightData,Airport
from .serializers import FlightDataSerializer
from rest_framework.decorators import api_view, parser_classes
from django.views.decorators.csrf import csrf_exempt
from .langchain import process_query,process_bulk_csv
from rest_framework.parsers import MultiPartParser
import pandas as pd
from .calculate_miles import calculate_distance, DistanceUnit

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

def home(request):
    return HttpResponse("Hello, Sustainable world.")

