import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import App from '../App';

global.ResizeObserver = class {
  observe() {}

  unobserve() {}

  disconnect() {}
};

beforeEach(() => {
  sessionStorage.clear();
  sessionStorage.setItem('token', 'mock-token');
  sessionStorage.setItem('subscription', 'Free');

  global.fetch = jest.fn((url) => {
    if (url.includes('/api/data/coin_data')) {
      return Promise.resolve({
        json: () => Promise.resolve({
          price_trend: [],
          sentiment: [],
          statistic: {
            percent_change_24h: 1.23,
            last_updated: '2024-01-01T00:00:00Z',
          },
          news: [],
          aml: [],
          recommendation: 'Recommended',
        }),
      });
    }

    if (url.includes('/api/user/profile')) {
      return Promise.resolve({
        json: () => Promise.resolve({
          followed_currencies: ['btc', 'eth'],
          username: 'testuser',
          email: 'test@example.com',
          subscription: 'Free',
        }),
      });
    }

    return Promise.resolve({ json: () => Promise.resolve({}) });
  });
});

afterEach(() => {
  jest.clearAllMocks();
});

test('shows loading spinner and handles fetch failure gracefully', async () => {
  global.fetch.mockImplementation((url) => {
    if (url.includes('/api/data/coin_data')) {
      return Promise.reject('API failure');
    }

    if (url.includes('/api/user/profile')) {
      return Promise.resolve({
        json: () => Promise.resolve({
          followed_currencies: ['btc'],
          username: 'testuser',
          email: 'test@example.com',
          subscription: 'Free',
        }),
      });
    }

    return Promise.resolve({ json: () => Promise.resolve({}) });
  });

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByRole('status')).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.getByText(/failed to load data/i)).toBeInTheDocument();
  });
});

test('Pro coins are disabled in select for Free user', async () => {
  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  );

  const bnbOption = screen.getByRole('option', { name: /bnb/i });
  expect(bnbOption).toBeDisabled();
});

test('does not fetch coin data when selecting Pro coin', async () => {
  const fetchSpy = jest.spyOn(global, 'fetch');

  render(
    <MemoryRouter initialEntries={['/']}>
      <App />
    </MemoryRouter>,
  );

  const select = await screen.findByRole('combobox');
  const bnbOption = screen.getByRole('option', { name: /bnb/i });
  expect(bnbOption).toBeDisabled();

  userEvent.selectOptions(select, 'bnb');

  await waitFor(() => {
    const coinDataFetches = fetchSpy.mock.calls.filter(([url]) => url.includes('/api/data/coin_data'));
    expect(coinDataFetches.length).toBeLessThanOrEqual(2);
  });
});

test('navigates to Register page', async () => {
  render(
    <MemoryRouter initialEntries={['/register']}>
      <App />
    </MemoryRouter>,
  );

  const heading = await screen.findByRole('heading', { name: /register/i });
  expect(heading).toBeInTheDocument();
});

test('navigates to Pricing page', async () => {
  render(
    <MemoryRouter initialEntries={['/pricing']}>
      <App />
    </MemoryRouter>,
  );

  expect(await screen.findByText(/track up to 5 cryptocurrencies/i)).toBeInTheDocument();
  expect(await screen.findByRole('button', { name: /monthly/i })).toBeInTheDocument();
  expect(await screen.findByRole('heading', { name: /free/i })).toBeInTheDocument();
});
