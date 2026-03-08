import React from 'react';
import {
  render, screen, waitFor, fireEvent,
  within,
} from '@testing-library/react';
import { ChakraProvider } from '@chakra-ui/react';
import UserProfile from '../UserProfile';

// Helper to render with Chakra

const renderWithProvider = () => render(
  <ChakraProvider>
    <UserProfile />
  </ChakraProvider>,
);

beforeEach(() => {
  jest.clearAllMocks();
  global.fetch = jest.fn();
  sessionStorage.clear();
});

test('renders user profile data', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      username: 'testuser',
      email: 'test@example.com',
      subscription_plan: 'Pro',
      rating: 'Intermediate',
      followed_currencies: ['btc', 'eth'],
      max_currencies: 3,
    }),
  });

  renderWithProvider();

  await waitFor(() => {
    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.getByText('test@example.com')).toBeInTheDocument();
    expect(screen.getByText('Pro')).toBeInTheDocument();
    expect(screen.getByText('Intermediate')).toBeInTheDocument();
    expect(screen.getByText('btc')).toBeInTheDocument();
    expect(screen.getByText('eth')).toBeInTheDocument();
  });
});

test('shows loading spinner', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: () => new Promise((resolve) => {
      setTimeout(() => resolve({}), 100);
    }),

  });

  renderWithProvider();
  expect(screen.getByText(/loading profile/i)).toBeInTheDocument();
});

test('shows error if not logged in', async () => {
  renderWithProvider();
  await waitFor(() => {
    expect(screen.getByText(/please log in to view your profile/i)).toBeInTheDocument();
  });
});

test('shows error when fetch fails', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch.mockResolvedValueOnce({
    ok: false,
    json: async () => ({ message: 'Unauthorized' }),
  });

  renderWithProvider();

  await waitFor(() => {
    expect(screen.getByText(/unauthorized/i)).toBeInTheDocument();
  });
});

test('blocks Free users from editing preferences', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      username: 'testuser',
      email: 'test@example.com',
      subscription_plan: 'Free',
      rating: 'Beginner',
      followed_currencies: ['btc'],
      max_currencies: 2,
    }),
  });

  renderWithProvider();

  await screen.findByText('btc');

  const editButton = screen.getByRole('button', { name: /edit/i });
  fireEvent.click(editButton);

  expect(await screen.findByText(/upgrade required/i)).toBeInTheDocument();
});

test('allows Pro users to open modal and save preferences', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        username: 'prouser',
        email: 'pro@example.com',
        subscription_plan: 'Pro',
        rating: 'Intermediate',
        followed_currencies: ['btc'],
        max_currencies: 2,
      }),
    })
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({}),
    });

  renderWithProvider();

  await screen.findByText('btc');
  const editButton = screen.getByRole('button', { name: /edit/i });
  fireEvent.click(editButton);

  const checkbox = await screen.findByLabelText(/ethereum/i);
  fireEvent.click(checkbox);

  const saveBtn = screen.getByRole('button', { name: /save preferences/i });
  fireEvent.click(saveBtn);

  await waitFor(() => {
    expect(screen.getByText(/preferences updated/i)).toBeInTheDocument();
  });
});

test('shows error if saving preferences fails', async () => {
  sessionStorage.setItem('token', 'mock-token');
  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        username: 'prouser',
        email: 'pro@example.com',
        subscription_plan: 'Pro',
        rating: 'Intermediate',
        followed_currencies: ['btc'],
        max_currencies: 2,
      }),
    })
    .mockResolvedValueOnce({
      ok: false,
      json: async () => ({ message: 'Update failed' }),
    });

  renderWithProvider();

  await screen.findByText('btc');
  const editButton = screen.getByRole('button', { name: /edit/i });
  fireEvent.click(editButton);

  const checkbox = await screen.findByLabelText(/ethereum/i);
  fireEvent.click(checkbox);

  const saveBtn = screen.getByRole('button', { name: /save preferences/i });
  fireEvent.click(saveBtn);

  await waitFor(() => {
    expect(screen.getByText(/error updating preferences/i)).toBeInTheDocument();
  });
});

test('disables checkboxes beyond max selection', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch
    .mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        username: 'pro_user',
        email: 'pro@example.com',
        subscription_plan: 'Pro',
        rating: 'Intermediate',
        followed_currencies: ['btc', 'eth'],
        max_currencies: 2,
      }),
    })
    .mockResolvedValueOnce({
      ok: true,

      json: async () => ({}),
    });

  renderWithProvider();

  await screen.findByText('btc');

  fireEvent.click(screen.getByRole('button', { name: /edit/i }));

  const disabledCheckbox = await screen.findByLabelText(/usdt/i);
  expect(disabledCheckbox).toBeDisabled();
});

test('shows fallback text when rating is not set', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      username: 'no_rating_user',
      email: 'x@example.com',
      subscription_plan: 'Pro',
      rating: null, // ⚠️ no rating
      followed_currencies: [],
      max_currencies: 3,
    }),
  });

  renderWithProvider();

  await screen.findByText(/not completed yet/i);
});

test('uses default max_currencies if missing', async () => {
  sessionStorage.setItem('token', 'mock-token');

  global.fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      username: 'default_limit_user',
      email: 'd@example.com',
      subscription_plan: 'Pro',
      followed_currencies: [],
      rating: 'Beginner',
      // no max_currencies
    }),
  });

  renderWithProvider();

  await screen.findByText('default_limit_user');

  fireEvent.click(screen.getByRole('button', { name: /edit/i }));

  const modal = await screen.findByRole('dialog');

  fireEvent.click(within(modal).getByLabelText(/bitcoin/i));
  fireEvent.click(within(modal).getByLabelText(/ethereum/i));
  fireEvent.click(within(modal).getByLabelText(/tether/i));

  const disabledCheckbox = within(modal).getByLabelText(/bnb/i);
  expect(disabledCheckbox).toBeDisabled();
});
