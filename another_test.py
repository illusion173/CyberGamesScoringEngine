import ping3

response = ping3.ping("10.187.125.55", timeout=4)
print(type(response))
print(f"Ping response: {response}")
