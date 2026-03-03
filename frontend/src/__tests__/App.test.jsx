import { render, screen } from '@testing-library/react';
import App from '../App';

vi.mock('@auth0/auth0-react', () => ({
  Auth0Provider: ({ children }) => children,
  useAuth0: () => ({
    isLoading: false,
    isAuthenticated: false,
    user: null,
    loginWithRedirect: vi.fn(),
    logout: vi.fn(),
  }),
}));

describe('App Component', () => {
  test('renders the app root without crashing', () => {
    render(<App />); // no extra BrowserRouter – App already has it

    // More specific: look for the main welcome heading
    expect(
      screen.getByRole('heading', { name: /Welcome to InsuranceApp/i })
    ).toBeInTheDocument();

    // Optional additional checks
    expect(screen.getByText(/Protecting what matters most/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Get Started Today/i })).toBeInTheDocument();
  });
});