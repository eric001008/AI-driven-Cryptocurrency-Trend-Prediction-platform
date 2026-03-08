import React, { useState, useMemo } from 'react';
import {
  Box,
  Text,
  VStack,
  Button,
  Collapse,
  Badge,
  Link,
  Divider,
  HStack,
  useColorModeValue,
} from '@chakra-ui/react';
import { ExternalLinkIcon } from '@chakra-ui/icons';

function SentimentAnalysis({ _selectedCoin, sentiment, recommendation_ }) {
  const [showReason, setShowReason] = useState(false);

  const avgScore = useMemo(() => {
    if (!sentiment || sentiment.length === 0) return 0;
    return sentiment.reduce((acc, item) => acc + item.sentiment_score, 0) / sentiment.length;
  }, [sentiment]);

  const isRecommended = avgScore > 0.5;
  const isDataDeficient = recommendation_?.message?.startsWith('Data Deficiencies!');
  const reason = isRecommended
    ? 'This cryptocurrency has a relatively high sentiment score, indicating a generally '
      + 'positive market attitude. It may be worth considering.'
    : 'This cryptocurrency has a relatively low sentiment score, indicating some market '
      + 'doubt or negative sentiment. Caution is advised.';

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.300', 'gray.600');
  const aiBgColor = isDataDeficient
    ? 'blue.50'
    : isRecommended
      ? 'green.50'
      : 'red.50';
  const aiBorderColor = isDataDeficient
    ? 'blue.200'
    : isRecommended
      ? 'green.200'
      : 'red.200';

  const renderFormattedMessage = (message) => {
    if (message.startsWith('Data Deficiencies!')) {
      return (
        <>
          <Text as="span" fontWeight="bold" color="blue.800">
            Data Deficiencies!
          </Text>
          {' '}
          <Text as="span" color="gray.800">
            {message.replace('Data Deficiencies!', '')}
          </Text>
        </>
      );
    }

    const highlightRegex = new RegExp(
      [
        '\\d+\\.?\\d*%',
        'Maintain', 'maintain',
        'Consider', 'consider',
        'Diversify', 'diversify',
        'Prioritize', 'prioritize',
        'Monitor', 'monitor',
        'Avoid', 'avoid',
        'Focus', 'focus',
        'Increase', 'increase',
      ].join('|'),
      'g',
    );

    const matches = message.match(highlightRegex) || [];
    const segments = [];
    let lastIndex = 0;

    matches.forEach((match) => {
      const index = message.indexOf(match, lastIndex);
      if (index > lastIndex) {
        segments.push(
          <Text as="span" color="gray.800" key={segments.length}>
            {message.slice(lastIndex, index)}
          </Text>,
        );
      }

      const isPercentage = /^\d+\.?\d*%$/.test(match);
      segments.push(
        <Text
          as="span"
          fontWeight={isPercentage ? 'bold' : 'semibold'}
          color="purple.600"
          key={segments.length}
        >
          {match}
        </Text>,
      );

      lastIndex = index + match.length;
    });

    if (lastIndex < message.length) {
      segments.push(
        <Text as="span" color="gray.800" key={segments.length}>
          {message.slice(lastIndex)}
        </Text>,
      );
    }

    return segments;
  };

  return (
    <Box
      bg={cardBg}
      p={6}
      borderRadius="2xl"
      boxShadow="lg"
      border="1px solid"
      borderColor={borderColor}
      transition="0.3s ease"
    >
      {/* ✅ AI Recommendation */}
      {recommendation_?.message && (
        <Box
          mt={2}
          p={4}
          borderWidth="1px"
          borderRadius="lg"
          bg={aiBgColor}
          borderColor={aiBorderColor}
        >
          <Text fontSize="md" fontWeight="bold" mb={2}>
            AI-Generated Suggestion
          </Text>
          <Text fontSize="sm" lineHeight="1.6">
            {renderFormattedMessage(recommendation_.message)}
          </Text>
          {recommendation_.symbol && (
            <Text fontSize="xs" color="gray.500" mt={2}>
              (for
              {' '}
              {recommendation_.symbol.toUpperCase()}
              )
            </Text>
          )}
        </Box>
      )}

      {/* 🔽 Toggle Detail */}
      <Button
        mt={6}
        size="sm"
        colorScheme="blue"
        variant="outline"
        onClick={() => setShowReason(!showReason)}
        _hover={{ bg: 'blue.50' }}
      >
        {showReason ? 'Hide Details' : 'Do Your Own Research'}
      </Button>

      {/* ⬇ Sentiment Detail */}
      <Collapse in={showReason} animateOpacity>
        <Box mt={4} p={4} borderWidth="1px" borderRadius="lg" bg="gray.50">
          <Text mb={3}>{reason}</Text>
          <Text fontSize="sm" color="gray.600" fontWeight="bold" mb={2}>
            🔍 Sentiment Sources:
          </Text>
          <VStack align="start" spacing={4}>
            {sentiment?.map((item, index) => (
              <Box key={index} w="100%">
                <HStack spacing={3} mb={1}>
                  <Badge
                    colorScheme={
                      item.sentiment === 'positive'
                        ? 'green'
                        : item.sentiment === 'neutral'
                          ? 'yellow'
                          : 'red'
                    }
                  >
                    {item.sentiment.toUpperCase()}
                  </Badge>
                  <Text fontWeight="medium">
                    Score:
                    {' '}
                    {item.sentiment_score.toFixed(2)}
                  </Text>
                </HStack>
                <Text fontSize="sm" color="gray.700">{item.title}</Text>
                <Link
                  href={item.url}
                  color="blue.500"
                  fontSize="sm"
                  isExternal
                >
                  View Source
                  {' '}
                  <ExternalLinkIcon mx="2px" />
                </Link>
                {index !== sentiment.length - 1 && <Divider mt={3} />}
              </Box>
            ))}
          </VStack>
        </Box>
      </Collapse>
    </Box>
  );
}

export default SentimentAnalysis;
