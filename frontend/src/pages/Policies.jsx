import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Badge, Card } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function Policies() {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchPolicies();
  }, []);

  const fetchPolicies = async () => {
    try {
      const response = await api.get('/policies');
      setPolicies(response.data);
    } catch (error) {
      console.error('Error fetching policies:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'Active': 'success',
      'Expired': 'danger',
      'Cancelled': 'secondary'
    };
    return <Badge bg={variants[status] || 'secondary'}>{status}</Badge>;
  };

  const isActive = (endDate) => {
    return new Date(endDate) > new Date();
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

  return (
    <Container>
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>My Policies</h2>
        <Button variant="primary" onClick={() => navigate('/products')}>
          <i className="bi bi-plus-circle me-2"></i>
          Get New Quote
        </Button>
      </div>

      {policies.length === 0 ? (
        <Card className="text-center p-5">
          <Card.Body>
            <h4>No Policies Yet</h4>
            <p className="text-muted">
              You don't have any active policies. Get a quote to get started.
            </p>
            <Button variant="primary" onClick={() => navigate('/products')}>
              Browse Products
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <Table striped hover responsive>
          <thead>
            <tr>
              <th>Policy #</th>
              <th>Product</th>
              <th>Premium</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {policies.map(policy => (
              <tr key={policy.id}>
                <td>
                  <Link to={`/policies/${policy.id}`}>
                    {policy.policy_number}
                  </Link>
                </td>
                <td>{policy.product_name}</td>
                <td>
                  <strong>${policy.premium_amount.toLocaleString()}/year</strong>
                </td>
                <td>{new Date(policy.start_date).toLocaleDateString()}</td>
                <td>{new Date(policy.end_date).toLocaleDateString()}</td>
                <td>
                  {getStatusBadge(
                    isActive(policy.end_date) ? 'Active' : 'Expired'
                  )}
                </td>
                <td>
                  <Button
                    as={Link}
                    to={`/policies/${policy.id}`}
                    variant="outline-primary"
                    size="sm"
                    className="me-2"
                  >
                    View
                  </Button>
                  {isActive(policy.end_date) && (
                    <Button
                      as={Link}
                      to={`/claims/new?policyId=${policy.id}`}
                      variant="outline-warning"
                      size="sm"
                    >
                      File Claim
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </Container>
  );
}

export default Policies;