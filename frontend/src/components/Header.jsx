import React from 'react';
import {
  Flex,
  Box,
  Heading,
  Spacer,
  Button,
  HStack,
  Link as ChakraLink,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

export default function Header({ setIsLoggedIn, setSubscription }) {
  const isLoggedIn = !!sessionStorage.getItem('token');
  const navigate = useNavigate();

  const handleLogout = () => {
    sessionStorage.clear();
    if (setIsLoggedIn) setIsLoggedIn(false);
    if (setSubscription) setSubscription('Free');
    navigate('/login');
  };

  return (
    <Flex
      as="header"
      p={4}
      bg="purple.50"
      alignItems="center"
      boxShadow="sm"
      position="sticky"
      top={0}
      zIndex={1000}
    >
      <Box>
        <Heading size="md" color="purple.700">
          Financial Data Dashboard
        </Heading>
      </Box>

      <Spacer />

      <HStack spacing={4}>
        <ChakraLink as={RouterLink} to="/" fontWeight="medium" color="gray.600">
          Dashboard
        </ChakraLink>
        <ChakraLink as={RouterLink} to="/pricing" fontWeight="medium" color="gray.600">
          Pricing
        </ChakraLink>

        {isLoggedIn ? (
          <Menu>
            <MenuButton as={Button} size="sm" variant="outline" colorScheme="purple">
              account
            </MenuButton>
            <MenuList>
              <MenuItem as={RouterLink} to="/profile">View Profile</MenuItem>
              <MenuItem onClick={handleLogout}>Log Out</MenuItem>
            </MenuList>
          </Menu>
        ) : (
          <>
            <Button as={RouterLink} to="/login" size="sm" variant="outline" colorScheme="purple">
              Sign In
            </Button>
            <Button as={RouterLink} to="/register" size="sm" colorScheme="purple">
              Register
            </Button>
          </>
        )}
      </HStack>
    </Flex>
  );
}
