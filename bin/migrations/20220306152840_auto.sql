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

CREATE TABLE passengers (
    gender CHAR(1),
    type CHAR(3),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    date_of_birth CHAR(10),
    citizenship CHAR(2),
    document JSONB,
    booking_id VARCHAR(36) NOT NULL,
    FOREIGN KEY (booking_id) REFERENCES booking(id)
);
-- migrate:down

DROP TABLE booking;
DROP TABLE passengers;