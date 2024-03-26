#!/usr/bin/env python3
import asyncio
from .Results import ServiceHealthCheck


class FTPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the ICMP Check."""
        details = {"target": self.service_check_priv.target_host}
        loop = asyncio.get_running_loop()
        print("We got to FTP!")

        return self.service_check_priv
