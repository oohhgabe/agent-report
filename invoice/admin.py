from decimal import Decimal
from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from functools import reduce
from import_export import fields
from import_export.admin import ImportExportMixin, ImportForm
from import_export.resources import ModelResource
from import_export.widgets import Widget
from io import BytesIO
from operator import or_


from .models import CallLog, Interpreter
import pandas as pd

class CustomImportExportMixin(ImportExportMixin):
    def import_action(self, request, *args, **kwargs):
        messages.warning(request, _('Once the SUBMIT button is clicked, please wait until imported data is shown below. Then, click CONFIRM IMPORT and wait to be redirected.'))
        return super().import_action(request, *args, **kwargs)

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
        fields = (
            "Name",
            "Payment_Method",
            "Service_Center",
            "Total_Amount",
            "Total_Minutes",
        )

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
    list_display = (
        "Name",
        "Payment_Method",
        "Service_Center",
        "Total_Amount",
        "Total_Minutes",
    )
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
        df["Interpreter Calltime"] = df["Interpreter Calltime"].apply(
            pd.to_numeric, downcast="integer", errors="coerce"
        )

        group = (
            df.groupby(["Interpreter Name"])["Interpreter Pay"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        minutes = (
            df.groupby(["Interpreter Name"])["Interpreter Calltime"]
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
                total_minutes = float(
                    minutes.loc[minutes["Interpreter Name"] == interpreter.Name][
                        "Interpreter Calltime"
                    ].iloc[0]
                )

                interpreter.Total_Amount = round(Decimal(result), 2)
                interpreter.Total_Minutes = total_minutes
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
            "Service_Center"
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


def export_sergio_center(modeladmin, request, queryset):
    selected = queryset.values_list("pk", flat=True)
    queryset = CallLog.objects.filter(pk__in=selected)
    dataset = ExportCallLogResource().export(queryset)

    df = pd.DataFrame(dataset.dict)
    df["Total"] = df["Interpreter Pay"]
    df["Total"] = df["Total"].astype(float)
    df["Day Rate"] = 0.25
    df["Night Rate"] = 0.37

    df["Day Minutes"] = df.apply(
        lambda x: x["Interpreter Pay"] / x["Interpreter Calltime"]
        if x["Interpreter Calltime"] != 0
        else Decimal("NaN"),
        axis=1,
    )
    df["Day Minutes"].fillna(0, inplace=True)
    df["Day Minutes"] = df["Day Minutes"].astype(float)

    df["Night Minutes"] = df.apply(
        lambda x: x["Interpreter Pay"] / x["Interpreter Calltime"]
        if x["Interpreter Calltime"] != 0
        else Decimal("NaN"),
        axis=1,
    )
    df["Night Minutes"].fillna(0, inplace=True)
    df["Night Minutes"] = df["Night Minutes"].astype(float)

    group = df.groupby(["Interpreter Name"]).aggregate(
        {
            "Day Minutes": "sum",
            "Day Rate": "first",
            "Night Minutes": "sum",
            "Night Rate": "first",
            "Total": "sum",
        }
    )

    with BytesIO() as b:
        writer = pd.ExcelWriter(b, engine="openpyxl")
        group.to_excel(writer, sheet_name="Sheet1")
        writer.save()
        # TODO: CHANGE FILENAME
        filename = "InterpreterCalls.xlsx"
        response = HttpResponse(
            b.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = "attachment; filename=%s" % filename
        return response


def get_total_pay(modeladmin, request, queryset):
    total = sum(obj.Interpreter_Pay for obj in queryset)
    message = f"Total Amount for selected rows: {total}"
    modeladmin.message_user(request, message)


def update_service_center(modeladmin, request, queryset):
    for call in queryset:
        try:
            interpreter = Interpreter.objects.get(Name=call.Interpreter_Name)
        except Interpreter.DoesNotExist:
            continue
        
        call.Service_Center = interpreter.Service_Center
        call.save()
    
    modeladmin.message_user(request, "The Service Center has been updated for the selected rows.")
    
export_selected_call_logs.short_description = "Export selected call logs to XLSX"
export_sergio_center.short_description = "Export selected rows to Universal's Format"
get_total_pay.short_description = "Obtain total pay for selected call logs"
update_service_center.short_description = "Update Service Center"

class CallLogAdmin(CustomImportExportMixin, admin.ModelAdmin):
    list_display = (
        "Interpreter_Name",
        "Language",
        "Interpreter_Pay",
        "Interpreter_Calltime",
        "Customer_Name",
        "Call_Time",
        "Service_Center",
    )

    actions = [export_selected_call_logs, export_sergio_center, get_total_pay, update_service_center]
    search_fields = ["Interpreter_Name", "Customer_Name"]
    list_filter = ("Service_Center",)
    resource_class = ImportCallLogResource

    def get_export_resource_class(self):
        return ExportCallLogResource

    def get_search_results(self, request, queryset, search_term):
        orig_queryset = queryset
        queryset, use_distinct = super(CallLogAdmin, self).get_search_results(
            request, queryset, search_term
        )

        if '"' in search_term:
            # Search for exact match using quotation marks
            terms = search_term.split('"')[1::2]  # extract all quoted terms
            print("This is the term length: ", len(terms))
            if len(terms) == 1:
                term = terms[0]
                q_objects = [Q(**{field: term}) for field in self.search_fields]
                queryset |= self.model.objects.filter(reduce(or_, q_objects))
            else:
                # Search for all quoted terms in relevant fields
                for term in terms:
                    print("This is the term: ", term)
                    q_objects = [Q(**{field: term}) for field in self.search_fields]
                    queryset |= self.model.objects.filter(reduce(or_, q_objects))
        else:
            # Search for records containing any of the searched words
            search_words = search_term.split(", ")
            if search_words:
                q_objects = [
                    Q(**{field + "__icontains": word})
                    for field in self.search_fields
                    for word in search_words
                ]
                queryset |= self.model.objects.filter(reduce(or_, q_objects))

        queryset = queryset & orig_queryset

        return queryset, use_distinct


admin.site.register(Interpreter, InterpreterAdmin)
admin.site.register(CallLog, CallLogAdmin)
