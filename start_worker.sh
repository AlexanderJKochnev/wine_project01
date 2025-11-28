#!/bin/sh
# start_worker.sh
# Используем exec, чтобы заменить текущий процесс оболочки процессом arq
exec arq app.support.parser.worker