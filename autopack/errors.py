class AutoPackError(Exception):
    pass


class AutoPackFetchError(AutoPackError):
    pass


class AutoPackNotFoundError(AutoPackError):
    pass


class AutoPackNotInstalledError(AutoPackError):
    pass


class AutoPackLoadError(AutoPackError):
    pass


class AutoPackInstallationError(AutoPackError):
    pass
