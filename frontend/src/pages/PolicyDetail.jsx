import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Button, Badge, Table, Alert } from 'react-bootstrap';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function PolicyDetail() {
  const [policy, setPolicy] = useState(null);
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { id } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    fetchPolicy();
    fetchPayments();
  }, [id]);

  const fetchPolicy = async () => {
    try {
      const response = await api.get(`/policies/${id}`);
      setPolicy(response.data);
    } catch (error) {
      console.error('Error fetching policy:', error);
      setError('Failed to load policy details');
    } finally {
      setLoading(false);
    }
  };

  const fetchPayments = async () => {
    try {
      const response = await api.get('/payments');
      const policyPayments = response.data.filter(p => p.policy_number === policy?.policy_number);
      setPayments(policyPayments);
    } catch (error) {
      console.error('Error fetching payments:', error);
    }
  };

  const handleMakePayment = async () => {
    try {
      await api.post(`/policies/${policy.id}/payments`, {
        payment_method: 'Credit Card'
      });
      alert('Payment successful!');
      fetchPayments();
    } catch (error) {
      console.error('Error making payment:', error);
      alert('Payment failed. Please try again.');
    }
  };

  const handleFileClaim = () => {
    navigate(`/claims/new?policyId=${policy.id}`);
  };

  const isActive = () => {
    return new Date(policy?.end_date) > new Date();
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

  if (error || !policy) {
    return (
      <Container className="text-center mt-5">
        <Alert variant="danger">{error || 'Policy not found'}</Alert>
        <Button as={Link} to="/policies" variant="primary">
          Back to Policies
        </Button>
      </Container>
    );
  }

  return (
    <Container>
      <Row className="mb-4">
        <Col>
          <h2>Policy Details</h2>
          <p className="text-muted">Policy #{policy.policy_number}</p>
        </Col>
        <Col className="text-end">
          <Button as={Link} to="/policies" variant="outline-secondary">
            Back to Policies
          </Button>
        </Col>
      </Row>

      <Row>
        <Col md={8}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Policy Information</h5>
            </Card.Header>
            <Card.Body>
              <Table borderless>
                <tbody>
                  <tr>
                    <td className="fw-bold" style={{ width: '200px' }}>Status:</td>
                    <td>
                      <Badge bg={isActive() ? 'success' : 'danger'}>
                        {isActive() ? 'Active' : 'Expired'}
                      </Badge>
                    </td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Product:</td>
                    <td>{policy.product.name}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Category:</td>
                    <td>{policy.product.category}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Premium Amount:</td>
                    <td>
                      <h4 className="text-primary mb-0">
                        ${policy.premium_amount.toLocaleString()}/year
                      </h4>
                    </td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Start Date:</td>
                    <td>{new Date(policy.start_date).toLocaleDateString()}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">End Date:</td>
                    <td>{new Date(policy.end_date).toLocaleDateString()}</td>
                  </tr>
                  <tr>
                    <td className="fw-bold">Created:</td>
                    <td>{new Date(policy.created_at).toLocaleDateString()}</td>
                  </tr>
                </tbody>
              </Table>
            </Card.Body>
          </Card>

          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Coverage Details</h5>
            </Card.Header>
            <Card.Body>
              <p>{policy.product.coverage_details}</p>
              <h6 className="mt-3">What's Covered:</h6>
              <ul>
                <li>Liability protection</li>
                <li>Property damage</li>
                <li>Medical payments</li>
                <li>Personal injury protection</li>
              </ul>
            </Card.Body>
          </Card>

          {payments.length > 0 && (
            <Card>
              <Card.Header>
                <h5 className="mb-0">Payment History</h5>
              </Card.Header>
              <Card.Body>
                <Table striped hover responsive size="sm">
                  <thead>
                    <tr>
                      <th>Transaction ID</th>
                      <th>Date</th>
                      <th>Amount</th>
                      <th>Method</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {payments.map(payment => (
                      <tr key={payment.id}>
                        <td>{payment.transaction_id}</td>
                        <td>{new Date(payment.payment_date).toLocaleDateString()}</td>
                        <td>${payment.amount.toLocaleString()}</td>
                        <td>{payment.payment_method}</td>
                        <td>
                          <Badge bg="success">{payment.status}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </Card.Body>
            </Card>
          )}
        </Col>

        <Col md={4}>
          <Card className="mb-4">
            <Card.Header>
              <h5 className="mb-0">Actions</h5>
            </Card.Header>
            <Card.Body>
              {isActive() ? (
                <>
                  <Button 
                    variant="success" 
                    className="w-100 mb-2"
                    onClick={handleMakePayment}
                  >
                    Make a Payment
                  </Button>
                  <Button 
                    variant="warning" 
                    className="w-100 mb-2"
                    onClick={handleFileClaim}
                  >
                    File a Claim
                  </Button>
                  <Button 
                    variant="outline-primary" 
                    className="w-100 mb-2"
                    as={Link}
                    to={`/policies/${policy.id}/documents`}
                  >
                    View Documents
                  </Button>
                </>
              ) : (
                <Alert variant="warning">
                  This policy has expired. Please contact support to renew.
                </Alert>
              )}
              
              <hr />
              
              <Button 
                variant="outline-secondary" 
                className="w-100"
                as={Link}
                to={`/claims?policyId=${policy.id}`}
              >
                View Related Claims
              </Button>
            </Card.Body>
          </Card>

          <Card>
            <Card.Header>
              <h5 className="mb-0">Need Help?</h5>
            </Card.Header>
            <Card.Body>
              <p>
                Contact our support team for assistance with your policy.
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

export default PolicyDetail;
