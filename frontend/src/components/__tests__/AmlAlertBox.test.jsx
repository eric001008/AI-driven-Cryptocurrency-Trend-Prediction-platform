import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import AmlAlertBox from '../AmlAlertBox';

const renderWithChakra = (ui) => render(<ChakraProvider>{ui}</ChakraProvider>);

describe('AmlAlertBox', () => {
  test('renders suspicious warning if aml_label is 1', () => {
    const amlData = [
      { symbol: 'btc', aml_label: 1 },
    ];

    renderWithChakra(<AmlAlertBox selectedCoin="BTC" aml={amlData} />);

    expect(screen.getByText(/AML Warning/i)).toBeInTheDocument();
    expect(screen.getByText(/Suspicious transactions detected/i)).toBeInTheDocument();
    expect(screen.getByText(/BTC/i)).toBeInTheDocument();
  });

  test('renders safe status if aml_label is not 1', () => {
    const amlData = [
      { symbol: 'eth', aml_label: 0 },
    ];

    renderWithChakra(<AmlAlertBox selectedCoin="ETH" aml={amlData} />);

    expect(screen.getByText(/AML Status/i)).toBeInTheDocument();
    expect(screen.getByText(/No suspicious activity detected/i)).toBeInTheDocument();
    expect(screen.getByText(/ETH/i)).toBeInTheDocument();
  });

  test('renders nothing suspicious if no matching coin found', () => {
    const amlData = [
      { symbol: 'xrp', aml_label: 0 },
    ];

    renderWithChakra(<AmlAlertBox selectedCoin="DOGE" aml={amlData} />);

    expect(screen.getByText(/AML Status/i)).toBeInTheDocument();
    expect(screen.getByText(/No suspicious activity detected/i)).toBeInTheDocument();
    expect(screen.getByText(/DOGE/i)).toBeInTheDocument();
  });
});
