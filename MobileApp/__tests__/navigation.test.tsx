import React from 'react';
import { render } from '@testing-library/react-native';
import App from '../App';

describe('Mobile App Navigation and User Flows', () => {
  it('renders the main App component', () => {
    const { getByText } = render(<App />);
    expect(getByText('Weather App')).toBeTruthy();
  });

  // Additional navigation and user flow tests can be added here as the app grows
});
