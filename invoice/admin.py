from decimal import Decimal
from django.contrib import admin
from import_export.admin import ImportExportMixin
from import_export.resources import ModelResource


from .models import CallLog, Interpreter
import pandas as pd


class InterpreterResource(ModelResource):
    class Meta:
        model = Interpreter
        import_id_fields = ("name",)
        fields = (
            "name",
            "payment",
            "center",
        )

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        print(type(dataset))
        df = pd.DataFrame(dataset.dict)
        print(df.head(10))
        return super().before_import(dataset, using_transactions, dry_run, **kwargs)


class InterpreterAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "payment", "center", "amount")
    list_filter = ("center", "payment")
    search_fields = ("name",)
    resource_class = InterpreterResource


class CallLogResource(ModelResource):
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
    resource_class = CallLogResource


admin.site.register(Interpreter, InterpreterAdmin)
admin.site.register(CallLog, CallLogAdmin)
