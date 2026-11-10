
from datetime import timezone as datetime_timezone

from ibm_db_django.base import DatabaseWrapper as IBMDatabaseWrapper
from ibm_db_django.operations import (
    DatabaseOperations as IBMDatabaseOperations,
)
from ibm_db_django.pybase import DB2CursorWrapper


class CompatibleDB2CursorWrapper(DB2CursorWrapper):
    def _format_parameters(self, parameters, operation, return_only_param=False):
        from django.utils import timezone

        original_utc = getattr(timezone, "utc", None)
        timezone.utc = datetime_timezone.utc

        try:
            return super()._format_parameters(
                parameters,
                operation,
                return_only_param,
            )
        finally:
            if original_utc is None:
                delattr(timezone, "utc")
            else:
                timezone.utc = original_utc


class DatabaseOperations(IBMDatabaseOperations):
    def adapt_datetimefield_value(self, value):
        if value is None or hasattr(value, "resolve_expression"):
            return value
        return value


class DatabaseWrapper(IBMDatabaseWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ops = DatabaseOperations(self)

    def create_cursor(self, name=None):
        return CompatibleDB2CursorWrapper(self.connection)
