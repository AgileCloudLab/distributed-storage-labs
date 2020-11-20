CREATE TABLE IF NOT EXISTS `file` (
   `id` INTEGER PRIMARY KEY AUTOINCREMENT,
   `filename` TEXT,
   `size` INTEGER,
   `content_type` TEXT,
   `storage_mode` TEXT,
   `storage_details` TEXT,
   `created` DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS `block_hash` (
   `id` INTEGER PRIMARY KEY AUTOINCREMENT,
   `hash` TEXT
);