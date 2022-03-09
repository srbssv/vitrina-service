-- migrate:up

CREATE TABLE passengers (
    passenger_id SERIAL PRIMARY KEY,
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

DROP TABLE passengers;