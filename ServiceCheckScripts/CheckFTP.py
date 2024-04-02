#!/usr/bin/env python3
import asyncio
from .Results import ServiceHealthCheck
from ftplib import FTP, all_errors as FTPError
import io


class FTPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the FTP Check."""

        details = {}
        details["target"] = self.service_check_priv.target_host

        if self.service_check_priv.ftp_info:
            details["username"] = self.service_check_priv.ftp_info.ftp_username
            details["password"] = self.service_check_priv.ftp_info.ftp_password
            details["directory"] = self.service_check_priv.ftp_info.directory
            details["files"] = self.service_check_priv.ftp_info.files

        else:
            return self.service_check_priv.result.fail(
                feedback=f"No FTP info given for target: {details['target']}",
                staff_details=details,
            )

        loop = asyncio.get_running_loop()
        # Check Connection to FTP server
        try:
            ftp = FTP(details["target"])
        except Exception as e:
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f"Failted to connect to {self.service_check_priv.target_host} over FTP.",
                staff_details=details,
            )
            return self.service_check_priv

        # Check user login
        try:
            ftp.login(details["username"], details["password"])
        except FTPError as e:
            details["raw"] = str(e)
            self.service_check_priv.result.unknown(
                feedback=f"Generic FTP Login Error, call staff for more details.",
                staff_details=details,
            )
            return self.service_check_priv
        except Exception as e:
            details["raw"] = str(e)
            self.service_check_priv.result.fail(
                feedback=f"Failed to authenticate FTP on host {details['target']} as user {details['username']}",
                staff_details=details,
            )
            return self.service_check_priv

        # User Logged On, try to do list operation
        try:
            ftp.login(details["username"], details["password"])
            ftp.cwd(details["directory"])
            response = ftp.retrlines("LIST")
        except FTPError as e:
            details["raw"] = e
            return self.service_check_priv.result.warn(
                feedback=f"Failed to retrieve data from host {details['target']} as user {details['username']}",
                staff_details=details,
            )
        except Exception as e:
            details["raw"] = e
            return self.service_check_priv.result.warn(
                feedback=f"Failed to retrieve data from host {details['target']} as user {details['username']}",
                staff_details=details,
            )

        return self.service_check_priv
