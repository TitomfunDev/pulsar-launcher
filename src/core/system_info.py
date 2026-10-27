# External dependencies
import platform

def get_system_name():
    system = platform.system().lower()
    if system == "darwin":
        return "mac"
    return system


def get_system_architecture():
    architecture = platform.machine()

    if architecture == "x86_64" or architecture == "AMD64":
        return "x64"
    elif architecture == "aarch64" or architecture == "arm64":
        return "aarch64"
    elif architecture in ["x86", "i386", "i686"]:
        return "x86"
    elif architecture.startswith("arm"):
        return "arm"
    else:
        return architecture.lower()