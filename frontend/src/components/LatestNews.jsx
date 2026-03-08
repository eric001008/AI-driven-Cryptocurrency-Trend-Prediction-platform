import React from 'react';
import {
  Box,
  Heading,
  VStack,
  Text,
  Divider,
  Link,
  Spinner,
  Flex,
} from '@chakra-ui/react';

export default function LatestNews({
  selectedCoin, latest_news, lastUpdated, loading,
}) {
  console.log('🔥 LatestNews props:');
  console.log('selectedCoin:', selectedCoin);
  console.log('latest_news:', latest_news);

  const newsToShow = latest_news || [];

  return (
    <Box
      bg="white"
      p={6}
      borderRadius="lg"
      border="1px solid"
      borderColor="gray.300"
      boxShadow="md"
    >
      <Heading size="md" mb={4}>Latest News</Heading>

      {lastUpdated && (
        <Text fontSize="xs" color="gray.500" mb={2}>
          Last Updated:
          {' '}
          {new Date(lastUpdated).toLocaleString()}
        </Text>
      )}

      {loading ? (
        <Flex h="100px" align="center" justify="center">
          <Spinner size="lg" role="status" data-testid="loading-spinner" />
        </Flex>
      ) : (
        <VStack align="start" spacing={4}>
          {newsToShow.map((item, idx) => (
            <Box key={idx}>
              <Text fontWeight="bold">{item.title}</Text>
              <Link href={item.url} color="blue.500" isExternal fontSize="sm">
                View Source &gt;
              </Link>
              {idx < newsToShow.length - 1 && <Divider my={2} />}
            </Box>
          ))}
          {newsToShow.length === 0 && (
            <Text fontSize="sm" color="gray.500">
              No news available for
              {' '}
              {selectedCoin.toUpperCase()}
              .
            </Text>
          )}
        </VStack>
      )}
    </Box>
  );
}
