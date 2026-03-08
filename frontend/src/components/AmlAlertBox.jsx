import React from 'react';
import { Box, Text } from '@chakra-ui/react';

export default function AmlAlertBox({ selectedCoin, aml }) {
  const coinInfo = (aml || []).find(
    (item) => item.symbol?.toLowerCase() === selectedCoin?.toLowerCase(),
  );

  const isSuspicious = coinInfo?.aml_label === 1;

  return (
    <Box
      position="fixed"
      bottom="20px"
      right="20px"
      bg={isSuspicious ? 'yellow.50' : 'green.50'}
      border="1px solid"
      borderColor={isSuspicious ? 'orange.200' : 'green.200'}
      borderRadius="md"
      p={4}
      boxShadow="lg"
      zIndex={1000}
      maxW="400px"
    >
      <Text fontWeight="bold" mb={1}>
        AML
        {' '}
        {isSuspicious ? 'Warning' : 'Status'}
      </Text>

      {isSuspicious ? (
        <Text fontSize="sm">
          Suspicious transactions detected for
          {' '}
          {selectedCoin.toUpperCase()}
          .
        </Text>
      ) : (
        <Text fontSize="sm">
          No suspicious activity detected for
          {' '}
          {selectedCoin.toUpperCase()}
          .
        </Text>
      )}
    </Box>
  );
}
