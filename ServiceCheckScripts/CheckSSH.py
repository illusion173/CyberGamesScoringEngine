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
        # Initialize the SSHCheck object with a service_check instance and details dictionary.
        self.service_check_priv = service_check
        self.details = {"target": self.service_check_priv.target_host}

        # Populate the details dictionary with SSH information if available.
        if self.service_check_priv.ssh_info:
            self.details.update(
                {
                    "ssh_username": self.service_check_priv.ssh_info.ssh_username,
                    "ssh_priv_key": self.service_check_priv.ssh_info.ssh_priv_key,
                    "ssh_script": self.service_check_priv.ssh_info.ssh_script,
                    "md5_sum": self.service_check_priv.ssh_info.md5sum,
                }
            )
        else:
            # Exit the program if SSH information is missing.
            print("Error while retrieving SSH info for target", self.details["target"])
            sys.exit(0)

    def is_completely_empty_err(self, s):
        # Check if a given string is not just whitespace.
        return s.strip()

    async def test_connection(self, ssh: SSHClient, loop: asyncio.AbstractEventLoop):
        # Asynchronously attempt to establish an SSH connection to the target.
        try:
            # Load the private key from a file specified in the details.
            private_key_file_name = self.details["ssh_priv_key"]
            private_key_file_path = str(Path.home()) + "/" + private_key_file_name

            private_key_file_obj = paramiko.RSAKey.from_private_key_file(
                private_key_file_path
            )
            # Connect to the target host asynchronously.
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
            # Handle connection errors and timeouts, marking the result accordingly.
            self.details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f"Request Timed Out after 5 seconds for host {self.service_check_priv.target_host}",
                staff_details=self.details,
            )
            return self.service_check_priv
        except paramiko.AuthenticationException as e:
            # Handle authentication errors.
            self.details["raw"] = str(e)
            self.service_check_priv.result.error(
                feedback=f"Could not Authenticate host: {self.service_check_priv.target_host} for the user",
                staff_details=self.details,
            )
            return self.service_check_priv
        except Exception as exc:
            # Handle any other exceptions.
            self.details["raw"] = str(exc)
            self.service_check_priv.result.error(
                feedback="SSH Service Check Execution had an Exception: Call Staff",
                staff_details=self.details,
            )
            return self.service_check_priv

    def test_interactions(self, ssh: SSHClient):
        # Execute commands via SSH and process the output.
        stdin, stdout, stderr = ssh.exec_command(self.details["ssh_script"])

        stdout_data = stdout.read().decode()
        stderr_data = stderr.readlines()

        stdout_list = stdout_data.split(" ")
        retrieved_md5_sum = stdout_list[0]

        # Compare the retrieved MD5 sum with the expected value.
        if self.details["md5_sum"] == retrieved_md5_sum:
            self.service_check_priv.result.success(
                feedback=f"SSH User: {self.details['ssh_username']} can do appropriate MD5 check"
            )

        # Handle errors found in stderr.
        if len(stderr_data) != 0:
            self.details["ssh_error"] = stderr_data[0]
            self.service_check_priv.result.warn(
                feedback=f"Able to Connect: {self.details['target_host']}, SSH Script execution reported errors {stderr_data[0]}",
                staff_details=self.details,
            )

    async def execute(self):
        # Main method to execute the SSH check.
        loop = asyncio.get_running_loop()

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            # Test the connection to the target.
            await self.test_connection(ssh_client, loop)
        except Exception as exc:
            print(exc)
            return (
                self.service_check_priv
            )  # Return immediately if an error occurs during connection test.

        try:
            # Execute interactions if connection is successful.
            self.test_interactions(ssh_client)
        except Exception as exc:
            print(exc)

        return self.service_check_priv
