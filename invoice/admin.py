from decimal import Decimal
from django.contrib import admin
from import_export import fields
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource
from import_export.widgets import Widget


from .models import CallLog, Interpreter
import pandas as pd


class PaymentChoiceWidget(Widget):
    def clean(self, value, row=None, *args, **kwargs):
        for choice in Interpreter.PAYMENT_CHOICES:
            if choice[1] == value:
                return choice[0]
        return value


class CenterChoiceWidget(Widget):
    def clean(self, value, row=None, *args, **kwargs):
        for choice in Interpreter.CENTER_CHOICES:
            if choice[1] == value:
                return choice[0]
        return value


class ExportInterpreterResource(ModelResource):
    class Meta:
        model = Interpreter
        fields = ("name", "payment", "center", "amount")


class InterpreterResource(ModelResource):
    payment = fields.Field(
        column_name="payment",
        attribute="payment",
        widget=PaymentChoiceWidget(),
    )
    center = fields.Field(
        column_name="center",
        attribute="center",
        widget=CenterChoiceWidget(),
    )

    class Meta:
        model = Interpreter
        import_id_fields = ("name",)
        fields = ("name", "payment", "center", "amount")


class InterpreterAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "payment", "center", "amount")
    list_filter = ("center", "payment")
    search_fields = ("name",)
    resource_class = InterpreterResource

    def get_export_resource_class(self):
        return ExportInterpreterResource


class ImportCallLogResource(ModelResource):
    class Meta:
        model = CallLog
        import_id_fields = ("CallId",)
        fields = (
            "Interpreter_Name",
            "Language",
            "Interpreter_Pay",
            "Interpreter_Calltime",
            "Customer_Name",
            "Call_Time",
            "CallId",
        )

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        df = pd.DataFrame(dataset.dict)
        df.drop(
            columns=[
                "CallId",
                "Caller Id",
                "Billed Seconds",
                "Operator",
                "Datacapture",
                "Customer Calltime",
                "Interpreter Calltime",
                "Interpreter Number",
                "Language Id",
                "Language",
                "Bill Customer",
                "Account Code",
                "Customer Name",
                "Call Time",
            ],
            inplace=True,
        )

        df["Interpreter Pay"] = df["Interpreter Pay"].apply(
            pd.to_numeric, downcast="float", errors="coerce"
        )
        group = (
            df.groupby(["Interpreter Name"])["Interpreter Pay"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )

        interpreters = Interpreter.objects.all()
        for interpreter in interpreters:
            if interpreter.name in group.values:
                result = float(
                    group.loc[group["Interpreter Name"] == interpreter.name][
                        "Interpreter Pay"
                    ].iloc[0]
                )
                interpreter.amount = round(Decimal(result), 2)
                interpreter.save()

        dataset.headers = [
            "CallId",
            "Caller_Id",
            "Call_Time",
            "Billed_Seconds",
            "Operator",
            "Datacapture",
            "Customer_Calltime",
            "Interpreter_Calltime",
            "Interpreter_Number",
            "Language_Id",
            "Language",
            "Interpreter_Pay",
            "Bill_Customer",
            "Account_Code",
            "Interpreter_Name",
            "Customer_Name",
        ]


class ExportCallLogResource(ModelResource):
    class Meta:
        model = CallLog
        fields = (
            "Interpreter_Name",
            "Language",
            "Interpreter_Pay",
            "Interpreter_Calltime",
            "Call_Time",
            "CallId",
        )


class CallLogAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "Interpreter_Name",
        "Language",
        "Interpreter_Pay",
        "Interpreter_Calltime",
        "Customer_Name",
        "Call_Time",
    )

    search_fields = ["Interpreter_Name", "Customer_Name"]
    resource_class = ImportCallLogResource

    def get_export_resource_class(self):
        return ExportCallLogResource

    def get_import_resource_class(self):
        return ImportCallLogResource


admin.site.register(Interpreter, InterpreterAdmin)
admin.site.register(CallLog, CallLogAdmin)
