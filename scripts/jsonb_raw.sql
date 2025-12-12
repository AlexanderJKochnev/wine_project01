-- создание столбца metadata_json -- все делаетсяя через alembic
ALTER TABLE rawdatas ADD COLUMN metadata_json JSONB;
--  заполнение столбца metadata_json
UPDATE rawdatas SET metadata_json = parsed_data::jsonb;

ALTER TABLE rawdatas DROP COLUMN parsed_data;

CREATE INDEX rawdata_trigram_idx_combined ON rawdatas USING GIN ((metadata_json ->> 'name') gin_trgm_ops);

-- ALTER TABLE rawdatas RENAME COLUMN metadata_json TO parsed_data;