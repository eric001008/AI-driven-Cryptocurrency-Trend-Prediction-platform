// src/components/__tests__/LockedOverlay.test.jsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import LockedOverlay from '../LockedOverlay';

describe('LockedOverlay', () => {
  test('renders child content', () => {
    render(
      <LockedOverlay>
        <div>Protected Content</div>
      </LockedOverlay>,
    );
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  test('renders overlay message', () => {
    render(
      <LockedOverlay>
        <div>Protected Content</div>
      </LockedOverlay>,
    );
    expect(
      screen.getByText(/please register to access this content/i),
    ).toBeInTheDocument();
  });
});
