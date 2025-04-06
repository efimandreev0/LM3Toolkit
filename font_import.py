count = 3
files = ["alor_normal.ddsraw_swizzled_switch.dat", "hanzel_bold.ddsraw_swizzled_switch.dat", "hanzel_normal.ddsraw_swizzled_switch.dat"]
offsets = [0x0, 0x140000, 0x280000]
dds_start = 0x0
width = 2048
height = 512

def importSwizzledPixels(fontsPath, outFile):
    for i in range(count):
        files[i] = fontsPath + '\\' + files[i]
        print('%s => %s' % (files[i], outFile))
        f = open(files[i], 'rb')
        f.seek(dds_start)
        pixelData = f.read(width * height)
        f.close()
        f = open(outFile, 'rb+')
        f.seek(offsets[i])
        f.write(pixelData)
        f.close()

importSwizzledPixels('fonts_edited', 'init_patch\\0071.dat')