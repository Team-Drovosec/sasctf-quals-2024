folder = r'dumped_mem'

from os import listdir
from os.path import isfile, join

onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]

for filename in onlyfiles:
    if ".dmp" in filename:
        name_split = filename.replace("pid.1536.vad.", "").replace(".dmp", "").split("-")
        filename_end = int(name_split[-1], 16)
        filename_start = int(name_split[-2], 16)
        idc.AddSeg(filename_start, filename_end, 0, 1, 0, idaapi.scPub)
        idc.SetSegClass(filename_start, 'CODE')
        SetRegEx(filename_start, "ds", 0, SR_user)
        with open(join(folder, filename), 'rb') as f:
            a = f.read()
            idaapi.put_many_bytes(filename_start, a)
