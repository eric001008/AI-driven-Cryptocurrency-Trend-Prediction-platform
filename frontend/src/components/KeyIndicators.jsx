import React from 'react';
import {
  Box, Heading, VStack, HStack, Text, Divider, Spinner, Flex,
} from '@chakra-ui/react';

export default function KeyIndicators({ statistic, loading }) {
  const formatNumber = (n) => (n ? parseFloat(n).toLocaleString('en-US', { maximumFractionDigits: 2 }) : '-');

  return (
    <Box
      bg="white"
      p={6}
      borderRadius="lg"
      border="1px solid"
      borderColor="gray.300"
      boxShadow="md"
    >
      <Heading size="md" mb={4}>Key Indicators</Heading>

      {loading ? (
        <Flex h="100px" align="center" justify="center">
          <Spinner size="lg" data-testid="loading-spinner" />
        </Flex>
      ) : statistic ? (
        <VStack spacing={3} align="stretch">
          <IndicatorItem name="Market Cap" value={`$${formatNumber(statistic.market_cap)}`} />
          <IndicatorItem name="24h Volume" value={`$${formatNumber(statistic.volume_24h)}`} />
          <IndicatorItem name="Circulating Supply" value={formatNumber(statistic.circulating_supply)} />
          <IndicatorItem name="Total Supply" value={formatNumber(statistic.total_supply)} />
          <IndicatorItem
            name="Max Supply"
            value={
                statistic.max_supply
                  ? formatNumber(statistic.max_supply)
                  : 'Unlimited'
            }
          />
          <IndicatorItem name="24h Change" value={`${(statistic.percent_change_24h || 0).toFixed(2)}%`} isChange />
          <IndicatorItem name="7d Change" value={`${(statistic.percent_change_7d || 0).toFixed(2)}%`} isChange />
        </VStack>
      ) : (
        <Text color="gray.500">No indicator data available.</Text>
      )}
    </Box>
  );
}

function IndicatorItem({ name, value, isChange = false }) {
  const isPositive = parseFloat(value) >= 0;
  return (
    <Box>
      <HStack justify="space-between">
        <Text fontWeight="medium">{name}</Text>
        <Text
          data-testid={`indicator-${name}`}
          style={
                        isChange
                          ? { color: isPositive ? '#38A169' : '#E53E3E' }
                          : { color: '#1A202C' }
                      }
        >
          {value}
        </Text>
      </HStack>
      <Divider mt={2} />
    </Box>
  );
}
