import React, { useState } from 'react';
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  HStack,
  SimpleGrid,
  Tag,
  useToast,
} from '@chakra-ui/react';
import { CheckCircleIcon, StarIcon } from '@chakra-ui/icons';
import { motion } from 'framer-motion';

const MotionBox = motion(Box);

const plans = [
  {
    name: 'Free',
    price: { monthly: 0, yearly: 0 },
    features: [
      'Track up to 5 cryptocurrencies.',
      'View basic charts and sentiment scores.',
      'Access 7-day historical data only.',
      'UTC time display only.',
      'Standard email support.',
    ],
    buttonText: 'Subscribed',
    isPopular: false,
    bgGradient: 'linear(to-t, gray.100, white)',
  },
  {
    name: 'Pro',
    price: { monthly: 15, yearly: 144 },
    features: [
      'Track up to 10 cryptocurrencies.',
      'Interactive charts with customizable ranges.',
      'Access 90-day historical data.',
      'Minimal ads or upgrade prompts.',
      'Priority email support.',
    ],
    buttonText: 'Upgrade',
    isPopular: true,
    bgGradient: 'linear(to-t, blue.100, white)',
  },
  {
    name: 'Pro Max',
    price: { monthly: 35, yearly: 300 },
    features: [
      'Unlimited cryptocurrency tracking.',
      'Full access to all technical indicators and AI analysis.',
      '1-year+ historical data with filters.',
      'Early access to new features.',
      'VIP-level customer support.',
    ],
    buttonText: 'Upgrade',
    isPopular: false,
    bgGradient: 'linear(to-t, purple.100, white)',
  },
];

function Pricing() {
  const [billing, setBilling] = useState('monthly');
  const toast = useToast();

  return (
    <Box px={8} py={12} bg="gray.50" minH="100vh">
      <HStack justify="center" mb={6}>
        <Button
          data-testid="billing-monthly"
          onClick={() => setBilling('monthly')}
          variant={billing === 'monthly' ? 'solid' : 'outline'}
          colorScheme="purple"
        >
          Monthly
        </Button>
        <Button
          data-testid="billing-yearly"
          onClick={() => setBilling('yearly')}
          variant={billing === 'yearly' ? 'solid' : 'outline'}
          colorScheme="purple"
        >
          Yearly
        </Button>
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={10}>
        {plans.map((plan) => (
          <MotionBox
            key={plan.name}
            whileHover={{ scale: 1.05 }}
            transition={{ duration: 0.3 }}
            p={8}
            bgGradient={plan.bgGradient}
            borderRadius="xl"
            boxShadow={plan.isPopular ? 'xl' : 'md'}
            color="gray.800"
            border={plan.isPopular ? '2px solid #805AD5' : '1px solid #E2E8F0'}
            position="relative"
          >
            {plan.isPopular && (
              <Tag
                position="absolute"
                top={4}
                right={4}
                colorScheme="purple"
                variant="solid"
              >
                <StarIcon mr={1} />
                Popular
              </Tag>
            )}

            <VStack spacing={4} align="stretch">
              <Heading as="h3" size="md" textAlign="center">
                {plan.name}
              </Heading>
              <VStack spacing={0} textAlign="center">
                <Text fontSize="4xl" fontWeight="bold">
                  $
                  {plan.price[billing]}
                  <Text as="span" fontSize="md">
                    {billing === 'monthly' ? '/mo' : '/yr'}
                  </Text>
                </Text>
                {billing === 'yearly' && plan.name !== 'Free' && (
                  <Text fontSize="sm" color="gray.600">
                    $
                    {Math.round(plan.price.yearly / 12)}
                    /mo when billed yearly
                  </Text>
                )}
              </VStack>

              <VStack align="start" spacing={2}>
                {plan.features.map((feature, idx) => (
                  <HStack key={idx} spacing={2}>
                    <CheckCircleIcon color="green.400" />
                    <Text>{feature}</Text>
                  </HStack>
                ))}
              </VStack>

              <Button
                mt={4}
                colorScheme={
                  plan.name === 'Pro' || plan.name === 'Pro Max' ? 'purple' : 'gray'
                }
                variant="outline"
                onClick={() => toast({
                  title: 'Coming Soon!',
                  description: 'This subscription feature is not available yet.',
                  status: 'info',
                  duration: 3000,
                  isClosable: true,
                  position: 'top',
                })}
              >
                {plan.buttonText}
              </Button>
            </VStack>
          </MotionBox>
        ))}
      </SimpleGrid>
    </Box>
  );
}

export default Pricing;
