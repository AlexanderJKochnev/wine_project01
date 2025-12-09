# DOCS/trigram_index.md

1. Как проверить подкючение trigram
    SELECT *
    FROM pg_extension;
2. Как проверить наличие индекса:
    SELECT tablename, indexname, indexdef
    FROM pg_indexes
    WHERE tablename = 'drinks' AND indexname = 'drink_trigram_idx_combined';
3. как создать индекс
   sh create_trigram.sh
