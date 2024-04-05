from .Results import ServiceHealthCheck
import mysql.connector
import asyncio


class SQLCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        # Store the service check instance for later use.
        self.service_check_priv = service_check

    async def execute(self):
        # Get the current asyncio event loop to run asynchronous operations.
        loop = asyncio.get_running_loop()

        # Prepare the SQL connection details.
        details = self._prepare_details()

        # If the details are missing, return an error.
        if not details:
            return self.service_check_priv.result.error(
                feedback=f"No SQL info given for target: {self.service_check_priv.target_host}",
                staff_details="No details!",
            )

        try:
            # Attempt to asynchronously connect to the database.
            db = await loop.run_in_executor(
                None,
                lambda: mysql.connector.connect(
                    host=details["target"],
                    user=details["username"],
                    password=details["password"],
                    database=details["db_name"],
                ),
            )
            try:
                # Perform read and write checks on the database.
                await self._check_table_read(loop, db, details)
                await self._check_table_write(loop, db, details)

                # If successful, return a success result.
                return self.service_check_priv.result.success(
                    feedback=f"Successful Read & Write on SQL Host: {details['target']}\nAs User: {details['username']}",
                    staff_details=details,
                )
            finally:
                # Ensure the database connection is closed after operations.
                db.close()
        except mysql.connector.errors.InterfaceError as e:
            # Handle connection failures.
            details["raw"] = str(e)
            return self.service_check_priv.result.fail(
                feedback=f"Failed to connect to SQL Host: {details['target']}",
                staff_details=details,
            )
        except mysql.connector.errors.ProgrammingError as e:
            # Handle SQL syntax errors or missing databases/tables.
            details["raw"] = str(e)
            return self.service_check_priv.result.warn(
                feedback=f"SQL error occurred: {e.msg}",
                staff_details=details,
            )
        except Exception as e:
            # Catch-all for any other exceptions.
            details["raw"] = str(e)
            return self.service_check_priv.result.fail(
                feedback="An unexpected error occurred.",
                staff_details=details,
            )

    async def _check_table_read(self, loop, db, details):
        # Prepare a cursor for executing SQL queries.
        dbc = db.cursor()
        try:
            # Asynchronously execute a SELECT query to read from the table.
            await loop.run_in_executor(
                None, lambda: dbc.execute(f"SELECT * FROM {details['table_name']}")
            )
            # Fetch the results to ensure the query was successful.
            _ = dbc.fetchall()
        except mysql.connector.errors.ProgrammingError as e:
            # Re-raise the exception for centralized handling.
            raise
        except mysql.connector.errors.DataError as e:
            # Re-raise the exception for centralized handling.
            raise

    async def _check_table_write(self, loop, db, details):
        # Prepare a cursor for executing SQL queries.
        dbc = db.cursor()
        # Build an INSERT query from the test data.
        query = self._build_query(details["table_name"], details["test_data"])
        try:
            # Asynchronously execute the INSERT query to write to the table.
            await loop.run_in_executor(
                None, lambda: dbc.execute(query, tuple(details["test_data"].values()))
            )
            # Commit the changes to the database.
            await loop.run_in_executor(None, db.commit)
        except mysql.connector.errors.ProgrammingError as e:
            # Re-raise the exception for centralized handling.
            raise
        except mysql.connector.errors.DataError as e:
            # Re-raise the exception for centralized handling.
            raise

    def _build_query(self, table_name: str, test_data: dict):
        # Construct a SQL INSERT query string using the provided test data.
        key_string = ", ".join(test_data.keys())
        value_string = ", ".join("%s" for _ in test_data)
        return f"INSERT INTO {table_name} ({key_string}) VALUES ({value_string})"

    def _prepare_details(self):
        # Extract and return the necessary SQL connection and operation details from the service check.
        if self.service_check_priv.sql_info:
            sql_info = self.service_check_priv.sql_info
            return {
                "target": self.service_check_priv.target_host,
                "username": sql_info.sql_username,
                "password": sql_info.sql_password,
                "db_name": sql_info.db_name,
                "table_name": sql_info.table_name,
                "test_data": sql_info.test_data,
            }
        return None  # Return None if no SQL info is provided.
