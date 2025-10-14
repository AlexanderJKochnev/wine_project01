# Benchmark проверки IP
import time


def check_ip_speed(host):
    start = time.time()
    internal_prefixes = ["127.0.0.1", "172.", "192.168.", "10.", "frontend"]
    for prefix in internal_prefixes:
        if host.startswith(prefix):
            break
    return time.time() - start
