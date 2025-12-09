-- create_index.sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS drink_trigram_idx_combined
ON drinks
USING gin (
    (
        coalesce(title, '') || ' ' ||
        coalesce(title_ru, '') || ' ' ||
        coalesce(title_fr, '') || ' ' ||
        coalesce(subtitle, '') || ' ' ||
        coalesce(subtitle_ru, '') || ' ' ||
        coalesce(subtitle_fr, '') || ' ' ||
        coalesce(description, '') || ' ' ||
        coalesce(description_ru, '') || ' ' ||
        coalesce(description_fr, '') || ' ' ||
        coalesce(recommendation, '') || ' ' ||
        coalesce(recommendation_ru, '') || ' ' ||
        coalesce(recommendation_fr, '') || ' ' ||
        coalesce(madeof, '') || ' ' ||
        coalesce(madeof_ru, '') || ' ' ||
        coalesce(madeof_fr, '')
    )
    gin_trgm_ops
);