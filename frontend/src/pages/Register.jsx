import { useState } from 'react';
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
  Text,
  HStack,
} from '@chakra-ui/react';
import { Link as RouterLink, useNavigate } from 'react-router-dom';

export default function Register() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    verificationCode: '',
  });

  const [loading, setLoading] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const [errorMsg, setErrorMsg] = useState('');
  const [, setCodeSent] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((f) => ({ ...f, [name]: value }));
  };

  const handleSendCode = async () => {
    if (!form.email) {
      setErrorMsg('Please enter your email first.');
      return;
    }

    try {
      const resp = await fetch('http://localhost:5001/api/send-code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: form.email }),
      });

      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.message || 'Failed to send code');
      }

      toast({
        title: 'Verification code sent',
        status: 'info',
        duration: 3000,
        isClosable: true,
      });
      setCodeSent(true);
      setCooldown(60);

      const interval = setInterval(() => {
        setCooldown((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } catch (err) {
      setErrorMsg(err.message);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg('');

    if (form.password !== form.confirmPassword) {
      setErrorMsg('Passwords do not match.');
      return;
    }

    setLoading(true);
    try {
      const resp = await fetch('http://localhost:5001/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          password: form.password,
          code: form.verificationCode,
          plan: 'Free',
        }),
      });

      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.message || JSON.stringify(data.errors));
      }

      if (data.user) {
        localStorage.setItem('tempUser', JSON.stringify(data.user));
      }

      toast({
        title: 'Registration successful!',
        description: 'Please complete our onboarding survey.',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });

      setTimeout(() => navigate('/survey'), 1500);
    } catch (err) {
      setErrorMsg(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      as="form"
      maxW="sm"
      mx="auto"
      mt={12}
      p={6}
      bg="purple.50"
      borderRadius="lg"
      boxShadow="md"
      onSubmit={handleSubmit}
    >
      <Heading size="lg" mb={6} textAlign="center" color="purple.700">
        Register
      </Heading>
      <VStack spacing={4}>
        {errorMsg && <Text color="red.500">{errorMsg}</Text>}

        <FormControl isRequired>
          <FormLabel htmlFor="username">Username</FormLabel>
          <Input
            id="username"
            name="username"
            placeholder="Enter your username"
            type="text"
            value={form.username}
            onChange={handleChange}
            bg="white"
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel>Email & Verification</FormLabel>
          <HStack spacing={2}>
            <Input
              id="email"
              name="email"
              placeholder="you@example.com"
              type="email"
              value={form.email}
              onChange={handleChange}
              bg="white"
            />
            <Button
              onClick={handleSendCode}
              colorScheme="purple"
              size="sm"
              isDisabled={cooldown > 0}
            >
              {cooldown > 0 ? `${cooldown}s` : 'Send Code'}
            </Button>
          </HStack>
        </FormControl>

        <FormControl isRequired>
          <FormLabel htmlFor="verificationCode">Verification Code</FormLabel>
          <Input
            id="verificationCode"
            name="verificationCode"
            placeholder="Enter 6-digit code"
            type="text"
            value={form.verificationCode}
            onChange={handleChange}
            bg="white"
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel htmlFor="password">Password</FormLabel>
          <Input
            id="password"
            name="password"
            placeholder="Create a password"
            type="password"
            value={form.password}
            onChange={handleChange}
            bg="white"
          />
        </FormControl>

        <FormControl isRequired>
          <FormLabel htmlFor="confirmPassword">Confirm Password</FormLabel>
          <Input
            id="confirmPassword"
            name="confirmPassword"
            placeholder="Confirm your password"
            type="password"
            value={form.confirmPassword}
            onChange={handleChange}
            bg="white"
          />
        </FormControl>

        <Button
          type="submit"
          colorScheme="purple"
          width="100%"
          isLoading={loading}
        >
          Register
        </Button>

        <Link as={RouterLink} to="/login" fontSize="sm" color="purple.500">
          Already have an account? Log in
        </Link>
      </VStack>
    </Box>
  );
}
