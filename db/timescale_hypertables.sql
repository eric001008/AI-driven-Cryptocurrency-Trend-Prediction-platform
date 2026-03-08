-- Enable TimescaleDB extension (safe if already exists)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create hypertable for ods.media_reddit_posts if and only if the column exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'ods'
      AND table_name = 'media_reddit_posts'
      AND column_name = 'created_utc'
  ) THEN
    PERFORM create_hypertable('ods.media_reddit_posts', 'created_utc', if_not_exists := TRUE);
    RAISE NOTICE 'Hypertable created for ods.media_reddit_posts.';
  ELSE
    RAISE NOTICE 'Table ods.media_reddit_posts is missing column created_utc. Skipping hypertable creation.';
  END IF;
END
$$;

-- Create hypertable for ods.price_cryptocurrencies if and only if the column exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'ods'
      AND table_name = 'price_cryptocurrencies'
      AND column_name = 'created_utc'
  ) THEN
    PERFORM create_hypertable('ods.price_cryptocurrencies', 'created_utc', if_not_exists := TRUE);
    RAISE NOTICE 'Hypertable created for ods.price_cryptocurrencies.';
  ELSE
    RAISE NOTICE 'Table ods.price_cryptocurrencies is missing column created_utc. Skipping hypertable creation.';
  END IF;
END
$$;

-- Create hypertable for ods.media_twitter_posts if and only if the column exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'ods'
      AND table_name = 'media_twitter_posts'
      AND column_name = 'created_utc'
  ) THEN
    PERFORM create_hypertable('ods.media_twitter_posts', 'created_utc', if_not_exists := TRUE);
    RAISE NOTICE 'Hypertable created for ods.media_twitter_posts.';
  ELSE
    RAISE NOTICE 'Table ods.media_twitter_posts is missing column created_utc. Skipping hypertable creation.';
  END IF;
END
$$;

-- Create hypertable for ods.blockchain_transactions if and only if the column exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'ods'
      AND table_name = 'blockchain_transactions'
      AND column_name = 'created_utc'
  ) THEN
    PERFORM create_hypertable('ods.blockchain_transactions', 'created_utc', if_not_exists := TRUE);
    RAISE NOTICE 'Hypertable created for ods.blockchain_transactions.';
  ELSE
    RAISE NOTICE 'Table ods.blockchain_transactions is missing column created_utc. Skipping hypertable creation.';
  END IF;
END
$$;

-- Create hypertable for ods.news_articles if and only if the column exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'ods'
      AND table_name = 'news_articles'
      AND column_name = 'created_utc'
  ) THEN
    PERFORM create_hypertable('ods.news_articles', 'created_utc', if_not_exists := TRUE);
    RAISE NOTICE 'Hypertable created for ods.news_articles.';
  ELSE
    RAISE NOTICE 'Table ods.news_articles is missing column created_utc. Skipping hypertable creation.';
  END IF;
END
$$;
