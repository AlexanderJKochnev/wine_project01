-- clear_data.sql
-- очищает базу данных postgresql
-- Отключаем триггеры для избежания ошибок FK
SET session_replication_role = 'replica';

-- Удаляем данные из всех таблиц (кроме users)
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
        AND tablename NOT IN ('users', 'alembic_version')
    ) LOOP
        EXECUTE 'DELETE FROM ' || quote_ident(r.tablename) || ' CASCADE';
        RAISE NOTICE 'Cleared table: %', r.tablename;
    END LOOP;
END $$;

-- Включаем триггеры обратно
SET session_replication_role = 'origin';

-- Очищаем последовательности (сбрасываем autoincrement)
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT sequencename
        FROM pg_sequences
        WHERE schemaname = 'public'
        AND sequencename NOT LIKE '%users%'
    ) LOOP
        EXECUTE 'ALTER SEQUENCE ' || quote_ident(r.sequencename) || ' RESTART WITH 1';
        RAISE NOTICE 'Reset sequence: %', r.sequencename;
    END LOOP;
END $$;