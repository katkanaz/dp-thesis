#TODO: credit
from subprocess import STDOUT, Popen, PIPE
from time import time
import os

class Pymol():
    def __init__(self, gui = False) -> None:
        cmd = "pymol -p" if gui else "pymol -pc"

        # Launch PyMOL subprocess
        self.pymol = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE)
        os.set_blocking(self.pymol.stdout.fileno(), False)

    def __del__(self) -> None:
        self.pymol.stdin.close() # type: ignore
        self.pymol.wait()
        self.pymol.terminate()

    def __call__(self, command: str) -> list[str]:
        self.pymol.stdin.write((command + "\n").encode())
        self.pymol.stdin.flush()

        # return [l.decode("utf-8").rstrip("\n") for l in iter(self.pymol.stdout.readlines())]

        # print(self.pymol.stdout.readlines())

        

        outputs = []
        last_line = time()
        while True:
            l = self.pymol.stdout.readline()
            l_str = l.decode("utf-8")
            if l_str != "":
                outputs.append(l_str)
                # print(">>>", l_str)
                last_line = time()
            if time() - last_line > 0.4:
                print("===== timeout =====")
                break
        print(outputs)
        return outputs
