#!/usr/bin/env python3
import enum
import json
import sys
from typing import Optional, Union, Any, List
import argparse
import ping3
import json
import sys
import argparse
from pydantic import Field
from ImportEnvVars import load_env_vars


class ResultCode(enum.Enum):
    """
    String representing the result of a check
    """

    PASS = "success"
    FAIL = "failure"
    WARN = "partial"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"
    ERROR = "error"


class ResultJSONEncoder(json.JSONEncoder):
    """
    Encoder to handle converting result to JSON
    """

    def default(self, o):
        if hasattr(o, "reportJSON"):
            return o.reportJSON()
        if isinstance(o, ResultCode):
            return o.value
        return json.JSONEncoder.default(self, o)


class Feedback:
    """
    Holds Feedback from a script, either participant or staff details
    """

    def __init__(self):
        self.feedback = ""
        self._details = []

    @property
    def details(self):
        """Get Details."""
        return self._details

    def add_details(self, val: Union[List, Any]):
        """
        Add details to the Feedback. Accepts a value or list of values.
        """
        if isinstance(val, list):
            self._details.extend(val)
        else:
            self._details.append(val)


class FinalResult:
    def __init__(self):
        self._result: Optional[ResultCode] = None
        self._participant_result = Feedback()
        self._staff_result = Feedback()

    @property
    def result(self):
        """GET Result Code."""
        return self._result

    @result.setter
    def result(self, val: ResultCode):
        """Set Result Code. Verifies val is a valid ResultCode."""
        if not isinstance(val, ResultCode):
            raise ValueError("Result must be a ResultCode enum object")
        self._result = val

    @property
    def feedback(self) -> str:
        """Get Participant Feedback."""
        return self._participant_result.feedback

    @feedback.setter
    def feedback(self, val: str):
        """Set Participant Feedback. Verifies Feedback is a string."""
        if not isinstance(val, str):
            raise ValueError("feedback must be a string")
        self._participant_result.feedback = val

    @property
    def staff_feedback(self) -> str:
        """Get Staff Feedback."""
        return self._staff_result.feedback

    @staff_feedback.setter
    def staff_feedback(self, val: str):
        """Set Staff Feedback. Verifies Feedback is a string."""
        if not isinstance(val, str):
            raise ValueError("feedback must be a string")
        self._staff_result.feedback = val

    def add_detail(self, detail):
        """Add Participant Detail."""
        self._participant_result.add_details(detail)

    def add_staff_detail(self, detail):
        """Add Staff Detail."""
        self._staff_result.add_details(detail)

    def success(self, **kwargs):
        """Exit with Success (success) ResultCode."""
        self.exit(**kwargs, status=ResultCode.PASS)

    def warn(self, **kwargs):
        """Exit with Warning (partial) ResultCode."""
        self.exit(**kwargs, status=ResultCode.WARN)

    def fail(self, **kwargs):
        """Exit with Failed (failure) ResultCode."""
        self.exit(**kwargs, status=ResultCode.FAIL)

    def unknown(self, **kwargs):
        """Exit with Unknown ResultCode."""
        self.exit(**kwargs, status=ResultCode.UNKNOWN)

    def timeout(self, **kwargs):
        """Exit with Timeout ResultCode."""
        self.exit(**kwargs, status=ResultCode.TIMEOUT)

    def error(self, **kwargs):
        """Exit with Error ResultCode."""
        self.exit(**kwargs, status=ResultCode.ERROR)

    def exit(
        self,
        status: ResultCode,
        feedback=None,
        details=None,
        staff_feedback=None,
        staff_details=None,
    ):
        """
        Exit with specified result code, feedback, and details. Prints JSON to stdout and exits.
        """
        self.result = status
        if feedback:
            self.feedback = feedback
        if details:
            self.add_detail(details)
        if staff_feedback:
            self.staff_feedback = staff_feedback
        if staff_details:
            self.add_staff_detail(staff_details)

        # sys.exit(0)

    def json(self) -> str:
        """Dump results to JSON."""
        return json.dumps(self.__dict__, cls=ResultJSONEncoder)


class ServiceHealthCheck:
    target_host: str = ""
    result: FinalResult = FinalResult()
    args: argparse.Namespace
    parser: argparse.ArgumentParser

    def __init__(self, ip_host: str):
        self.target_host = ip_host
