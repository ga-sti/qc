import os
DEST_FOLDER = r"C:\QC_Auto"
INFO_TXT = os.path.join(DEST_FOLDER, "info_sistema.txt")

BASE_DIR = os.path.dirname(__file__)
PLANTILLA_PC = os.path.join(BASE_DIR, 'QCPC.xlsx')
PLANTILLA_LAPTOP = os.path.join(BASE_DIR, 'QCLAPTOP.xlsx')
