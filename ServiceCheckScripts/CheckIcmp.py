#!/usr/bin/env python3

import ping3  # Import the ping3 library to use for pinging.
import asyncio  # Import the asyncio library for asynchronous programming.
from .Results import (
    ServiceHealthCheck,
)  # Import ServiceHealthCheck from the Results module in the current package.

# Enable specific Errors in ping3 library to be raised during execution.
ping3.EXCEPTIONS = True


class ICMPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        # Initialize the ICMPCheck object with a service_check instance.
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the ICMP Check."""
        details = {
            "target": self.service_check_priv.target_host
        }  # Details dict to store target host information.
        loop = asyncio.get_running_loop()  # Get the current asyncio event loop.

        try:
            # Perform the ping operation asynchronously.
            # ping3.ping method is called in an executor, with the target host and a 4-second timeout as arguments.
            result = await loop.run_in_executor(
                None, ping3.ping, self.service_check_priv.target_host, 4
            )
        except ping3.errors.Timeout as e:
            # Handle timeout errors by logging and setting the result to fail with a descriptive message.
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f"Request Timed Out after 4 seconds for host {self.service_check_priv.target_host}",
                staff_details=details,
            )
            return self.service_check_priv
        except ping3.errors.HostUnknown as e:
            # Handle unknown host errors similarly, marking the result as an error.
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback=f"Could not resolve host: {self.service_check_priv.target_host}",
                staff_details=details,
            )
            return self.service_check_priv
        except ping3.errors.DestinationHostUnreachable as e:
            # Handle the error when the destination host is unreachable.
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f'ping says "Destination Host Unreachable" for target: {self.service_check_priv.target_host}',
                staff_details=details,
            )
            return self.service_check_priv
        except ping3.errors.DestinationUnreachable as e:
            # Handle generic destination unreachable errors.
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback='ping says "Destination Unreachable"', staff_details=details
            )
            return self.service_check_priv
        except ping3.errors.PingError as e:
            # Catch-all for other ping-related errors, marking the result as an error with a generic message.
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback="An unknown ping error occurred", staff_details=details
            )
            return self.service_check_priv

        # If ping is successful, mark the result as success.
        self.service_check_priv.result.success(
            feedback=f"ping successful to host {self.service_check_priv.target_host}"
        )
        return self.service_check_priv
