import requests
import asyncio
from .Results import ServiceHealthCheck, HTTPInfo


class HTTPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the HTTP Check."""
        details = {"target": self.service_check_priv.target_host}

        if self.service_check_priv.http_info:
            details["url"] = self.service_check_priv.http_info.url
            details["path"] = self.service_check_priv.http_info.path

        loop = asyncio.get_running_loop()
        full_url = f"http://{details['url']}/{details['path']}"
        details["full_url"] = full_url

        try:
            # Since requests.get is a blocking operation, run it in the executor
            response = await loop.run_in_executor(
                None, requests.get, full_url, {"timeout": 4}
            )
            if response.status_code == 200:
                self.service_check_priv.result.success(
                    feedback=f"HTTP Accessible to host {self.service_check_priv.target_host} for page {details['path']}",
                    staff_details=details,
                )
            else:
                self.service_check_priv.result.fail(
                    feedback=f"Host {self.service_check_priv.target_host} returned status {response.status_code}",
                    staff_details=details,
                )
        except requests.exceptions.ConnectionError as e:
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback="Failed to connect to server, is port 80 open?",
                staff_details=details,
            )
        except requests.exceptions.Timeout as e:
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback="Request timed out",
                staff_details=details,
            )
        except Exception as e:  # Handling other exceptions as generic failures/errors
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback="An unknown error occurred during the HTTP check",
                staff_details=details,
            )
        finally:
            if "response" in locals() and response is not None:
                response.close()

        return self.service_check_priv
