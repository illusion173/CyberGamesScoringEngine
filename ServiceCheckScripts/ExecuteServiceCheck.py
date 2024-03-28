import sys
from ServiceCheckScripts import CheckIcmp, CheckFTP, CheckSSH
from .Results import ServiceHealthCheck


async def arrange_service_check(service_check: ServiceHealthCheck):
    service_name = service_check.service_name

    match service_name:
        case "ICMP":
            service_check_result = await CheckIcmp.ICMPCheck(service_check).execute()
        case "FTP":
            service_check_result = await CheckFTP.FTPCheck(service_check).execute()
        case "SSH":
            service_check_result = await CheckSSH.SSHCheck(service_check).execute()
        case _:
            print("ERROR, No service or Port Inputted? Call Staff.")
            sys.exit(0)

    return service_check_result
