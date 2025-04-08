from django.db import models

# Create your models here.
# Create Model for each table

class FlightData(models.Model):
    sno = models.IntegerField(primary_key=True)
    source_iata_code = models.CharField(max_length=100)
    destination_iata_code = models.CharField(max_length=100)
    flight_company = models.CharField(max_length=100)
    source_latitude = models.FloatField()
    destination_latitude = models.FloatField()
    source_longitude = models.FloatField()
    destination_longitude = models.FloatField()
    miles = models.FloatField()
    carbon_emission = models.FloatField()

    class Meta:
        managed = False  # This tells Django not to try to create or manage the table
        db_table = 'flight_emissions'  # The name of your existing table


class Airport(models.Model):
    id = models.CharField(primary_key=True)  # Example: "12345"
    iata = models.CharField(max_length=5)  # Example: "JFK"
    icao = models.CharField(max_length=5)  # Example: "JFK"
    airport = models.CharField(max_length=100)
    region_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, db_column="latitude")
    longitude = models.DecimalField(max_digits=10, decimal_places=6, db_column="longitude")


    class Meta:
        managed = False  # This tells Django not to try to create or manage the table
        db_table = 'Airports'  # The name of your existing table

    def __str__(self):
        return f"{self.iata_code} - {self.airport_name}"
    