#!/usr/bin/env python3
import asyncio
from .Results import ServiceHealthCheck
import sys
import paramiko
import paramiko.ssh_exception
import socket
import io


class SSHCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the SSH Check."""
        details = {"target": self.service_check_priv.target_host}
        if self.service_check_priv.ssh_info:
            details["ssh_username"] = self.service_check_priv.ssh_info.ssh_username
            details["ssh_priv_key"] = self.service_check_priv.ssh_info.ssh_priv_key
            details["ssh_pub_key"] = self.service_check_priv.ssh_info.ssh_pub_key
        else:
            print("Error while retrieving SSH info for target %s", details["target"])
            sys.exit(0)
        # Assuming 'details["ssh_priv_key"]' contains the private key as a string
        private_key_str = details["ssh_priv_key"]
        private_key_file_obj = io.StringIO(private_key_str)
        private_key = paramiko.RSAKey.from_private_key(private_key_file_obj)

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
                    pkey=private_key,
                    timeout=5,
                ),
            )
            ssh.exec_command("exit 0")
        except (paramiko.ssh_exception.NoValidConnectionsError, socket.timeout) as e:
            print(e)
        except paramiko.AuthenticationException as e:
            print(e)
        except Exception as exc:
            print(exc)
        finally:
            ssh.close()

        self.service_check_priv.result.success(
            feedback=f"Successful to SSH to host {self.service_check_priv.target_host} for user {self.service_check_priv.ssh_info.ssh_username}"
        )
        return self.service_check_priv
