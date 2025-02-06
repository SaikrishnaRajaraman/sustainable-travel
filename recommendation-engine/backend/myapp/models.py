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
    