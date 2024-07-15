explain in chinese:@echo OFF

cd "D:\vt-dlp\vt-dlp"

title Enter URL to Download

set /p URL=URL:

cls

title Enter File Format

set /p format=Audio (a) or Video (v)?:

cls

title Downloading...

if %format%==a yt-dlp.exe -P "D:\vt-dlp\vt-dlp downloads" -x --audio-format "mp3" -f "ba/b" -o "%%(title)s.%%(ext)s" -w %URL%

if %format%==v yt-dlp.exe -P "D:\vt-dlp\vt-dlp downloads" -f "bv+ba/b" -o "%%(title)s.%%(ext)s" -w %URL%

if %format%==a @echo Audio - %URL%>>"D:\vt-dlp\vt-dlp\log.txt"

if %format%==v @echo Video - %URL%>>"D:\vt-dlp\vt-dlp\log.txt"

cls

title Download more?

set /p more=Do you want to download more? Yes (y) or No (n):

if %more%==y start Run.bat

if %more%==y exit

if %more%==n goto b

:b

explorer "D:\vt-dlp\vt-dlp downloads"

exit