import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ClaimDetail from '../pages/ClaimDetail';

// ───────────────────────────────────────────────
// Mocks FIRST — before any import that uses them
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: '123' }),
  };
});

vi.mock('../services/api', () => ({
  default: {
    get: vi.fn(),
  },
}));

// NOW safe to import the mocked module
import api from '../services/api';

const mockClaim = {
  id: 123,
  claim_number: 'CLM-2026-001',
  status: 'Submitted',
  policy_number: 'POL-123',
  policy: { id: 456 },
  incident_date: '2026-01-15',
  filing_date: '2026-01-16',
  claim_amount: 5000,
  description: 'Test claim description',
  documents: [],
};

describe('ClaimDetail Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('displays claim details', async () => {
    api.get.mockResolvedValue({ data: mockClaim });

    render(
      <BrowserRouter>
        <ClaimDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      // Use regex to handle split text nodes ("Claim # CLM-2026-001")
      expect(screen.getByText(/CLM-2026-001/)).toBeInTheDocument();
    });

    expect(screen.getByText('Submitted')).toBeInTheDocument();
    expect(screen.getByText('$5,000.00')).toBeInTheDocument();
    expect(screen.getByText('Test claim description')).toBeInTheDocument();
  });

  // ... add your other tests back here when ready
  // (shows loading spinner, handles not found, etc.)
});