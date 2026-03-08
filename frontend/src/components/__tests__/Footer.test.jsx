import React from 'react';
import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import Footer from '../Footer';

const renderWithChakra = (ui) => render(<ChakraProvider>{ui}</ChakraProvider>);

describe('Footer component', () => {
  test('renders current year and copyright text', () => {
    renderWithChakra(<Footer />);
    const year = new Date().getFullYear();
    expect(screen.getByText(`© ${year} Financial Dashboard Group. All rights reserved.`)).toBeInTheDocument();
  });
});
