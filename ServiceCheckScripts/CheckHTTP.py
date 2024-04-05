import requests
import asyncio
from .Results import ServiceHealthCheck


class HTTPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        # Initialize the HTTPCheck object with a ServiceHealthCheck instance.
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the HTTP Check."""
        # Initialize details dictionary with target host and timeout.
        details = {"target": self.service_check_priv.target_host, "timeout": 4}

        # If HTTP info is provided, populate the details dictionary with URL and path.
        if self.service_check_priv.http_info:
            details["url"] = self.service_check_priv.http_info.url
            details["path"] = self.service_check_priv.http_info.path

        loop = asyncio.get_running_loop()

        # Construct the full URL from the provided URL and path.
        if details["path"]:
            full_url = f"http://{details['url']}/{details['path']}"
        else:
            full_url = f"http://{details['url']}"
        details["full_url"] = full_url

        try:
            # Since requests.get is a blocking operation, use run_in_executor to run it asynchronously.
            response = await loop.run_in_executor(
                None, requests.get, full_url, details["timeout"]
            )
            # Check if the HTTP request was successful.
            if response.status_code == 200:
                # Mark the check as successful if the status code is 200.
                self.service_check_priv.result.success(
                    feedback=f"HTTP Accessible to host {self.service_check_priv.target_host} for page {details['path']}",
                    staff_details=details,
                )
            else:
                # Fail the check if the status code is not 200.
                self.service_check_priv.result.fail(
                    feedback=f"Host {self.service_check_priv.target_host} returned status {response.status_code}",
                    staff_details=details,
                )
        except requests.exceptions.ConnectionError as e:
            # Handle connection errors explicitly.
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback="Failed to connect to server, is port 80 open?",
                staff_details=details,
            )
        except requests.exceptions.Timeout as e:
            # Handle timeout errors explicitly.
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback="Request timed out",
                staff_details=details,
            )
        except Exception as e:  # Catch all other exceptions.
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback="An unknown error occurred during the HTTP check",
                staff_details=details,
            )
        finally:
            # Ensure the response is closed to free up resources.
            if "response" in locals() and response is not None:
                response.close()

        return self.service_check_priv
