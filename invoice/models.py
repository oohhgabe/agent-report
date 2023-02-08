from django.db import models

# Create your models here.
class Interpreter(models.Model):
    name = models.CharField("Name", max_length=255)
    payment = models.CharField("Payment Method", max_length=100, blank=True)
    center = models.CharField("Service Center", max_length=255, blank=True)
    amount = models.FloatField("Total Amount", null=True)

    def __str__(self):
        return self.name


class CallLog(models.Model):
    CallId = models.CharField("Call Id", max_length=25, blank=True)
    Call_Time = models.DateTimeField("Call Time", null=True)
    Interpreter_Calltime = models.IntegerField("Interpreter Calltime", null=True)
    Language = models.CharField("Language", max_length=100, blank=True)
    Interpreter_Pay = models.DecimalField(
        "Interpreter Pay", max_digits=6, decimal_places=2, null=True
    )
    Interpreter_Name = models.CharField("Interpreter Name", max_length=255, blank=True)
    Customer_Name = models.CharField("Customer Name", max_length=255, blank=True)

    def __str__(self):
        return self.Interpreter_Name
