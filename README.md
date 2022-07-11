# scada_autotests_service_DB
Автоматическое тестирование модуля «Обслуживание БД» SCADA состоят из трёх тестов.

1) test_service_DB_auto.py
Данный тест создаёт дневные таблицы с 1 по 31 января 2000 года. Тест контролирует удаление таблиц, удаление файлов резервных копий и появление соответствующих
сообщений в журнале событий. 
Длительность примерно 33 минуты. 

2) test_service_DB_manual.py
Тест создаёт одну таблицу за 28 февраля 2000 года. Сохраняет значение сигнала в CSV-файл, затем удаляет созданную таблицу и восстанавливает её из файла резервной.
Затем из восстановленной таблицы создаётся CSV-файл сигналов. Оба файла сравниваются между с собой и с эталонным файлом, хранящимся на ПК. 
Все файлы должны быть одинаковы. Таким образом проверяется правильность информации при восстановлении таблиц.
Длительность около 2 минут.

3) test_service_DB_trend.py
В этом автотесте проверяется скорость загрузки тренда сигналов с очень большим количеством значений, которые получаются искусственно при помощи специальной утилиты.
На скорость загрузки влияет тот факт, что для построения графика нужно последнее значение сигнала вне запрашиваемого временного диапазона,
чтобы график не возникал из пустоты.
Данный тест создаёт таблицы сигналов за март 2000 года (одной операцией). Затем пытается построить таблицу значений за последний час (вкладка «База данных» SCADA)
в двух вариантах с поиском последнего значения и без поиска. Проверяется то, что без поиска последнего значения построение таблицы происходит быстрее,
а также проверяется правильность нахождения этого последнего значения. Полученная таблица должна быть пустой, так как строится по умолчанию за последний час,
в течение которого тестового сигнала не было.
Длительность около 12 минут.
