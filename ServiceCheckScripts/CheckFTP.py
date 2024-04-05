#!/usr/bin/env python3
import asyncio
from ftplib import FTP, all_errors as FTPError  # Import FTP client and error handling.
import hashlib  # For generating md5 hashes to verify file integrity.
import os  # To handle file paths.
from .Results import ServiceHealthCheck  # Import a custom results handler.


class FTPCheck:
    def __init__(self, service_check: ServiceHealthCheck):
        # Initialize with a service check object containing necessary details for the FTP check.
        self.service_check_priv = service_check

    async def execute(self):
        """Asynchronously execute the FTP Check."""
        # Prepare FTP details required for the check.
        details = self._prepare_details()

        # If FTP details are missing, return an error immediately.
        if not details:
            return self.service_check_priv.result.error(
                feedback=f"No FTP info given for target: {self.service_check_priv.target_host}",
                staff_details=details,
            )

        loop = asyncio.get_running_loop()

        # Attempt to connect to the FTP server.
        try:
            ftp = await loop.run_in_executor(None, lambda: self._connect_ftp(details))
        except Exception as e:
            # Handle any connection errors.
            return self._handle_ftp_error(e, details, action="connect")

        # Try to log in to the FTP server.
        try:
            await self._login_ftp(ftp, details)
        except Exception as e:
            # Handle any login errors and ensure the connection is closed before returning.
            service_check_login_error = self._handle_ftp_error(
                e, details, action="login"
            )
            ftp.close()
            return service_check_login_error

        # Based on the specified FTP action (GET or PUT), handle the respective operations.
        match details["ftp_action"]:
            case "GET":
                # Handle file downloading, then close the connection.
                get_service_check = await self._handle_get_action(ftp, details, loop)
                ftp.close()
                return get_service_check
            case "PUT":
                # Handle file uploading, then close the connection.
                put_service_check = await self._handle_put_action(ftp, details, loop)
                ftp.close()
                return put_service_check
            case _:
                # If no valid action is specified, close the connection and return.
                if ftp:
                    ftp.close()
                return self.service_check_priv

    def _prepare_details(self):
        """Prepare and return FTP details from the service check object."""
        # Extract FTP info from the service check object, if available.
        if self.service_check_priv.ftp_info:
            ftp_info = self.service_check_priv.ftp_info
            # Construct and return a details dictionary with necessary information for the FTP operation.
            return {
                "target": self.service_check_priv.target_host,
                "username": ftp_info.ftp_username,
                "password": ftp_info.ftp_password,
                "directory": ftp_info.directory,
                "files": ftp_info.files,
                "sums": ftp_info.md5_sums,
                "ftp_action": ftp_info.ftp_action,
            }
        return None  # Return None if no FTP info is available.

    def _connect_ftp(self, details):
        """Establish a connection to the FTP server."""
        ftp = FTP(details["target"])
        return ftp

    async def _login_ftp(self, ftp, details):
        """Login to the FTP server using provided credentials."""
        ftp.login(user=details["username"], passwd=details["password"])

    def _handle_ftp_error(self, error, details, action="operation"):
        """Handle and report FTP errors based on the action being performed."""
        details["raw"] = str(error)
        feedback = f"Failed to {action} on host {details['target']} as user {details['username']}, error: {error}"
        # Differentiate handling based on whether the error occurred during login or another operation.
        if action == "login":
            return self.service_check_priv.result.warn(
                feedback=feedback, staff_details=details
            )
        return self.service_check_priv.result.fail(
            feedback=feedback, staff_details=details
        )

    async def _handle_get_action(self, ftp, details, loop):
        """Handle GET action for FTP, including file integrity checks."""
        # Lists to track the success and failure of file transfers.
        failed_files = []
        success_files = []
        for index, file in enumerate(details["files"]):
            try:
                file_hash = hashlib.md5()
                # Execute the file download and hashing in an executor to prevent blocking.
                await loop.run_in_executor(
                    None,
                    lambda: ftp.retrbinary(f"RETR {file}", file_hash.update),
                )
                # Compare the computed hash with the expected hash to verify file integrity.
                if file_hash.hexdigest() == details["sums"][index]:
                    success_files.append(file)
                else:
                    failed_files.append(file)
            except FTPError as e:
                # Record any FTP-specific errors.
                failed_files.append(file)
                self.service_check_priv.result.add_staff_detail({file: e})
            except Exception as e:
                # Record any other errors that may occur.
                failed_files.append(file)
                self.service_check_priv.result.add_staff_detail({file: e})

        # Generate feedback based on the success or failure of file downloads.
        details["successful_files"] = success_files

        if failed_files:
            failed_file_string = ", ".join(failed_files)
            return self.service_check_priv.result.warn(
                feedback=f"Failed either to retrieve or pass integrity check on the following file(s): {failed_file_string} \nAs user: {details['username']}",
                staff_details=details,
            )
        return self.service_check_priv.result.success(
            feedback=f"Successful Downloading of files as user {details['username']}",
            staff_details=details,
        )

    async def _handle_put_action(self, ftp, details, loop):
        """Handle PUT action for FTP, including file upload."""
        # Prepare the base path for files to be uploaded.
        file_base_path = os.getcwd() + "/test_items/ftp_test_items/"
        failed_files = []
        success_files = []
        for file_name in details["files"]:
            file_path = os.path.join(file_base_path, file_name)
            try:
                # Upload the file, executing the upload operation in an executor to prevent blocking.
                await loop.run_in_executor(
                    None, lambda: self._upload_file(ftp, file_path, file_name)
                )
                success_files.append(file_name)
            except Exception as e:
                failed_files.append(file_name)
                self.service_check_priv.result.add_staff_detail({file_name: str(e)})
        details["successful_files"] = success_files

        # Generate feedback based on the success or failure of file uploads.
        if failed_files:
            return self._handle_file_transfer_error(failed_files, details)

        return self.service_check_priv.result.success(
            feedback=f"Successful writing of files as user {details['username']}",
            staff_details=details,
        )

    def _upload_file(self, ftp, file_path, file_name):
        """Upload a specific file to the FTP server."""
        with open(file_path, "rb") as file:
            ftp.storbinary(f"STOR {file_name}", file)

    def _handle_file_transfer_error(self, failed_files, details):
        """Generate feedback for file transfer errors."""
        failed_file_string = ", ".join(failed_files)
        return self.service_check_priv.result.warn(
            feedback=f"Failed to transfer the following file(s): {failed_file_string} \nAs user: {details['username']}",
            staff_details=details,
        )
