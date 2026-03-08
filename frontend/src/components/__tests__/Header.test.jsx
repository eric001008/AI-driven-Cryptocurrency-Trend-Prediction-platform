import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ChakraProvider } from '@chakra-ui/react';
import Header from '../Header';

// mock navigate
const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => {
  const original = jest.requireActual('react-router-dom');
  return {
    ...original,
    useNavigate: () => mockNavigate,
    Link: original.Link,
  };
});

const renderHeader = (session = {}, withProps = true) => {
  jest.spyOn(Storage.prototype, 'getItem').mockImplementation((key) => session[key]);
  jest.spyOn(Storage.prototype, 'clear').mockImplementation(() => {});

  const setIsLoggedIn = jest.fn();
  const setSubscription = jest.fn();

  render(
    <BrowserRouter>
      <ChakraProvider>
        <Header
          {...(withProps ? { setIsLoggedIn, setSubscription } : {})}
        />
      </ChakraProvider>
    </BrowserRouter>,
  );

  return { setIsLoggedIn, setSubscription };
};

describe('Header component', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  test('renders Dashboard and Pricing links', () => {
    renderHeader();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Pricing')).toBeInTheDocument();
  });

  test('shows Sign In and Register when not logged in', () => {
    renderHeader({ token: null });
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByText('Register')).toBeInTheDocument();
  });

  test('shows account menu when logged in', () => {
    renderHeader({ token: 'fake-token' });
    expect(screen.getByRole('button', { name: /account/i })).toBeInTheDocument();
  });

  test('handles logout correctly with props', () => {
    const { setIsLoggedIn, setSubscription } = renderHeader({ token: 'token123' });

    const accountBtn = screen.getByRole('button', { name: /account/i });
    fireEvent.click(accountBtn);

    const logoutItem = screen.getByText('Log Out');
    fireEvent.click(logoutItem);

    expect(window.sessionStorage.clear).toHaveBeenCalled();
    expect(setIsLoggedIn).toHaveBeenCalledWith(false);
    expect(setSubscription).toHaveBeenCalledWith('Free');
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  test('handles logout gracefully without props', () => {
    renderHeader({ token: 'token123' }, false); // 不传 props

    const accountBtn = screen.getByRole('button', { name: /account/i });
    fireEvent.click(accountBtn);

    const logoutItem = screen.getByText('Log Out');
    fireEvent.click(logoutItem);

    expect(window.sessionStorage.clear).toHaveBeenCalled();

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
