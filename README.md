learn.csv - обучающая выборка 
test.csv - тестовая выборка

users.csv - общий набор данных

обучить и протестировать:
python lrmgd.py learn.csv userfilt.csv
кросс-валидация:
python lrmgd.py cross-val users.csv

получить информацию из vkontakte:
python vk.py
Результат можно найти в users.csv
При желании можно отфильтровать его  filter.py users.csv usersfilt.csv
Фильтер оставляет лишь тех, у кого доступна вся нужная информция
