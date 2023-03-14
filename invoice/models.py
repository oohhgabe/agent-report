from django.db import models

# Create your models here.
class Interpreter(models.Model):
    PAYMENT_CHOICES = [
        ("BCheck", "BCheck"),
        ("BTransfer", "BTransfer"),
        ("Check", "Check"),
        ("Gusto", "Gusto"),
        ("Michael Kings OPI Services", "Michael Kings OPI Services"),
        ("QBD", "QBD"),
        ("Universal Call Center", "Universal Call Center"),
        ("Trolly", "Trolly"),
        ("VIP Call Center", "VIP Call Center"),
    ]
    CENTER_CHOICES = [
        ("Michael Kings OPI Services", "Michael Kings OPI Services"),
        ("Universal Call Center", "Universal Call Center"),
        ("VIP Call Center", "VIP Call Center"),
        ("WWI Foreign", "WWI Foreign"),
        ("WWI Spanish", "WWI Spanish"),
    ]

    Name = models.CharField("Name", max_length=255)
    Payment_Method = models.CharField(
        "Payment Method", max_length=50, blank=True, choices=PAYMENT_CHOICES
    )
    Service_Center = models.CharField(
        "Service Center", max_length=50, blank=True, choices=CENTER_CHOICES
    )
    Total_Amount = models.FloatField("Total Amount", null=True)
    Total_Minutes = models.IntegerField("Total Minutes", null=True)

    def __str__(self):
        return self.Name


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
    Service_Center = models.CharField(
        "Service Center", max_length=50, blank=True,
    )

    def __str__(self):
        return self.Interpreter_Name
