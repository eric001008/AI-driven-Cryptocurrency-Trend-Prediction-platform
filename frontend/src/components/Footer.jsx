import React from 'react';
import { Box, Text, Flex } from '@chakra-ui/react';

export default function Footer() {
  return (
    <Box as="footer" bg="purple.50" py={4}>
      <Flex justify="center" align="center" maxW="6xl" mx="auto" px={4}>
        <Text fontSize="sm" color="gray.600" textAlign="center">
          ©
          {' '}
          {new Date().getFullYear()}
          {' '}
          Financial Dashboard Group. All rights reserved.
        </Text>
      </Flex>
    </Box>
  );
}
