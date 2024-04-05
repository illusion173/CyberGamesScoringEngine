#!/usr/bin/env python3
import asyncio
import sys
import socket
import paramiko
from paramiko import SSHClient
import paramiko.ssh_exception
from pathlib import Path

from .Results import ServiceHealthCheck


class SSHCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check
        self.details = {"target": self.service_check_priv.target_host}
        if self.service_check_priv.ssh_info:
            self.details["ssh_username"] = self.service_check_priv.ssh_info.ssh_username
            self.details["ssh_priv_key"] = self.service_check_priv.ssh_info.ssh_priv_key
            self.details["ssh_script"] = self.service_check_priv.ssh_info.ssh_script
            self.details["md5_sum"] = self.service_check_priv.ssh_info.md5sum

        else:
            print("Error while retrieving SSH info for target", self.details["target"])
            sys.exit(0)

    def is_completely_empty_err(self, s):
        return s.strip()

    async def test_connection(self, ssh: SSHClient, loop: asyncio.AbstractEventLoop):
        try:
            # Run the blocking function ssh.connect in a separate thread
            # Assuming 'details["ssh_priv_key"]' contains the private key as a string

            private_key_file_name = self.details["ssh_priv_key"]
            private_key_file_path = str(Path.home()) + "/" + private_key_file_name

            private_key_file_obj = paramiko.RSAKey.from_private_key_file(
                private_key_file_path
            )
            await loop.run_in_executor(
                None,
                lambda: ssh.connect(
                    hostname=self.details["target"],
                    username=self.details["ssh_username"],
                    pkey=private_key_file_obj,
                    timeout=5,
                ),
            )
            return self.service_check_priv
        except (paramiko.ssh_exception.NoValidConnectionsError, socket.timeout) as e:
            self.details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f"Request Timed Out after 4 seconds for host {self.service_check_priv.target_host}",
                staff_details=self.details,
            )
            return self.service_check_priv
        except paramiko.AuthenticationException as e:
            self.details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback=f"Could not Authneticate host: {self.service_check_priv.target_host} for the user",
                staff_details=self.details,
            )
            return self.service_check_priv

        except Exception as exc:
            self.details["raw"] = str(exc)
            self.service_check_priv.result.error(
                feedback="SSH Service Check Execution had an Exception: Call Staff",
                staff_details=self.details,
            )
            return self.service_check_priv

    def test_interactions(self, ssh: SSHClient):
        """Execute SSH Interactions"""

        stdin, stdout, stderr = ssh.exec_command(self.details["ssh_script"])
        # Read the standard output and print it
        # Now also handle the standard error
        stdout_data = stdout.read().decode()
        stderr_data = stderr.readlines()
        # grab all items from stdout, including spaces
        stdout_list = stdout_data.split(" ")
        retrieved_md5_sum = stdout_list[0]

        if self.details["md5_sum"] == retrieved_md5_sum:
            self.service_check_priv.result.success(
                feedback=f"SSH User: {self.details['ssh_username']} can do appropriate MD5check"
            )

        if len(stderr_data) != 0:
            self.details["ssh_error"] = stderr_data[0]

            self.service_check_priv.result.warn(
                feedback=f"Able to Connect: {self.details['target_host']}, SSH Script execution reported errors {stderr_data[0]}",
                staff_details=self.details,
            )

    async def execute(self):
        """Execute the SSH Check."""
        loop = asyncio.get_running_loop()

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            await self.test_connection(ssh_client, loop)

        except Exception as exc:
            print(exc)

        try:
            self.test_interactions(ssh_client)
        except Exception as exc:
            print(exc)

        return self.service_check_priv
