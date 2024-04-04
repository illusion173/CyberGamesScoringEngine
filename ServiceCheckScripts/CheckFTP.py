#!/usr/bin/env python3
import asyncio
from ftplib import FTP, all_errors as FTPError
import hashlib
import os
from .Results import ServiceHealthCheck


class FTPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        self.service_check_priv = service_check

    async def execute(self):
        """Execute the FTP Check."""
        details = self._prepare_details()

        if not details:
            return self.service_check_priv.result.fail(
                feedback=f"No FTP info given for target: {self.service_check_priv.target_host}",
                staff_details=details,
            )

        loop = asyncio.get_running_loop()

        # Establish FTP connection
        try:
            ftp = await loop.run_in_executor(None, lambda: self._connect_ftp(details))
        except Exception as e:
            return self._handle_ftp_error(e, details, action="connect")

        try:
            await self._login_ftp(ftp, details)
        except Exception as e:
            return self._handle_ftp_error(e, details, action="login")

        # Execute FTP action (GET or PUT)
        if details["ftp_action"] == "GET":
            return await self._handle_get_action(ftp, details, loop)
        elif details["ftp_action"] == "PUT":
            return await self._handle_put_action(ftp, details, loop)

        ftp.close()
        return self.service_check_priv

    def _prepare_details(self):
        """Prepare the FTP details from the service check."""
        details = {}
        if self.service_check_priv.ftp_info:
            ftp_info = self.service_check_priv.ftp_info
            details.update(
                {
                    "target": self.service_check_priv.target_host,
                    "username": ftp_info.ftp_username,
                    "password": ftp_info.ftp_password,
                    "directory": ftp_info.directory,
                    "files": ftp_info.files,
                    "sums": ftp_info.md5_sums,
                    "ftp_action": ftp_info.ftp_action,
                }
            )
            return details

        return None

    def _connect_ftp(self, details):
        """Connect to the FTP server."""
        ftp = FTP(details["target"])
        return ftp

    async def _login_ftp(self, ftp, details):
        """Login to the FTP server."""
        ftp.login(user=details["username"], passwd=details["password"])

    def _handle_ftp_error(self, error, details, action="operation"):
        """Handle FTP errors."""
        details["raw"] = str(error)
        feedback = f"Failed to {action} on host {details['target']} as user {details['username']}, error: {error}"
        if action == "login":
            return self.service_check_priv.result.warn(
                feedback=feedback, staff_details=details
            )
        return self.service_check_priv.result.fail(
            feedback=feedback, staff_details=details
        )

    async def _handle_get_action(self, ftp, details, loop):
        """Handle GET action for FTP."""
        # User can read, now try to retrieve a file.
        failed_files = []
        success_files = []
        for index, file in enumerate(details["files"]):
            try:
                file_hash = hashlib.md5()
                result = loop.run_in_executor(
                    None,
                    lambda: ftp.retrbinary(f"RETR {file}", file_hash.update),
                )
                if file_hash.hexdigest() == details["sums"][index]:
                    success_files.append(file)
                else:
                    failed_files.append(file)

            except FTPError as e:
                failed_files.append(file)
                self.service_check_priv.result.add_staff_detail({file: e})
            except Exception as e:
                failed_files.append(file)
                self.service_check_priv.result.add_staff_detail({file: e})
        if failed_files:
            ftp.close()
            failed_file_string = ", ".join(failed_files)
            details["successful_files"] = success_files
            return self.service_check_priv.result.warn(
                feedback=f"Failed either to retrieve or pass integrity check on the following file(s): {failed_file_string} \nAs user: {details['username']}",
                staff_details=details,
            )
        details["successful_files"] = success_files
        return self.service_check_priv.result.success(
            feedback=f"Successful Downloading of files as user {details['username']}",
            staff_details=details,
        )

    async def _handle_put_action(self, ftp, details, loop):
        """Handle PUT action for FTP."""
        file_base_path = os.getcwd() + "/test_items/ftp_test_items/"
        failed_files = []
        success_files = []
        for file_name in details["files"]:
            file_path = os.path.join(file_base_path, file_name)
            try:
                await loop.run_in_executor(
                    None, lambda: self._upload_file(ftp, file_path, file_name)
                )
                success_files.append(file_name)
            except Exception as e:
                failed_files.append(file_name)
                self.service_check_priv.result.add_staff_detail({file_name: str(e)})

        if failed_files:
            ftp.close()
            return self._handle_file_transfer_error(
                failed_files, success_files, details
            )

        details["successful_files"] = success_files
        return self.service_check_priv.result.success(
            feedback=f"Successful writing of files as user {details['username']}",
            staff_details=details,
        )

    def _upload_file(self, ftp, file_path, file_name):
        """Upload a file to the FTP server."""
        with open(file_path, "rb") as file:
            ftp.storbinary(f"STOR {file_name}", file)

    def _handle_file_transfer_error(self, failed_files, success_files, details):
        """Handle errors occurred during file transfer."""
        failed_file_string = ", ".join(failed_files)
        details["successful_files"] = success_files
        return self.service_check_priv.result.warn(
            feedback=f"Failed to transfer the following file(s): {failed_file_string} \nAs user: {details['username']}",
            staff_details=details,
        )
