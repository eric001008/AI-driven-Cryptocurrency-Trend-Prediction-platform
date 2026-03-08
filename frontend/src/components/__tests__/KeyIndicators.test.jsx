import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import KeyIndicators from '../KeyIndicators';

const renderWithChakra = (ui) => render(<ChakraProvider>{ui}</ChakraProvider>);

describe('KeyIndicators component', () => {
  test('renders spinner when loading is true', () => {
    renderWithChakra(<KeyIndicators loading statistic={null} />);
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('renders indicator items when data is present', () => {
    const mockData = {
      market_cap: 123456789,
      volume_24h: 98765432,
      circulating_supply: 19000000,
      total_supply: 21000000,
      max_supply: null,
      percent_change_24h: 2.45,
      percent_change_7d: -1.23,
    };

    renderWithChakra(<KeyIndicators loading={false} statistic={mockData} />);

    expect(screen.getByTestId('indicator-Market Cap')).toHaveTextContent('$123,456,789');
    expect(screen.getByTestId('indicator-24h Volume')).toHaveTextContent('$98,765,432');
    expect(screen.getByTestId('indicator-Circulating Supply')).toHaveTextContent('19,000,000');
    expect(screen.getByTestId('indicator-Total Supply')).toHaveTextContent('21,000,000');
    expect(screen.getByTestId('indicator-Max Supply')).toHaveTextContent('Unlimited');
    expect(screen.getByTestId('indicator-24h Change')).toHaveTextContent('2.45%');
    expect(screen.getByTestId('indicator-7d Change')).toHaveTextContent('-1.23%');
  });

  test('renders correct color for positive and negative changes', () => {
    const mockData = {
      percent_change_24h: -2.45,
      percent_change_7d: 3.67,
    };

    renderWithChakra(<KeyIndicators loading={false} statistic={mockData} />);

    const negativeEl = screen.getByTestId('indicator-24h Change');
    const positiveEl = screen.getByTestId('indicator-7d Change');

    // Chakra red.500 → rgb(229, 62, 62)
    // Chakra green.500 → rgb(56, 161, 105)
    expect(getComputedStyle(negativeEl).color).toBe('rgb(229, 62, 62)');
    expect(getComputedStyle(positiveEl).color).toBe('rgb(56, 161, 105)');
  });

  test('renders fallback text when no data is available', () => {
    renderWithChakra(<KeyIndicators loading={false} statistic={null} />);
    expect(screen.getByText('No indicator data available.')).toBeInTheDocument();
  });
});
