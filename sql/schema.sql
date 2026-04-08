CREATE TABLE adolescents_argentina (
    id VARCHAR(255) PRIMARY KEY,
    country VARCHAR(255) NOT NULL,
    year INTEGER NOT NULL,
    value NUMERIC NOT NULL,
    unit VARCHAR(100),
    source TEXT,
    notes TEXT
);
