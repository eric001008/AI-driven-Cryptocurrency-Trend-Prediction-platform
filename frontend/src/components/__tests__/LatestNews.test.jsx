// src/components/__tests__/LatestNews.test.jsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import LatestNews from '../LatestNews';

const renderWithChakra = (ui) => render(<ChakraProvider>{ui}</ChakraProvider>);

describe('LatestNews Component', () => {
  test('renders loading spinner when loading is true', () => {
    renderWithChakra(
      <LatestNews selectedCoin="btc" latest_news={[]} lastUpdated={null} loading />,
    );
    expect(screen.getByRole('status')).toBeInTheDocument(); // Chakra Spinner
  });

  test('renders news items when loading is false', () => {
    const mockNews = [
      {
        title: 'Bitcoin reaches new high',
        url: 'https://example.com/bitcoin-news',
      },
      {
        title: 'Investors eye crypto surge',
        url: 'https://example.com/investors-crypto',
      },
    ];

    renderWithChakra(
      <LatestNews
        selectedCoin="btc"
        latest_news={mockNews}
        lastUpdated={null}
        loading={false}
      />,
    );

    expect(screen.getByText('Bitcoin reaches new high')).toBeInTheDocument();
    expect(screen.getByText('Investors eye crypto surge')).toBeInTheDocument();
    expect(screen.getAllByText(/View Source/i).length).toBe(2);
  });

  test('renders fallback message if no news', () => {
    renderWithChakra(
      <LatestNews selectedCoin="eth" latest_news={[]} lastUpdated={null} loading={false} />,
    );

    expect(screen.getByText(/No news available for ETH/i)).toBeInTheDocument();
  });

  test('renders last updated time if provided', () => {
    const timestamp = new Date('2025-07-26T10:30:00Z').toISOString();

    renderWithChakra(
      <LatestNews
        selectedCoin="btc"
        latest_news={[]}
        lastUpdated={timestamp}
        loading={false}
      />,
    );

    expect(screen.getByText(/Last Updated:/)).toBeInTheDocument();
  });
});
