@echo off
set "CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe"
set "USERDATA=%USERPROFILE%\AppData\Local\Google\Chrome\User Data\Profile 25"

start "" "%CHROME%" ^
    --remote-debugging-port=9222 ^

    --user-data-dir="%USERDATA%" 
