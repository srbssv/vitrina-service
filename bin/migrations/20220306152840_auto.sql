-- migrate:up

CREATE TABLE booking (
    id VARCHAR(36),
    pnr VARCHAR(6),
    expires_at VARCHAR(32),
    phone VARCHAR(12),
    email VARCHAR(255),
    offer JSONB,
    PRIMARY KEY (id)
);

-- migrate:down

DROP TABLE booking;