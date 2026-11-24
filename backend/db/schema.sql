CREATE DATABASE IF NOT EXISTS face_recognition_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE face_recognition_db;

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email_or_phone VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL, -- TODO: verify role values (user/admin) in existing data
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_email_or_phone (email_or_phone),
    KEY idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS authority (
    authority_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    authority_type VARCHAR(100) NOT NULL,
    authority_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    location VARCHAR(255) NOT NULL,
    license_number VARCHAR(100) NULL, -- TODO: verify existing production length
    status VARCHAR(20) NOT NULL DEFAULT 'pending', -- TODO: verify pending/approved/rejected values
    document VARCHAR(255) NULL, -- TODO: verify existing production path length
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (authority_id),
    UNIQUE KEY uq_authority_email (email),
    KEY idx_authority_status (status),
    KEY idx_authority_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS missing_persons (
    missing_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    user_id BIGINT UNSIGNED NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    age SMALLINT UNSIGNED NULL, -- TODO: verify age storage/range
    gender VARCHAR(32) NULL,
    last_seen_location VARCHAR(255) NULL,
    last_seen_date DATE NULL, -- TODO: verify existing date format/type
    phone_number1 VARCHAR(32) NULL,
    phone_number2 VARCHAR(32) NULL,
    image_path VARCHAR(255) NOT NULL,
    faiss_id INT NULL, -- TODO: verify FAISS ID range and uniqueness
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (missing_id),
    UNIQUE KEY uq_missing_faiss_id (faiss_id), -- TODO: verify uniqueness against existing rows
    KEY idx_missing_user_id (user_id),
    KEY idx_missing_created_at (created_at),
    CONSTRAINT fk_missing_user
        FOREIGN KEY (user_id) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS found_persons (
    found_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    authority_id BIGINT UNSIGNED NULL,
    uploaded_by_admin_id BIGINT UNSIGNED NULL,
    full_name VARCHAR(255) NOT NULL,
    approximate_age SMALLINT UNSIGNED NULL, -- TODO: verify age storage/range
    gender VARCHAR(32) NULL,
    found_location VARCHAR(255) NULL,
    found_date DATE NULL, -- TODO: verify existing date format/type
    health_status VARCHAR(255) NULL,
    image_path VARCHAR(255) NOT NULL,
    phone_number1 VARCHAR(32) NULL,
    phone_number2 VARCHAR(32) NULL,
    faiss_id INT NULL, -- TODO: verify FAISS ID range and uniqueness
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (found_id),
    UNIQUE KEY uq_found_faiss_id (faiss_id), -- TODO: verify uniqueness against existing rows
    KEY idx_found_authority_id (authority_id),
    KEY idx_found_admin_id (uploaded_by_admin_id),
    KEY idx_found_created_at (created_at),
    CONSTRAINT fk_found_authority
        FOREIGN KEY (authority_id) REFERENCES authority (authority_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_found_admin
        FOREIGN KEY (uploaded_by_admin_id) REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS match_results (
    match_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    missing_id BIGINT UNSIGNED NOT NULL,
    found_id BIGINT UNSIGNED NOT NULL,
    similarity_score DECIMAL(7,6) NULL, -- TODO: verify precision and 0-through-1 range
    status VARCHAR(20) NOT NULL, -- TODO: verify match/uncertain/no_match values
    PRIMARY KEY (match_id),
    KEY idx_match_missing_id (missing_id),
    KEY idx_match_found_id (found_id),
    KEY idx_match_status (status),
    CONSTRAINT fk_match_missing
        FOREIGN KEY (missing_id) REFERENCES missing_persons (missing_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_match_found
        FOREIGN KEY (found_id) REFERENCES found_persons (found_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- TODO: verify existing production column lengths and date types.
