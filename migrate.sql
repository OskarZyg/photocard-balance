CREATE TABLE IF NOT EXISTS oyster_balance
(
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    oyster_card_number  CHAR(12)                           NOT NULL,
    oyster_card_balance REAL                               NOT NULL,
    time                DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
);
