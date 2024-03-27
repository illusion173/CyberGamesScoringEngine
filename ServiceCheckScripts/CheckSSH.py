#!/usr/bin/env python3
import asyncio
from .Results import ServiceHealthCheck
import sys
import paramiko
import paramiko.ssh_exception
import socket
from pathlib import Path


class SSHCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the SSH Check."""
        details = {"target": self.service_check_priv.target_host}
        print(self.service_check_priv.ssh_info)
        if self.service_check_priv.ssh_info:
            details["ssh_username"] = self.service_check_priv.ssh_info.ssh_username
            details["ssh_priv_key"] = self.service_check_priv.ssh_info.ssh_priv_key
        else:
            print("Error while retrieving SSH info for target", details["target"])
            sys.exit(0)
        # Assuming 'details["ssh_priv_key"]' contains the private key as a string
        private_key_file_name = details["ssh_priv_key"]
        private_key_file_path = str(Path.home()) + "/" + private_key_file_name

        private_key_file_obj = paramiko.RSAKey.from_private_key_file(
            private_key_file_path
        )

        loop = asyncio.get_running_loop()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Run the blocking function ssh.connect in a separate thread
            await loop.run_in_executor(
                None,
                lambda: ssh.connect(
                    hostname=details["target"],
                    username=details["ssh_username"],
                    pkey=private_key_file_obj,
                    timeout=5,
                ),
            )
            ssh.exec_command("exit 0")
        except (paramiko.ssh_exception.NoValidConnectionsError, socket.timeout) as e:
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f"Request Timed Out after 4 seconds for host {self.service_check_priv.target_host}",
                staff_details=details,
            )
        except paramiko.AuthenticationException as e:
            details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback=f"Could not Authneticate host: {self.service_check_priv.target_host} for user {self.service_check_priv.ssh_info.ssh_username}",
                staff_details=details,
            )
            print(e)
        except Exception as exc:
            details["raw"] = str(exc)
            self.service_check_priv.result.error(
                feedback="SSH Service Check Execution had an Exception: Call Staff",
                staff_details=details,
            )
        finally:
            ssh.close()

        self.service_check_priv.result.success(
            feedback=f"Successful to SSH to host {self.service_check_priv.target_host} for user {self.service_check_priv.ssh_info.ssh_username}"
        )
        return self.service_check_priv
