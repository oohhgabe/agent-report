from decimal import Decimal
from django.contrib import admin
from django.http import HttpResponse
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
        fields = ("Name", "Payment_Method", "Service_Center", "Total_Amount")

    def get_export_fields(self):
        fields = super().get_export_fields()
        for field in fields:
            field.column_name = Interpreter._meta.get_field(
                field.attribute
            ).verbose_name
        return fields


class InterpreterResource(ModelResource):
    Payment_Method = fields.Field(
        column_name="Payment Method",
        attribute="Payment_Method",
        widget=PaymentChoiceWidget(),
    )
    Service_Center = fields.Field(
        column_name="Service Center",
        attribute="Service_Center",
        widget=CenterChoiceWidget(),
    )

    class Meta:
        model = Interpreter
        import_id_fields = ("Name",)
        fields = ("Name", "Payment_Method", "Service_Center")

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        dataset.headers = [
            "Name",
            "Payment Method",
            "Service Center",
        ]


def export_selected_interpreter_objects(modeladmin, request, queryset):
    selected = queryset.values_list("pk", flat=True)
    order_by = request.GET.get("order_by", "")
    print(order_by)
    queryset = Interpreter.objects.filter(pk__in=selected)
    dataset = ExportInterpreterResource().export(queryset)
    response = HttpResponse(
        dataset.xlsx,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="InterpretersPay.xlsx"'
    return response


export_selected_interpreter_objects.short_description = (
    "Export selected interpreters to XLSX"
)


class InterpreterAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("Name", "Payment_Method", "Service_Center", "Total_Amount")
    list_filter = ("Service_Center", "Payment_Method")
    search_fields = ("Name",)
    resource_class = InterpreterResource
    actions = [export_selected_interpreter_objects]

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
            if interpreter.Name in group.values:
                result = float(
                    group.loc[group["Interpreter Name"] == interpreter.Name][
                        "Interpreter Pay"
                    ].iloc[0]
                )
                interpreter.Total_Amount = round(Decimal(result), 2)
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

    def get_export_fields(self):
        fields = super().get_export_fields()
        for field in fields:
            field.column_name = CallLog._meta.get_field(field.attribute).verbose_name
        return fields


def export_selected_call_logs(modeladmin, request, queryset):
    selected = queryset.values_list("pk", flat=True)
    queryset = CallLog.objects.filter(pk__in=selected)
    dataset = ExportCallLogResource().export(queryset)
    response = HttpResponse(
        dataset.xlsx,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="InterpreterCalls.xlsx"'
    return response


export_selected_call_logs.short_description = "Export selected call logs to XLSX"


class CallLogAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "Interpreter_Name",
        "Language",
        "Interpreter_Pay",
        "Interpreter_Calltime",
        "Customer_Name",
        "Call_Time",
    )

    actions = [export_selected_call_logs]
    search_fields = ["Interpreter_Name", "Customer_Name"]
    resource_class = ImportCallLogResource

    def get_export_resource_class(self):
        return ExportCallLogResource

    # def get_import_resource_class(self):
    #     return ImportCallLogResource


admin.site.register(Interpreter, InterpreterAdmin)
admin.site.register(CallLog, CallLogAdmin)
