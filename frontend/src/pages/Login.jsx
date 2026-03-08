import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Heading,
  VStack,
  Link,
  useToast,
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useState } from 'react';

export default function Login({ setIsLoggedIn, setSubscription }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const toast = useToast();
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!email || !password) {
      toast({
        title: 'Please enter both email and password.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      const resp = await fetch('http://localhost:5000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ email, password }),
      });

      const data = await resp.json();

      if (resp.ok) {
        sessionStorage.setItem('token', data.token);
        sessionStorage.setItem('subscription', data.user.subscription);
        sessionStorage.setItem('username', data.user.username);
        sessionStorage.setItem('user_id', data.user.user_id);
        sessionStorage.setItem('has_completed_survey', data.user.has_completed_survey);

        sessionStorage.setItem('preference_coins', JSON.stringify(data.user.preferences || []));

        // Notify the app to update the login status
        if (setIsLoggedIn) setIsLoggedIn(true);
        if (setSubscription) setSubscription(data.user.subscription);

        try {
          const profileResp = await fetch('http://localhost:5000/api/user/profile', {
            headers: {
              Authorization: `Bearer ${data.token}`,
            },
          });

          if (profileResp.ok) {
            const profileData = await profileResp.json();
            const preferredCoins = profileData.followed_currencies || [];
            sessionStorage.setItem('preference_coins', JSON.stringify(preferredCoins));
          }
        } catch (err) {
          console.warn('⚠️ Error fetching profile:', err);
        }

        toast({
          title: 'Login successful',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });

        navigate('/');
      } else {
        toast({
          title: 'Login failed',
          description: data.message || 'Invalid credentials.',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (err) {
      toast({
        title: 'Failed to connect to server',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box maxW="sm" mx="auto" mt={20} p={6} bg="white" borderRadius="lg" boxShadow="md">
      <Heading size="lg" mb={6} textAlign="center">
        Login
      </Heading>
      <VStack spacing={4}>
        <FormControl isRequired>
          <FormLabel>Email</FormLabel>
          <Input
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </FormControl>
        <FormControl isRequired>
          <FormLabel>Password</FormLabel>
          <Input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </FormControl>
        <Button colorScheme="purple" width="100%" onClick={handleLogin}>
          Login
        </Button>
        <Link as={RouterLink} to="/register" fontSize="sm" color="purple.500">
          Don&apos;t have an account? Register now
        </Link>
      </VStack>
    </Box>
  );
}
