#!/usr/bin/python3
import sys,os,logging
from PyQt5.QtWidgets import QApplication, QDialog,QMainWindow
from ui_mainWindow import Ui_CeresEmulatorWindow
from nx3Emu import NX3Emu

EMU = False
def main():
    EMU = NX3Emu()
    EMU.start()
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
