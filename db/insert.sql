INSERT INTO ods.users (username, email, password_hash, created_at, subscription_id)
VALUES 
  ('alice_free1', 'alice1@example.com', '$2b$12$e1.2DVnEBOJVthihHXpvEeGosUGcLcBBj1D.JEnpCBviSe.u7VLei', NOW(), 1),
  ('bob_pro1', 'bob1@example.com', '$2b$12$e1.2DVnEBOJVthihHXpvEeGosUGcLcBBj1D.JEnpCBviSe.u7VLei', NOW(), 2),
  ('carol_enterprise1', 'carol1@example.com', '$2b$12$e1.2DVnEBOJVthihHXpvEeGosUGcLcBBj1D.JEnpCBviSe.u7VLei', NOW(), 3);

INSERT INTO ods.currencies (currency_id, symbol, name, is_flagged_aml) 
VALUES
  (1, 'btc', 'Bitcoin (BTC)', false),
  (2, 'eth', 'Ethereum (ETH)', false),
  (3, 'usdt', 'Tether (USDT)', false),
  (4, 'bnb', 'BNB (BNB)', false),
  (5, 'xrp', 'XRP (XRP)', false),
  (6, 'sol', 'Solana (SOL)', false),
  (7, 'ada', 'Cardano (ADA)', false),
  (8, 'aave', 'Aave (AAVE)', false),
  (9, 'doge', 'Dogecoin (DOGE)', false),
  (10, 'sand', 'The Sandbox (SAND)', false),
  (11, 'sei', 'Sei (SEI)', false);