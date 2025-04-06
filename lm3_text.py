import struct
import sys

input_extension = '.dat'

def remap(text):
    mapping = {
    " - ":" — ",
    "t":"î",
    "А":"A",
    "Б":"À",
    "В":"B",
    "Г":"Á",
    "Д":"Ô",
    "Е":"E",
    "Ё":"È",
    "Ж":"Œ",
    "З":"3",
    "И":"Ñ",
    "Й":"É",
    "К":"K",
    "Л":"Ê",
    "М":"M",
    "Н":"H",
    "О":"O",
    "П":"Ë",
    "Р":"P",
    "С":"C",
    "Т":"T",
    "У":"Y",
    "Ф":"œ",
    "Х":"X",
    "Ц":"Õ",
    "Ч":"ß",
    "Ш":"Ó",
    "Щ":"Ç",
    "Ъ":"Ò",
    "Ы":"Ä",
    "Ь":"Û",
    "Э":"Â",
    "Ю":"Ü",
    "Я":"Ã",
    "а":"a",
    "б":"á",
    "в":"à",
    "г":"ò",
    "д":"ç",
    "е":"e",
    "ё":"ë",
    "ж":"~",
    "з":"ó",
    "и":"ñ",
    "й":"è",
    "к":"k",
    "л":"é",
    "м":"×",
    "н":"ê",
    "о":"o",
    "п":"ô",
    "р":"p",
    "с":"c",
    "т":"t",
    "у":"y",
    "ф":"Ö",
    "х":"x",
    "ц":"õ",
    "ч":"â",
    "ш":"Ù",
    "щ":"Ú",
    "ъ":"ö",
    "ы":"ù",
    "ь":"ú",
    "э":"û",
    "ю":"ü",
    "я":"ã",
    "îp":"tp"}
    for c, a in mapping.items():
        text = text.replace(c, a)
    return text

def align(f):
    cur = f.tell()
    if cur % 4 != 0:
        f.seek(cur + (4 - cur % 4))
def writewstr(f, string):
    pos = f.tell()
    f.write(string.encode('utf-16-le'))
    f.write(b'\x00\x00')
    return pos
def readwstr(f, pos):
    cur = f.tell()
    f.seek(pos)
    cstr = bytearray()
    while True:
        ch = f.read(2)
        if(ch == b'\x00\x00'):
            f.seek(cur)
            return str(cstr, "utf-16")
        cstr.extend(ch)

class LM3String:
    def __init__(self, f, textStartOffset, index):
        self.index = index
        self.id, self.pos = struct.unpack('<II', f.read(8))
        self.string = readwstr(f, textStartOffset + (self.pos * 2))


def read(file):
    f = open(file, 'rb')
    localeId, stringCount, unknown = struct.unpack('<III', f.read(12))
    textStartOffset = 12 + (stringCount * 8)
    entries = []
    for i in range(stringCount):
        entries.append(LM3String(f, textStartOffset, i))
    f.close()

    return sorted(entries, key=lambda x:x.pos)

def extract(file):
    entries = read(file)
    f = open(file.replace(input_extension, '.txt'), 'w', encoding='utf-8')
    for entry in entries:
        f.write(entry.string + '\n')
    f.close()

def build(ofile, nfile):
    entries = read(ofile)

    f = open(ofile.replace(input_extension, '.txt'), 'r', encoding='utf-8')
    new_text = f.readlines()
    f.close()

    if len(entries) != len(new_text):
        input("The strings from txt > binary: %d/%d", len(entries), len(new_text))
        return

    for i in range(len(entries)):
        entries[i].string = remap(new_text[i].strip('\n'))

    entries = sorted(entries, key=lambda x:x.index)
    textStartOffset = 12 + (len(entries) * 8)

    f = open(nfile, 'wb')
    f.write(struct.pack('<III', 0, len(entries), 0))
    f.seek(textStartOffset)
    for i in range(len(entries)):
        entries[i].pos = writewstr(f, entries[i].string) - textStartOffset
    f.seek(12)
    for entry in entries:
        f.write(struct.pack('<II', entry.id, entry.pos // 2))
    align(f)
    f.close()
    print('All OK')
def printUsage():
    print('USAGE:')
    print('Extract: tool.py e file.dat')
    print('Import: tool.py i file.dat file.new')
if len(sys.argv) < 2:
    printUsage()
    exit()
if sys.argv[1] == 'e': extract(sys.argv[2])
elif sys.argv[1] == 'i': build(sys.argv[2], sys.argv[3])
else: printUsage()