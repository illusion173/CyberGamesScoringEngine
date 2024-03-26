import sys
from ServiceCheckScripts import CheckIcmp, CheckFTP, CheckSSH


async def arrange_service_check(service_check):
    port = service_check.target_port

    match port:
        case "ICMP":
            print("ICMP CHECK")
            result = await CheckIcmp.ICMPCheck(service_check).execute()
        case "21":
            result = ""
            print("FTP CHECK")
            # Handle other cases similarly
            result = await CheckFTP.FTPCheck(service_check).execute()
        case "22":
            result = ""
            print("SSH CHECK")
            result = await CheckSSH.SSHCheck(service_check).execute()
        case _:
            print("ERROR, No service or Port Inputted?")
            sys.exit(0)

    return result
