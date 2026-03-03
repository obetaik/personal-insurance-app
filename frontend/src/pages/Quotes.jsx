import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Badge, Card, Alert } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function Quotes() {
  const [quotes, setQuotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchQuotes();
  }, []);

  const fetchQuotes = async () => {
    try {
      console.log('📊 Fetching quotes...');
      const response = await api.get('/quotes');
      console.log('✅ Quotes received:', response.data);
      
      // Ensure response.data is an array
      if (Array.isArray(response.data)) {
        setQuotes(response.data);
        setError(null);
      } else {
        console.error('❌ Response is not an array:', response.data);
        setError('Invalid data format received from server');
      }
    } catch (error) {
      console.error('❌ Error fetching quotes:', error);
      setError(error.response?.data?.error || error.message || 'Failed to load quotes');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptQuote = async (quoteId) => {
    try {
      console.log('📊 Accepting quote:', quoteId);
      const response = await api.post('/policies', {
        quote_id: quoteId
      });
      console.log('✅ Policy created:', response.data);
      navigate(`/policies/${response.data.id}`);
    } catch (error) {
      console.error('❌ Error accepting quote:', error);
      alert(error.response?.data?.error || 'Failed to accept quote. Please try again.');
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'Pending': 'warning',
      'Accepted': 'success',
      'Expired': 'danger'
    };
    return variants[status] || 'secondary';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      console.error('Date formatting error:', error);
      return 'Invalid Date';
    }
  };

  const formatCurrency = (amount) => {
    if (amount === undefined || amount === null) return '$0';
    try {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount);
    } catch (error) {
      console.error('Currency formatting error:', error);
      return `$${amount}`;
    }
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3 text-muted">Loading your quotes...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <Alert.Heading>Error Loading Quotes</Alert.Heading>
          <p>{error}</p>
          <Button variant="primary" onClick={fetchQuotes}>
            Retry
          </Button>
        </Alert>
      </Container>
    );
  }

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2>My Quotes</h2>
          <p className="text-muted">Manage and track your insurance quotes</p>
        </div>
        <Button 
          variant="primary" 
          onClick={() => navigate('/products')}
          size="lg"
        >
          <i className="bi bi-plus-circle me-2"></i>
          Get New Quote
        </Button>
      </div>

      {quotes.length === 0 ? (
        <Card className="text-center p-5">
          <Card.Body>
            <div className="mb-4">
              <i className="bi bi-file-text" style={{ fontSize: '4rem', color: '#dee2e6' }}></i>
            </div>
            <h4>No Quotes Yet</h4>
            <p className="text-muted mb-4">
              Get started by requesting a quote for one of our insurance products.
            </p>
            <Button 
              variant="primary" 
              onClick={() => navigate('/products')}
              size="lg"
            >
              Browse Products
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <div className="table-container">
          <Table striped hover responsive className="mb-0">
            <thead>
              <tr>
                <th>Quote #</th>
                <th>Product</th>
                <th>Coverage</th>
                <th>Premium</th>
                <th>Status</th>
                <th>Created</th>
                <th>Expires</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {quotes.map(quote => (
                <tr key={quote.id}>
                  <td>
                    <Link to={`/quotes/${quote.id}`} className="fw-bold">
                      {quote.quote_number}
                    </Link>
                  </td>
                  <td>{quote.product_name}</td>
                  <td>{formatCurrency(quote.coverage_amount)}</td>
                  <td>
                    <strong className="text-primary">
                      {formatCurrency(quote.calculated_price)}
                    </strong>
                  </td>
                  <td>
                    <Badge bg={getStatusBadge(quote.status)} className="px-3 py-2">
                      {quote.status}
                    </Badge>
                  </td>
                  <td>{formatDate(quote.created_at)}</td>
                  <td>{formatDate(quote.expires_at)}</td>
                  <td>
                    <Button
                      as={Link}
                      to={`/quotes/${quote.id}`}
                      variant="outline-primary"
                      size="sm"
                      className="me-2"
                    >
                      <i className="bi bi-eye me-1"></i>
                      View
                    </Button>
                    {quote.status === 'Pending' && (
                      <Button
                        variant="success"
                        size="sm"
                        onClick={() => handleAcceptQuote(quote.id)}
                      >
                        <i className="bi bi-check-circle me-1"></i>
                        Accept
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </div>
      )}
    </Container>
  );
}

export default Quotes;