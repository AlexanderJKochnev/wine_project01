# структура SQL базы данных
1. Drink (напиток) (поля с 1 по 5 есть в каждой таблице далее они не указываются)
   1. Name/Title (уникальное поле однозначно определяющее запись) англ
   2. Description (описание) англ
   3. Name_ru (название на русском - для других языков - меняется суффикс)
   4. Decription_ru (описание на русском - для других языков - меняется суффикс)
   5. Created_at: (дата создания записи)
   6. Updated_at: (дата редактирования записи)
   7. User_id (пользователь внесший запись/изменения -  насколько это нужно? или серъезную систему журналирования сделать?)
   8. Subtitle (название на англ - для других языков -добавлятеся суффикс)
   9. alc
   10. aging
   11. sugar (проценты и )
   12. Sugar_id (сухое/полусухое/полусладкое/сладкое)
   13. recommendation ?
   14. Type_id ONETOMANY
   15. Made_of_id ONETOMANY
   16. Category_id ONETOMANY
   17. Region_id ONETOMANY
   18. Varietal_id MANYTOMANY
   19. Pairing_id MANYTOMANY
2. *Bottle (конкретная бутылка)
   1. Volume 
   2. Price
   3. Drink_id ONETOMANY
   4. Shelf_id ONETOMANY
   5. WineShop_id ONETOMANY
3. *Warehouse (конкретный склад/винный шкаф)
   1. Customer_id ONETOMANY
4. -WineShop (магазин где было приобретено вино)
5. *Customer: (пользователь) *
6. *Category (категория напитка) *
7. Region (регион)
   1. Country_id
8. *Country *
9. Raw material/Varietal (сырье для производства напитка)
10. *Food (Pairing)
11. Type: тип ?
12. madeOf "Изготовлено из" ?
