import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  Spinner,
  VStack,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  SimpleGrid,
  Tag,
  Wrap,
  WrapItem,
  Button,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalCloseButton,
  ModalBody,
  ModalFooter,
  useDisclosure,
  Checkbox,
  CheckboxGroup,
  SimpleGrid as Grid,
} from '@chakra-ui/react';

const ALL_COINS = [
  { value: 'btc', label: 'Bitcoin (BTC)', minPlan: 'Free' },
  { value: 'eth', label: 'Ethereum (ETH)', minPlan: 'Free' },
  { value: 'usdt', label: 'Tether (USDT)', minPlan: 'Free' },
  { value: 'bnb', label: 'BNB (BNB)', minPlan: 'Pro' },
  { value: 'xrp', label: 'XRP (XRP)', minPlan: 'Pro' },
  { value: 'sol', label: 'Solana (SOL)', minPlan: 'Pro' },
  { value: 'ada', label: 'Cardano (ADA)', minPlan: 'Enterprise' },
  { value: 'aave', label: 'Aave (AAVE)', minPlan: 'Enterprise' },
  { value: 'doge', label: 'Dogecoin (DOGE)', minPlan: 'Enterprise' },
  { value: 'sand', label: 'The Sandbox (SAND)', minPlan: 'Enterprise' },
  { value: 'sei', label: 'Sei (SEI)', minPlan: 'Enterprise' },
  { value: 'shib', label: 'Shiba Inu (SHIB)', minPlan: 'Enterprise' },
];

export default function UserProfile() {
  const [profileData, setProfileData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedPreferences, setSelectedPreferences] = useState([]);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    const fetchProfile = async () => {
      const token = sessionStorage.getItem('token');
      if (!token) {
        setError('Please log in to view your profile.');
        setLoading(false);
        return;
      }

      try {
        const response = await fetch('http://localhost:5000/api/user/profile', {
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || 'Failed to fetch profile data.');
        }

        const data = await response.json();
        setProfileData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);

  const handleSavePreferences = async () => {
    const token = sessionStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch('http://localhost:5000/api/user/preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ symbols: selectedPreferences }),
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.message);
      }

      toast({
        title: 'Preferences updated.',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      window.location.reload();
    } catch (e) {
      toast({
        title: 'Error updating preferences',
        description: e.message,
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={10} px={6}>
        <Spinner size="xl" />
        <Text mt={4}>Loading Profile...</Text>
      </Box>
    );
  }

  if (error) {
    return (
      <Box textAlign="center" py={10} px={6}>
        <Alert status="error">
          <AlertIcon />
          <AlertTitle>Error!</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </Box>
    );
  }

  const levelOrder = { Free: 0, Pro: 1, Enterprise: 2 };
  const allowedCoins = ALL_COINS.filter((c) => levelOrder[profileData.subscription_plan] >= levelOrder[c.minPlan]);
  const maxSelectable = profileData.max_currencies || 3;

  const handleOpenEdit = () => {
    if (profileData.subscription_plan === 'Free') {
      toast({
        title: 'Upgrade Required',
        description: 'This feature is available for paid users only.',
        status: 'info',
        duration: 4000,
        isClosable: true,
      });
      return;
    }
    setSelectedPreferences(profileData.followed_currencies);
    onOpen();
  };

  return (
    <Box maxW="container.md" mx="auto" mt={10} p={6} bg="white" borderRadius="lg" boxShadow="md">
      <VStack spacing={4} align="stretch">
        <Heading size="lg" mb={6}>User Profile</Heading>

        <SimpleGrid columns={2} spacing={4}>
          <Text fontWeight="bold">Username:</Text>
          <Text>{profileData.username}</Text>

          <Text fontWeight="bold">Email:</Text>
          <Text>{profileData.email}</Text>

          <Text fontWeight="bold">Subscription Plan:</Text>
          <Text>{profileData.subscription_plan}</Text>

          <Text fontWeight="bold">Survey Rating:</Text>
          <Text>{profileData.rating || 'Not completed yet'}</Text>
        </SimpleGrid>

        <Heading size="md" mt={8}>Followed Currencies</Heading>
        <Wrap spacing={2} mt={2} align="center">
          {profileData.followed_currencies.length > 0 ? (
            profileData.followed_currencies.map((symbol) => (
              <WrapItem key={symbol}>
                <Tag size="lg" colorScheme="purple">{symbol}</Tag>
              </WrapItem>
            ))
          ) : (
            <Text>You are not following any currencies yet.</Text>
          )}
          <Button size="sm" ml={4} onClick={handleOpenEdit}>Edit</Button>
        </Wrap>

        <Modal isOpen={isOpen} onClose={onClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Edit Preferences</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Text fontSize="sm" mb={2} color="gray.500">
                You can select up to
                {' '}
                {maxSelectable}
                {' '}
                currencies.
              </Text>
              <CheckboxGroup value={selectedPreferences} onChange={setSelectedPreferences}>
                <Grid columns={2} spacing={2}>
                  {allowedCoins.map((coin) => (
                    <Checkbox
                      key={coin.value}
                      value={coin.value}
                      isDisabled={
                        !selectedPreferences.includes(coin.value)
                        && selectedPreferences.length >= maxSelectable
                      }
                    >
                      {coin.label}
                    </Checkbox>
                  ))}
                </Grid>
              </CheckboxGroup>
            </ModalBody>
            <ModalFooter>
              <Button colorScheme="purple" mr={3} onClick={handleSavePreferences}>
                Save Preferences
              </Button>
              <Button onClick={onClose}>Cancel</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
}
