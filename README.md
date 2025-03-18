# SERVICE:
    manager_sheets
    manager_sheets_telegram_bot -> /etc/supervisord.d/sheet_services.ini
    manager_sheets_watch_files -> /etc/supervisord.d/sheet_telegram_bot.ini
    /var/www/manager_sheets/venv/bin/python /var/www/manager_sheets/start_watch_sheets.py
    cat /var/log/watch_sheets.err.log
    cat /var/log/watch_sheets.out.log
    sudo nano /etc/supervisord.d/manager_sheets.ini