import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ChakraProvider, useToast } from '@chakra-ui/react';
import Pricing from '../Pricing';

// mock useToast
jest.mock('@chakra-ui/react', () => {
  const actual = jest.requireActual('@chakra-ui/react');
  return {
    ...actual,
    useToast: jest.fn(),
  };
});

describe('Pricing Page', () => {
  let toastMock;

  beforeEach(() => {
    toastMock = jest.fn();
    useToast.mockReturnValue(toastMock);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderWithChakra = (ui) => render(<ChakraProvider>{ui}</ChakraProvider>);

  test('renders billing toggle buttons and switches billing mode', () => {
    renderWithChakra(<Pricing />);

    const monthlyBtn = screen.getByTestId('billing-monthly');
    const yearlyBtn = screen.getByTestId('billing-yearly');

    expect(monthlyBtn).toBeInTheDocument();
    expect(yearlyBtn).toBeInTheDocument();

    fireEvent.click(yearlyBtn);
    fireEvent.click(monthlyBtn);
  });

  test('renders 3 pricing plans', () => {
    renderWithChakra(<Pricing />);
    const headings = screen.getAllByRole('heading', { level: 3 });
    expect(headings).toHaveLength(3); // Free, Pro, Pro Max
  });

  test('clicking on a plan button triggers toast', () => {
    renderWithChakra(<Pricing />);
    const buttons = screen.getAllByRole('button', { name: /upgrade|subscribed/i });

    buttons.forEach((btn) => {
      fireEvent.click(btn);
    });

    expect(toastMock).toHaveBeenCalledTimes(3); // 3 plans, 3 toasts
    expect(toastMock).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'Coming Soon!',
        description: expect.any(String),
        status: 'info',
      }),
    );
  });
});
