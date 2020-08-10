import os

mypath = "D:\\tmp\\dir"
import glob
files = glob.glob(mypath + '\\*.xlsx')
print(files)
for f in files:
    print(os.path.splitext(f)[0])