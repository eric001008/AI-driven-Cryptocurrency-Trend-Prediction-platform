import React, { useEffect, useState } from 'react';
import {
  ChakraProvider,
  Box,
  Grid,
  VStack,
  Select,
  Text,
  Spinner,
  Flex,
} from '@chakra-ui/react';
import { Routes, Route } from 'react-router-dom';

import Header from './components/Header';
import Footer from './components/Footer';
import MarketOverview from './components/MarketOverview';
import SentimentAnalysis from './components/SentimentAnalysis';
import LatestNews from './components/LatestNews';
import KeyIndicators from './components/KeyIndicators';
import AmlAlertBox from './components/AmlAlertBox';
import LockedOverlay from './components/LockedOverlay';

import Login from './pages/Login';
import Register from './pages/Register';
import Pricing from './pages/Pricing';
import Survey from './pages/Survey';
import UserProfile from './pages/UserProfile';

const ALL_COINS = [
  { value: 'btc', label: 'Bitcoin (BTC)', minPlan: 'Free' },
  { value: 'dai', label: 'Dai (DAI)', minPlan: 'Free' },
  { value: 'eth', label: 'Ethereum (ETH)', minPlan: 'Free' },
  { value: 'usdc', label: 'USD Coin (USDC)', minPlan: 'Free' },
  { value: 'usdt', label: 'Tether (USDT)', minPlan: 'Free' },
  { value: 'apt', label: 'Aptos (APT)', minPlan: 'Pro' },
  { value: 'avax', label: 'Avalanche (AVAX)', minPlan: 'Pro' },
  { value: 'bch', label: 'Bitcoin Cash (BCH)', minPlan: 'Pro' },
  { value: 'bgb', label: 'Bitget Token (BGB)', minPlan: 'Pro' },
  { value: 'bnb', label: 'BNB (BNB)', minPlan: 'Pro' },
  { value: 'bsc-usd', label: 'Binance-Peg BSC-USD', minPlan: 'Pro' },
  { value: 'cbbtc', label: 'Coinbase Wrapped BTC (CBBTC)', minPlan: 'Pro' },
  { value: 'cro', label: 'Cronos (CRO)', minPlan: 'Pro' },
  { value: 'dot', label: 'Polkadot (DOT)', minPlan: 'Pro' },
  { value: 'ena', label: 'Ethena (ENA)', minPlan: 'Pro' },
  { value: 'etc', label: 'Ethereum Classic (ETC)', minPlan: 'Pro' },
  { value: 'hbar', label: 'Hedera (HBAR)', minPlan: 'Pro' },
  { value: 'icp', label: 'Internet Computer (ICP)', minPlan: 'Pro' },
  { value: 'link', label: 'Chainlink (LINK)', minPlan: 'Pro' },
  { value: 'ltc', label: 'Litecoin (LTC)', minPlan: 'Pro' },
  { value: 'near', label: 'NEAR Protocol (NEAR)', minPlan: 'Pro' },
  { value: 'ondo', label: 'Ondo (ONDO)', minPlan: 'Pro' },
  { value: 'sol', label: 'Solana (SOL)', minPlan: 'Pro' },
  { value: 'trx', label: 'TRON (TRX)', minPlan: 'Pro' },
  { value: 'uni', label: 'Uniswap (UNI)', minPlan: 'Pro' },
  { value: 'usde', label: 'Ethena USDe (USDe)', minPlan: 'Pro' },
  { value: 'wbtc', label: 'Wrapped Bitcoin (WBTC)', minPlan: 'Pro' },
  { value: 'weth', label: 'Wrapped ETH (WETH)', minPlan: 'Pro' },
  { value: 'xlm', label: 'Stellar (XLM)', minPlan: 'Pro' },
  { value: 'xrp', label: 'XRP (XRP)', minPlan: 'Pro' },
  { value: 'aave', label: 'Aave (AAVE)', minPlan: 'Enterprise' },
  { value: 'ada', label: 'Cardano (ADA)', minPlan: 'Enterprise' },
  { value: 'doge', label: 'Dogecoin (DOGE)', minPlan: 'Enterprise' },
  { value: 'hype', label: 'Hype (HYPE)', minPlan: 'Enterprise' },
  { value: 'jitosol', label: 'JitoSOL', minPlan: 'Enterprise' },
  { value: 'leo', label: 'UNUS SED LEO (LEO)', minPlan: 'Enterprise' },
  { value: 'pepe', label: 'Pepe (PEPE)', minPlan: 'Enterprise' },
  { value: 'pi', label: 'Pi Network (PI)', minPlan: 'Enterprise' },
  { value: 'shib', label: 'Shiba Inu (SHIB)', minPlan: 'Enterprise' },
  { value: 'steth', label: 'Lido Staked ETH (stETH)', minPlan: 'Enterprise' },
  { value: 'sui', label: 'Sui (SUI)', minPlan: 'Enterprise' },
  { value: 'susde', label: 'sUSDe', minPlan: 'Enterprise' },
  { value: 'tao', label: 'Bittensor (TAO)', minPlan: 'Enterprise' },
  { value: 'ton', label: 'Toncoin (TON)', minPlan: 'Enterprise' },
  { value: 'usds', label: 'Stably USD (USDS)', minPlan: 'Enterprise' },
  { value: 'wbeth', label: 'Wrapped Beacon ETH (WBETH)', minPlan: 'Enterprise' },
  { value: 'wbt', label: 'WhiteBIT Coin (WBT)', minPlan: 'Enterprise' },
  { value: 'weeth', label: 'wETH (wEETH)', minPlan: 'Enterprise' },
  { value: 'wsteth', label: 'Wrapped stETH (wstETH)', minPlan: 'Enterprise' },
  { value: 'xmr', label: 'Monero (XMR)', minPlan: 'Enterprise' },
];

const levelOrder = { Free: 0, Pro: 1, Enterprise: 2 };
const canAccess = (userPlan, requiredPlan) => levelOrder[userPlan] >= levelOrder[requiredPlan];

function Dashboard({
  selectedCoin, setSelectedCoin, coinData, loading, isLoggedIn, subscription,
}) {
  const [preferenceCoins, setPreferenceCoins] = useState([]);

  useEffect(() => {
    const token = sessionStorage.getItem('token');
    if (token) {
      fetch('http://localhost:5000/api/user/profile', {
        headers: { Authorization: `Bearer ${token}` },
      })
        .then((res) => res.json())
        .then((data) => setPreferenceCoins(data.followed_currencies || []))
        .catch((err) => {
          console.warn('Failed to fetch preferences:', err);
          setPreferenceCoins([]);
        });
    }
  }, [isLoggedIn, subscription, selectedCoin]);

  const isCoinAllowed = canAccess(
    subscription,
    ALL_COINS.find((c) => c.value === selectedCoin)?.minPlan || 'Enterprise',
  );

  return (
    <Box px={8} py={4} bg="gray.50">
      <Box mb={4} w="400px">
        <Text fontSize="sm" color="gray.600" mb={2}>
          Select the cryptocurrency you are interested in:
        </Text>
        <Select
          border="2px solid"
          borderColor="purple.500"
          borderRadius="md"
          boxShadow="sm"
          fontWeight="bold"
          bg="white"
          value={selectedCoin}
          onChange={(e) => setSelectedCoin(e.target.value)}
        >
          {ALL_COINS.map((coin) => {
            const disabled = !canAccess(subscription, coin.minPlan);
            const isPreferred = preferenceCoins.includes(coin.value);
            return (
              <option
                key={coin.value}
                value={coin.value}
                disabled={disabled}
                title={disabled ? 'Upgrade your plan to access this coin.' : ''}
              >
                {coin.label}
                {' '}
                {isPreferred ? '⭐' : ''}
                {' '}
                {disabled ? '🔒' : ''}
              </option>
            );
          })}
        </Select>
      </Box>

      {!isCoinAllowed ? (
        <Text color="red.500" fontWeight="bold">
          Your current subscription (
          {subscription}
          ) does not allow access to this currency.
        </Text>
      ) : loading ? (
        <Flex h="300px" align="center" justify="center">
          <Spinner size="xl" role="status" />
        </Flex>
      ) : coinData ? (
        <Grid templateColumns={{ base: '1fr', lg: '2fr 1.2fr 2fr' }} gap={6}>
          <VStack spacing={6} align="stretch">
            <MarketOverview
              selectedCoin={selectedCoin}
              price_trend={coinData.price_trend}
              percent_change_24h={coinData.statistic?.percent_change_24h}
              loading={loading}
            />
            {isLoggedIn ? (
              <SentimentAnalysis
                selectedCoin={selectedCoin}
                sentiment={coinData.sentiment}
                recommendation_={coinData.recommendation}
                lastUpdated={coinData.statistic?.last_updated}
                loading={loading}
              />
            ) : (
              <LockedOverlay>
                <SentimentAnalysis
                  selectedCoin={selectedCoin}
                  sentiment={coinData.sentiment}
                  recommendation_={coinData.recommendation}
                  lastUpdated={coinData.statistic?.last_updated}
                  loading={loading}
                />
              </LockedOverlay>
            )}
          </VStack>

          {isLoggedIn ? (
            <KeyIndicators
              selectedCoin={selectedCoin}
              statistic={coinData.statistic}
              loading={loading}
            />
          ) : (
            <LockedOverlay>
              <KeyIndicators
                selectedCoin={selectedCoin}
                statistic={coinData.statistic}
                loading={loading}
              />
            </LockedOverlay>
          )}

          {isLoggedIn ? (
            <LatestNews
              selectedCoin={selectedCoin}
              latest_news={coinData.latest_news}
              lastUpdated={coinData.statistic?.last_updated}
              loading={loading}
            />
          ) : (
            <LockedOverlay>
              <LatestNews
                selectedCoin={selectedCoin}
                latest_news={coinData.latest_news}
                lastUpdated={coinData.statistic?.last_updated}
                loading={loading}
              />
            </LockedOverlay>
          )}
        </Grid>
      ) : (
        <Text>
          Failed to load data for
          {' '}
          {selectedCoin}
        </Text>
      )}
    </Box>
  );
}

function App() {
  const [selectedCoin, setSelectedCoin] = useState('btc');
  const [coinData, setCoinData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isLoggedIn, setIsLoggedIn] = useState(!!sessionStorage.getItem('token'));
  const [subscription, setSubscription] = useState(sessionStorage.getItem('subscription') || 'Free');

  useEffect(() => {
    setLoading(true);
    const token = sessionStorage.getItem('token');
    fetch(`http://localhost:5000/api/data/coin_data?symbol=${selectedCoin.toUpperCase()}`, {
      headers: { Authorization: `Bearer ${token}` },
      credentials: 'include',
    })
      .then((res) => res.json())
      .then((data) => {
        const newCoinData = {
          price_trend: data.price_trend,
          sentiment: data.sentiment,
          statistic: data.statistic,
          latest_news: data.news,
          aml: data.aml,
          recommendation: data.recommendation,
        };
        setCoinData(newCoinData);
      })
      .catch((err) => {
        console.error('Error fetching coin data:', err);
        setCoinData(null);
      })
      .finally(() => setLoading(false));
  }, [selectedCoin, isLoggedIn]);

  return (
    <ChakraProvider>
      {/* 页面根：纵向 flex，main 占满剩余，footer 贴底 */}
      <Box minH="100vh" display="flex" flexDirection="column" bg="gray.50">
        <Header setIsLoggedIn={setIsLoggedIn} setSubscription={setSubscription} />

        <Box as="main" flex="1">
          <Routes>
            <Route
              path="/"
              element={(
                <>
                  <Dashboard
                    selectedCoin={selectedCoin}
                    setSelectedCoin={setSelectedCoin}
                    coinData={coinData}
                    loading={loading}
                    isLoggedIn={isLoggedIn}
                    subscription={subscription}
                  />

                  {isLoggedIn ? (
                    <AmlAlertBox selectedCoin={selectedCoin} aml={coinData?.aml} />
                  ) : (
                    <Box position="fixed" bottom="6" right="6" w={{ base: '92%', md: '360px' }} zIndex={10}>
                      <LockedOverlay>
                        <Box h="110px" borderRadius="lg" bg="gray.100" />
                      </LockedOverlay>
                    </Box>
                  )}
                </>
              )}
            />
            <Route path="/login" element={<Login setIsLoggedIn={setIsLoggedIn} setSubscription={setSubscription} />} />
            <Route path="/register" element={<Register />} />
            <Route path="/pricing" element={<Pricing />} />
            <Route path="/survey" element={<Survey />} />
            <Route path="/profile" element={<UserProfile />} />
          </Routes>
        </Box>

        <Footer />
      </Box>
    </ChakraProvider>
  );
}

export default App;
