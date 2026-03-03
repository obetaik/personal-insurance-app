import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';

function NewClaim() {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [formData, setFormData] = useState({
    policy_id: '',
    incident_date: '',
    description: '',
    claim_amount: ''
  });

  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetchUserPolicies();
    
    // Check if policyId was passed in URL
    const params = new URLSearchParams(location.search);
    const policyId = params.get('policyId');
    if (policyId) {
      setFormData(prev => ({ ...prev, policy_id: policyId }));
    }
  }, [location]);

  const fetchUserPolicies = async () => {
    try {
      setLoading(true);
      const response = await api.get('/policies');
      // Filter only active policies
      const activePolicies = response.data.filter(p => p.status === 'Active');
      setPolicies(activePolicies);
    } catch (error) {
      console.error('Error fetching policies:', error);
      setError('Failed to load your policies');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');

    // Validate form
    if (!formData.policy_id) {
      setError('Please select a policy');
      setSubmitting(false);
      return;
    }

    if (!formData.incident_date) {
      setError('Please enter the incident date');
      setSubmitting(false);
      return;
    }

    if (!formData.description.trim()) {
      setError('Please provide a description of the incident');
      setSubmitting(false);
      return;
    }

    if (!formData.claim_amount || parseFloat(formData.claim_amount) <= 0) {
      setError('Please enter a valid claim amount');
      setSubmitting(false);
      return;
    }

    try {
      const response = await api.post('/claims', {
        policy_id: parseInt(formData.policy_id),
        incident_date: new Date(formData.incident_date).toISOString(),
        description: formData.description,
        claim_amount: parseFloat(formData.claim_amount)
      });

      setSuccess('Claim filed successfully!');
      
      // Redirect to claim details after 2 seconds
      setTimeout(() => {
        navigate(`/claims/${response.data.id}`);
      }, 2000);

    } catch (error) {
      console.error('Error filing claim:', error);
      setError(error.response?.data?.error || 'Failed to file claim. Please try again.');
    } finally {
      setSubmitting(false);
    }
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
      <Row className="justify-content-center">
        <Col md={8}>
          <div className="page-header">
            <h2>File a New Claim</h2>
            <p className="text-muted">Please provide details about your incident</p>
          </div>

          {error && (
            <Alert variant="danger" className="mb-4">
              {error}
            </Alert>
          )}

          {success && (
            <Alert variant="success" className="mb-4">
              {success} Redirecting to claim details...
            </Alert>
          )}

          <Card>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Select Policy *</Form.Label>
                  <Form.Select
                    name="policy_id"
                    value={formData.policy_id}
                    onChange={handleInputChange}
                    required
                    disabled={policies.length === 0}
                  >
                    <option value="">Choose a policy...</option>
                    {policies.map(policy => (
                      <option key={policy.id} value={policy.id}>
                        {policy.policy_number} - {policy.product_name} (${policy.premium_amount}/year)
                      </option>
                    ))}
                  </Form.Select>
                  {policies.length === 0 && (
                    <Form.Text className="text-danger">
                      You don't have any active policies to file a claim against.
                    </Form.Text>
                  )}
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Incident Date *</Form.Label>
                  <Form.Control
                    type="date"
                    name="incident_date"
                    value={formData.incident_date}
                    onChange={handleInputChange}
                    max={new Date().toISOString().split('T')[0]}
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Claim Amount ($) *</Form.Label>
                  <Form.Control
                    type="number"
                    name="claim_amount"
                    value={formData.claim_amount}
                    onChange={handleInputChange}
                    placeholder="Enter claim amount"
                    min="1"
                    step="0.01"
                    required
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Description of Incident *</Form.Label>
                  <Form.Control
                    as="textarea"
                    name="description"
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder="Please describe what happened..."
                    rows={5}
                    required
                  />
                </Form.Group>

                <div className="d-grid gap-2">
                  <Button 
                    variant="primary" 
                    type="submit" 
                    size="lg"
                    disabled={submitting || policies.length === 0}
                  >
                    {submitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Filing Claim...
                      </>
                    ) : (
                      'File Claim'
                    )}
                  </Button>
                  <Button 
                    variant="outline-secondary" 
                    onClick={() => navigate('/claims')}
                  >
                    Cancel
                  </Button>
                </div>
              </Form>
            </Card.Body>
          </Card>

          <Card className="mt-4">
            <Card.Header>
              <h5 className="mb-0">Important Information</h5>
            </Card.Header>
            <Card.Body>
              <ul className="mb-0">
                <li className="mb-2">Claims must be filed within 30 days of the incident</li>
                <li className="mb-2">You'll need to provide supporting documentation</li>
                <li className="mb-2">Claim processing typically takes 5-7 business days</li>
                <li className="mb-2">You can track your claim status in the Claims section</li>
              </ul>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default NewClaim;
