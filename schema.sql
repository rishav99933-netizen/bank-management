CREATE DATABASE IF NOT EXISTS bank_management;
USE bank_management;

CREATE TABLE IF NOT EXISTS accounts (
    account_no INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone_no VARCHAR(10) NOT NULL UNIQUE,
    address VARCHAR(255) NOT NULL,
    account_type VARCHAR(20) NOT NULL,
    balance DECIMAL(12,2) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,
    account_no INT NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_transactions_account
        FOREIGN KEY (account_no) REFERENCES accounts(account_no)
        ON DELETE RESTRICT ON UPDATE CASCADE
);
