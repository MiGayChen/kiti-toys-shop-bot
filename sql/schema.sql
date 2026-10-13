CREATE TABLE categories (
    id   INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);
CREATE TABLE products (
    id          INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    name        TEXT NOT NULL,
    description TEXT,
    price       INTEGER NOT NULL CHECK (price >= 0),
    image       TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);
CREATE TABLE users (
    id               INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    platform         TEXT NOT NULL,
    platform_user_id BIGINT NOT NULL,
    name             TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (platform, platform_user_id)
);
CREATE TABLE cart_items (
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    qty        INTEGER NOT NULL CHECK (qty > 0),
    PRIMARY KEY (user_id, product_id)
);