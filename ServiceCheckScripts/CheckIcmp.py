#!/usr/bin/env python3

import ping3
import asyncio
from Results import ServiceHealthCheck

# Enable specific Errors
ping3.EXCEPTIONS = True


class ICMPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the ICMP Check."""
        details = {"target": self.service_check_priv.target_host}
        loop = asyncio.get_running_loop()
        try:
            # result = ping3.ping(self.service_check_priv.target_host, timeout=4)
            result = await loop.run_in_executor(
                None, ping3.ping, self.service_check_priv.target_host, 4
            )
            # Leave this for now, may use for later
            """
            if result is None:  # Treat None result as Destination Host Unreachable
                raise ping3.errors.DestinationHostUnreachable(
                    f"Destination Host Unreachable for host: {self.service_check_priv.target_host}"
                )
            """
        except ping3.errors.Timeout as e:
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f"Request Timed Out after 4 seconds for host {self.service_check_priv.target_host}",
                staff_details=details,
            )
            return self.service_check_priv
        except ping3.errors.HostUnknown as e:
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback=f"Could not resolve host: {self.service_check_priv.target_host}",
                staff_details=details,
            )
            return self.service_check_priv
        except ping3.errors.DestinationHostUnreachable as e:
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f'ping says "Destination Host Unreachable" for target: {self.service_check_priv.target_host}',
                staff_details=details,
            )
            return self.service_check_priv
        except ping3.errors.DestinationUnreachable as e:
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback='ping says "Destination Unreachable"', staff_details=details
            )
            return self.service_check_priv
        except ping3.errors.PingError as e:
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback="An unknown ping error occurred", staff_details=details
            )
            return self.service_check_priv
        self.service_check_priv.result.success(
            feedback=f"ping successful to host {self.service_check_priv.target_host}"
        )
        return self.service_check_priv
