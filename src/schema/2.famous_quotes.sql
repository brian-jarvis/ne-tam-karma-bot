
CREATE TABLE IF NOT EXISTS famous_quotes (
  quote_id INTEGER NOT NULL PRIMARY KEY,
  dt_added TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  quote_tx TEXT NOT NULL UNIQUE,
  author TEXT NOT NULL,
  added_by TEXT NOT NULL,
  quote_type TEXT NOT NULL CHECK (quote_type IN ('fame', 'redhat', 'nerd', 'nerd-excuse')),
  quote_src TEXT NULL,
  is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);
