# DOCS/trigram_index.md
1. trigram index (применяется в Drink)
   1. Как проверить подкючение trigram
       SELECT *
       FROM pg_extension;
   2. Как проверить наличие индекса:
       SELECT tablename, indexname, indexdef
       FROM pg_indexes
       WHERE tablename = 'drinks' AND indexname = 'drink_trigram_idx_combined';
   3. как создать индекс
      sh create_trigram.sh
   4. как проверить что поиск идет с триграммным индексом
   5. 
2. FTS index (полнотекстовый индекс применяется в Rawdata)
   1. см. Rawdata - порядок строго следующий (для большых данных):
      1. сначала копируются все данные которые должны быть
      2. затем создаются столбцы для ts векторов - на каждый язык свой nullable = True
      3. и индексы
      4. потом у векторов nullable меняется на False

3. как проверить что используется инлдекс
   EXPLAIN ANALYZE
   SELECT parsed_data
   FROM rawdatas
   WHERE fts_russian @@ to_tsquery('russian', 'водка'); 
4. Bitmap Heap Scan on rawdatas (cost=12.82..16.83 rows=1 width=991) (actual time=7.325..21.540 rows=223 loops=1)
Recheck Cond: (fts_russian @@ '''водк'''::tsquery)
Heap Blocks: exact=34
-> Bitmap Index Scan on idx_products_fts_russian (cost=0.00..12.82 rows=1 width=0) (actual time=3.590..3.591 rows=223 loops=1)
Index Cond: (fts_russian @@ '''водк'''::tsquery)
Planning Time: 212.409 ms
Execution Time: 21.755 ms