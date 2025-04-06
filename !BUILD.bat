md fonts_edited
mkdir atmosphere
cd atmosphere
mkdir contents
cd contents
mkdir 0100DCA0064A6000
cd 0100DCA0064A6000
mkdir RomFS
cd..
cd..
cd..
copy "fonts\*.dds" "fonts_edited\"
for %%F in ("fonts_edited\*.dds") do unrealTT.exe swizzle switch "fonts_edited\%%~nxF" 0x80 2048 512
python font_import.py
copy "0069.txt" "init_o/0069.txt"
python lm3_text.py i "init_o/0069.dat" "init_patch/0069.dat"
cd "init_o"
del "0105.txt"
ren "0069.txt" "0105.txt"
cd..
python lm3_text.py i "init_o/0105.dat" "init_patch/0105.dat"
replacer.exe "init_patch/0105.dat" 0 09000000
python lm3_dict.py
rmdir /s /q "fonts_edited"
move "init.dict" "atmosphere/contents/0100DCA0064A6000/RomFS/init.dict"
move "init.data" "atmosphere/contents/0100DCA0064A6000/RomFS/init.data"
@echo off

:: Получаем текущую дату
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "current_date=%dt:~0,8%"

:: Формируем имя архива
set "archive_name=LM3RC%current_date%"
:: Создаем архив 7-zip
7z a "%archive_name%.7z" "Atmosphere"
echo Packing %archive_name%.7z was OK.
PAUSE