import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Badge, Table } from 'react-bootstrap';
import { useParams, useNavigate, Link } from 'react-router-dom';
import api from '../services/api';

function QuoteDetail() {
  const [quote, setQuote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchQuote();
  }, [id]);

  const fetchQuote = async () => {
    try {
      const response = await api.get(`/quotes/${id}`);
      setQuote(response.data);
    } catch (error) {
      console.error('Error fetching quote:', error);
      setError('Failed to load quote details');
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptQuote = async () => {
    try {
      const response = await api.post('/policies', {
        quote_id: quote.id
      });
      navigate(`/policies/${response.data.id}`);
    } catch (error) {
      console.error('Error accepting quote:', error);
      alert('Failed to accept quote. Please try again.');
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'Pending': 'warning',
      'Accepted': 'success',
      'Expired': 'danger'
    };
    return (
      <Badge bg={variants[status] || 'secondary'} className="status-badge">
        {status}
      </Badge>
    );
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </Container>
    );
  }

  if (error || !quote) {
    return (
      <Container className="text-center mt-5">
        <Alert variant="danger">{error || 'Quote not found'}</Alert>
        <Button as={Link} to="/quotes" variant="primary">
          Back to Quotes
        </Button>
      </Container>
    );
  }

  const isExpired = new Date(quote.expires_at) < new Date();
  const canAccept = quote.status === 'Pending' && !isExpired;

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h2>Quote Details</h2>
          <p className="text-muted">Quote #{quote.quote_number}</p>
        </Col>
        <Col className="text-end">
          <Button as={Link} to="/quotes" variant="outline-secondary">
            Back to Quotes
          </Button>
        </Col>
      </Row>

      <Row>
        <Col md={8}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Quote Information</h5>
            </Card.Header>
            <Card.Body>
              <Table borderless>
                <tbody>
                  <tr>
                    <td className="fw-bold" style={{ width: '200px' }}>Status:</td>
                    <td>{getStatusBadge(quote.status)}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Product:</td>
                    <td>{quote.product.name}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Category:</td>
                    <td>{quote.product.category}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Coverage Amount:</td>
                    <td>${quote.coverage_amount?.toLocaleString()}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Deductible:</td>
                    <td>${quote.deductible?.toLocaleString()}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Calculated Premium:</td>
                    <td>
                      <h4 className="text-primary mb-0">
                        ${quote.calculated_price?.toLocaleString()}/year
                      </h4>
                    </td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Created Date:</td>
                    <td>{new Date(quote.created_at).toLocaleString()}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Expires:</td>
                    <td className={isExpired ? 'text-danger' : ''}>
                      {new Date(quote.expires_at).toLocaleString()}
                      {isExpired && ' (Expired)'}
                    </td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          <Card>
            <Card.Header>
              <h5 className="mb-0">Coverage Details</h5>
            </Card.Header>
            <Card.Body>
              <p>{quote.product.coverage_details}</p>
              <ul className="mt-3">
                <li>Liability coverage included</li>
                <li>24/7 claims support</li>
                <li>Flexible payment options</li>
                <li>Online account management</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>

        <Col md={4}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Actions</h5>
            </Card.Header>
            <Card.Body>
              {canAccept ? (
                <>
                  <p className="text-success">
                    <i className="bi bi-check-circle"></i> This quote is ready to accept
                  </p>
                  <Button 
                    variant="success" 
                    size="lg" 
                    className="w-100 mb-2"
                    onClick={handleAcceptQuote}
                  >
                    Accept Quote & Purchase Policy
                  </Button>
                  <p className="small text-muted">
                    By accepting, you agree to purchase this policy at the quoted premium.
                  </p>
                </>
              ) : quote.status === 'Accepted' ? (
                <>
                  <Alert variant="success">
                    This quote has been accepted and converted to a policy.
                  </Alert>
                  <Button 
                    as={Link}
                    to={`/policies/${quote.id}`}
                    variant="primary" 
                    className="w-100"
                  >
                    View Policy
                  </Button>
                </>
              ) : (
                <Alert variant="danger">
                  This quote is no longer available for acceptance.
                </Alert>
              )}
            </Card.Body>
          </Card>

          <Card>
            <Card.Header>
              <h5 className="mb-0">Need Help?</h5>
            </Card.Header>
            <Card.Body>
              <p>
                Contact our support team if you have questions about this quote.
              </p>
              <Button variant="outline-primary" className="w-100">
                Contact Support
              </Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default QuoteDetail;

