import { render, screen } from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../../App';

beforeEach(() => {
  fetch.resetMocks();
});

test('renders dashboard title', async () => {
  fetch.mockResponseOnce(JSON.stringify({
    coin: 'btc',
    data: {},
  }));

  render(
    <BrowserRouter>
      <ChakraProvider>
        <App />
      </ChakraProvider>
    </BrowserRouter>,
  );

  const titleElement = await screen.findByText(/financial data dashboard/i);
  expect(titleElement).toBeInTheDocument();
});
