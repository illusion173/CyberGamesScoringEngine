#!/usr/bin/env python3
import asyncio
from Results import ServiceHealthCheck


class SSHCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the SSH Check."""
        details = {"target": self.service_check_priv.target_host}
        loop = asyncio.get_running_loop()
        print("We got to SSH!")

        return self.service_check_priv
