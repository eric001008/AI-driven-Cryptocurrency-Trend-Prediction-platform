import React from 'react';
import {
  Box, Heading, Text, VStack, Flex, Spinner,
} from '@chakra-ui/react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from 'recharts';

export default function MarketOverview({
  selectedCoin, price_trend, percent_change_24h, loading,
}) {
  const formattedData = (price_trend || []).map((d) => ({
    time: new Date(d.last_updated).toLocaleString([], {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    }),
    price: parseFloat(d.price),
  }));

  const latestPrice = formattedData.at(-1)?.price ?? 0;

  return (
    <Box bg="white" p={6} borderRadius="lg" border="1px solid" borderColor="gray.300" boxShadow="md">
      <VStack align="start" spacing={4}>
        <Heading size="md">
          Market Overview -
          {selectedCoin.toUpperCase()}
        </Heading>

        <Flex w="100%" justify="space-between" align="center">
          <Box />
          <VStack align="end" spacing={0}>
            <Text fontSize="xl" fontWeight="bold">
              $
              {latestPrice.toFixed(2)}
            </Text>
            <Text fontSize="sm" color={percent_change_24h < 0 ? 'red.500' : 'green.500'}>
              {percent_change_24h?.toFixed(2)}
              %
            </Text>
          </VStack>
        </Flex>

        <Box w="100%" h="200px">
          {loading ? (
            <Flex h="100%" align="center" justify="center"><Spinner size="lg" data-testid="loading-spinner" /></Flex>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={formattedData}>
                <XAxis dataKey="time" />
                <YAxis domain={['auto', 'auto']} />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#3182CE" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          )}
        </Box>
      </VStack>
    </Box>
  );
}
