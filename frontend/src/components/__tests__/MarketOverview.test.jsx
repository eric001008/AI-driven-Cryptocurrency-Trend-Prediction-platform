import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import MarketOverview from '../MarketOverview';

// mock ResizeObserver for recharts
beforeAll(() => {
  global.ResizeObserver = class {
    observe() {}

    unobserve() {}

    disconnect() {}
  };
});

const mockData = [
  {
    last_updated: new Date().toISOString(),
    price: 12345.67,
  },
];

const renderWithChakra = (ui) => render(<ChakraProvider>{ui}</ChakraProvider>);

describe('MarketOverview Component', () => {
  test('renders spinner when loading is true', () => {
    renderWithChakra(
      <MarketOverview
        selectedCoin="btc"
        price_trend={[]}
        percent_change_24h={0}
        loading
      />,
    );
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  test('renders price and percent change when loading is false', () => {
    renderWithChakra(
      <MarketOverview
        selectedCoin="eth"
        price_trend={mockData}
        percent_change_24h={1.23}
        loading={false}
      />,
    );

    const priceElements = screen.queryAllByText((_, el) => el.textContent.includes('$12345.67'));
    expect(priceElements.length).toBeGreaterThan(0);

    const percentElements = screen.queryAllByText((_, el) => el.textContent.includes('1.23%'));
    expect(percentElements.length).toBeGreaterThan(0);
  });

  test('shows negative percent change in red', () => {
    renderWithChakra(
      <MarketOverview
        selectedCoin="eth"
        price_trend={mockData}
        percent_change_24h={-2.5}
        loading={false}
      />,
    );

    const negativeText = screen.queryAllByText((_, el) => el.textContent.includes('-2.50%'));
    expect(negativeText.length).toBeGreaterThan(0);
  });
});
