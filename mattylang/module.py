from mattylang.diagnostics import Diagnostics


class Module:
    def __init__(self, file: str, source: str, verbose: bool = False) -> None:
        self.__file = file
        self.__source = source
        self.__diagnostics = Diagnostics(verbose)

    def get_file(self) -> str:
        return self.__file

    def get_source(self) -> str:
        return self.__source

    def get_diagnostics(self) -> Diagnostics:
        return self.__diagnostics
