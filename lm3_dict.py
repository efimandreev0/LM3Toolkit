import struct
import zlib
import os
import glob
import shutil

extensions = ['.data', '.debug', '.nxpc']

def align(f):
    cur = f.tell()
    if cur % 8 != 0:
        f.seek(cur + (8 - cur % 8))
        

def readFileToEnd(path):
    f = open(path, 'rb')
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.seek(0, os.SEEK_SET)
    data = f.read(size)
    f.close()
    return data
    

class FileInfo:
    def __init__(self, f):
        self.pos = f.tell()
        self.offset, self.size, self.zsize, self.val0xC, self.val0xD, self.storingMode, self.isPatched = struct.unpack('<IIIbbbb', f.read(16))
        self.archiveExtension = extensions[self.storingMode]

    def write(self, f):
        f.seek(self.pos)
        f.write(struct.pack('<IIIbbbb', self.offset, self.size, self.zsize, self.val0xC, self.val0xD, self.storingMode, self.isPatched))

    def __str__(self):
        return '%0.8x %d %s (%d flag: %i)' % (self.offset, self.zsize, self.archiveExtension, self.val0xC, self.isPatched)

class Dictionary:
    def __init__(self, f):
        self.entries = []
        self.magic, self.val0x4, self.val0x5, self.compression, self.val0x7 = struct.unpack('<I4b', f.read(8))
        self.val0x8, self.fileCount, self.chunkCount, self.footerStringsCount, self.val0xF = struct.unpack('<I4b', f.read(8))
        f.seek(0x10 + (self.chunkCount * 0x18))
        for i in range(self.fileCount):
            self.entries.append(FileInfo(f))

def extract(dictFile):
    f = open(dictFile, 'rb')
    dict = Dictionary(f)
    f.close()
    c = 0
    path = dictFile.split('.')[0]
    if not os.path.exists(path):
        os.makedirs(path)
    for entry in dict.entries:
        if entry.size == 0 or entry.storingMode > 0:
            print('Skipped: %d: %s' % (c, entry))
            c += 1
            continue
        print('Extracting: %d: %s' % (c, entry))
        f = open(dictFile.replace('.dict', entry.archiveExtension), 'rb')
        f.seek(entry.offset)
        data = f.read(entry.zsize)
        if dict.compression:
            data = zlib.decompress(data)
        f.close()
        f = open('%s/%0.4d.dat' % (path, c), 'wb')
        f.write(data)
        f.close()
        c += 1

def reimport(originalDict, inputDir, newDict):
    files = [f for f in glob.glob('%s/*.dat' % inputDir)]
    shutil.copyfile(originalDict, newDict)
    shutil.copyfile(originalDict.replace('.dict', '.data'), newDict.replace('.dict', '.data'))
    dict_rw = open(newDict, 'rb+')
    data_rw = open(newDict.replace('.dict', '.data'), 'rb+')
    data_rw.seek(0, os.SEEK_END)
    dict = Dictionary(dict_rw)
    for file in files:
        print('Importing: %s' % file)
        spl = file.replace('/', '\\').split('\\')
        fileIndex = int(spl[len(spl)-1][:4])
        if fileIndex > dict.fileCount:
            input('file index > dict iteration' % spl[len(spl)-1])
            exit()
        data = readFileToEnd(file)
        compressed = zlib.compress(data)
        align(data_rw)
        entry = dict.entries[fileIndex]
        entry.offset = data_rw.tell()
        entry.size = len(data)
        entry.zsize = len(compressed)
        entry.isPatched = 0
        entry.write(dict_rw)
        dict.entries[fileIndex] = entry

        data_rw.write(compressed)
def printUsage():
    print('USAGE:')
    print('Extract: tool.py e file.dict')
    print('Import: tool.py i dict.orig dirWithFiles dict.new')
if len(sys.argv) < 2:
    printUsage()
    exit()
if sys.argv[1] == 'e': extract(sys.argv[2])
elif sys.argv[1] == 'i': build(sys.argv[2], sys.argv[3], sys.argv[4])
else: printUsage()
#reimport('init_o.dict', 'init_patch', 'init.dict')