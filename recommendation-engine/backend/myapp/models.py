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
    airport_id = models.CharField(max_length=50, primary_key=True)  # Example: "12345"
    iata_code = models.CharField(max_length=3, unique=True)  # Example: "JFK"
    airport_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    altitude = models.IntegerField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, db_column="latitude_decimal")
    longitude = models.DecimalField(max_digits=10, decimal_places=6, db_column="longitude_decimal")


    class Meta:
        managed = False  # This tells Django not to try to create or manage the table
        db_table = 'airports'  # The name of your existing table

    def __str__(self):
        return f"{self.iata_code} - {self.airport_name}"
    