# RandomGiftBot

Данный бот шлет напоминания о том, что нужно подарить подарки/цветы своим близким. Например, девушке/жене/etc.
Напоминания отправляются в случайный день в выбранном диапазоне.

## Конфигурация
Создайте файл `user_config.ini` и заполните его. Например:
```
[sqlite3]
db_file=rand_gift.db
sql_scripts=./sql_scripts

[bot]
bot_tg_token=ID бота

[debug]
debug=False
debug_tg_id=-1
```
