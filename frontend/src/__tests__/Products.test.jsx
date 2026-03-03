import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Products from '../pages/Products';

// Mock BEFORE import
vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
  },
}));

// Import AFTER mock
import api from '../services/api';

vi.mock('@auth0/auth0-react', () => ({
  useAuth0: () => ({
    isAuthenticated: false,
    loginWithRedirect: vi.fn(),
  }),
}));

const mockProducts = [
  {
    id: 1,
    name: 'Test Auto Insurance',
    category: 'Auto',
    coverage_details: 'Test coverage',
    base_price: 500,
  },
  {
    id: 2,
    name: 'Test Home Insurance',
    category: 'Home',
    coverage_details: 'Test coverage',
    base_price: 600,
  },
];

describe('Products Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('shows loading spinner initially', () => {
    api.get.mockResolvedValue({ data: [] });

    render(
      <BrowserRouter>
        <Products />
      </BrowserRouter>
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  test('displays products after loading', async () => {
    api.get.mockResolvedValue({ data: mockProducts });

    render(
      <BrowserRouter>
        <Products />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Auto Insurance')).toBeInTheDocument();
      expect(screen.getByText('Test Home Insurance')).toBeInTheDocument();
    });
  });

  test('filters products by category', async () => {
    api.get.mockResolvedValue({ data: mockProducts });

    render(
      <BrowserRouter>
        <Products />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Auto Insurance')).toBeInTheDocument();
      expect(screen.getByText('Test Home Insurance')).toBeInTheDocument();
    });

    // Only one combobox exists → safe to use without name
    const categorySelect = screen.getByRole('combobox');

    fireEvent.change(categorySelect, { target: { value: 'Auto' } });

    await waitFor(() => {
      expect(screen.getByText('Test Auto Insurance')).toBeInTheDocument();
      expect(screen.queryByText('Test Home Insurance')).not.toBeInTheDocument();
    });
  });

  test('handles API error', async () => {
    api.get.mockRejectedValue(new Error('API Error'));

    render(
      <BrowserRouter>
        <Products />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(
        screen.getByText(/No products found matching your criteria/i)
      ).toBeInTheDocument();
    });
  });
});