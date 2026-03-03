import React, { useState, useEffect } from 'react';
import { Container, Table, Button, Badge, Card, Row, Col } from 'react-bootstrap';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';

function Claims() {
  const [claims, setClaims] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchClaims();
  }, []);

  const fetchClaims = async () => {
    try {
      setLoading(true);
      const response = await api.get('/claims');
      setClaims(response.data);
      setError('');
    } catch (error) {
      console.error('Error fetching claims:', error);
      setError('Failed to load claims');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const variants = {
      'Submitted': 'info',
      'Under Review': 'warning',
      'Approved': 'success',
      'Rejected': 'danger',
      'Pending': 'warning',
      'In Progress': 'primary'
    };
    
    const bgColor = variants[status] || 'secondary';
    
    return (
      <Badge bg={bgColor} className="status-badge">
        {status}
      </Badge>
    );
  };

  const getStatusIcon = (status) => {
    const icons = {
      'Submitted': 'bi-clock-history',
      'Under Review': 'bi-search',
      'Approved': 'bi-check-circle',
      'Rejected': 'bi-x-circle',
      'Pending': 'bi-hourglass-split',
      'In Progress': 'bi-arrow-repeat'
    };
    
    return icons[status] || 'bi-question-circle';
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const formatCurrency = (amount) => {
    if (!amount) return '$0';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const getSummaryStats = () => {
    const total = claims.length;
    const submitted = claims.filter(c => c.status === 'Submitted').length;
    const approved = claims.filter(c => c.status === 'Approved').length;
    const rejected = claims.filter(c => c.status === 'Rejected').length;
    const underReview = claims.filter(c => c.status === 'Under Review').length;
    
    return { total, submitted, approved, rejected, underReview };
  };

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
        <p className="mt-3 text-muted">Loading your claims...</p>
      </Container>
    );
  }

  const stats = getSummaryStats();

  return (
    <Container>
      {/* Header */}
      <div className="page-header d-flex justify-content-between align-items-center">
        <div>
          <h2>My Claims</h2>
          <p className="text-muted">Track and manage your insurance claims</p>
        </div>
        <Button 
          variant="primary" 
          onClick={() => navigate('/claims/new')}
          size="lg"
        >
          <i className="bi bi-plus-circle me-2"></i>
          File New Claim
        </Button>
      </div>

      {error && (
        <Alert variant="danger" className="mb-4">
          <i className="bi bi-exclamation-triangle me-2"></i>
          {error}
        </Alert>
      )}

      {/* Stats Cards */}
      {claims.length > 0 && (
        <Row className="mb-4">
          <Col md={3}>
            <Card className="stat-card">
              <div className="stat-icon bg-primary bg-opacity-10">
                <i className="bi bi-file-text text-primary"></i>
              </div>
              <div className="stat-info">
                <h3>{stats.total}</h3>
                <p className="text-muted">Total Claims</p>
              </div>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <div className="stat-icon bg-warning bg-opacity-10">
                <i className="bi bi-clock-history text-warning"></i>
              </div>
              <div className="stat-info">
                <h3>{stats.submitted + stats.underReview}</h3>
                <p className="text-muted">In Progress</p>
              </div>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <div className="stat-icon bg-success bg-opacity-10">
                <i className="bi bi-check-circle text-success"></i>
              </div>
              <div className="stat-info">
                <h3>{stats.approved}</h3>
                <p className="text-muted">Approved</p>
              </div>
            </Card>
          </Col>
          <Col md={3}>
            <Card className="stat-card">
              <div className="stat-icon bg-info bg-opacity-10">
                <i className="bi bi-currency-dollar text-info"></i>
              </div>
              <div className="stat-info">
                <h3>
                  {formatCurrency(
                    claims
                      .filter(c => c.status === 'Approved')
                      .reduce((sum, c) => sum + (c.approved_amount || c.claim_amount || 0), 0)
                  )}
                </h3>
                <p className="text-muted">Total Payout</p>
              </div>
            </Card>
          </Col>
        </Row>
      )}

      {/* Claims List */}
      {claims.length === 0 ? (
        <Card className="text-center p-5">
          <Card.Body>
            <div className="mb-4">
              <i className="bi bi-file-text" style={{ fontSize: '4rem', color: '#dee2e6' }}></i>
            </div>
            <h4>No Claims Yet</h4>
            <p className="text-muted mb-4">
              You haven't filed any claims. If you need to file a claim, click the button below.
            </p>
            <Button 
              variant="primary" 
              onClick={() => navigate('/claims/new')}
              size="lg"
            >
              <i className="bi bi-plus-circle me-2"></i>
              File Your First Claim
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <Card>
          <Card.Body className="p-0">
            <div className="table-container">
              <Table hover responsive className="mb-0">
                <thead>
                  <tr>
                    <th>Claim #</th>
                    <th>Policy #</th>
                    <th>Incident Date</th>
                    <th>Filed Date</th>
                    <th>Claim Amount</th>
                    <th>Status</th>
                    <th>Documents</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {claims.map(claim => (
                    <tr key={claim.id}>
                      <td>
                        <Link to={`/claims/${claim.id}`} className="fw-bold">
                          {claim.claim_number}
                        </Link>
                      </td>
                      <td>
                        <Link to={`/policies/${claim.policy?.id}`} className="text-decoration-none">
                          <small>{claim.policy_number}</small>
                        </Link>
                      </td>
                      <td>{formatDate(claim.incident_date)}</td>
                      <td>{formatDate(claim.filing_date)}</td>
                      <td>
                        <strong className="text-primary">
                          {formatCurrency(claim.claim_amount)}
                        </strong>
                      </td>
                      <td>
                        <div className="d-flex align-items-center">
                          <i className={`bi ${getStatusIcon(claim.status)} me-2`}></i>
                          {getStatusBadge(claim.status)}
                        </div>
                      </td>
                      <td className="text-center">
                        {claim.documents && claim.documents.length > 0 ? (
                          <Badge bg="success" className="rounded-pill">
                            <i className="bi bi-check-circle me-1"></i>
                            {claim.documents.length}
                          </Badge>
                        ) : (
                          <Badge bg="secondary" className="rounded-pill">
                            <i className="bi bi-x-circle me-1"></i>
                            0
                          </Badge>
                        )}
                      </td>
                      <td>
                        <Button
                          as={Link}
                          to={`/claims/${claim.id}`}
                          variant="outline-primary"
                          size="sm"
                          className="me-2"
                        >
                          <i className="bi bi-eye me-1"></i>
                          View
                        </Button>
                        {claim.status === 'Submitted' && (
                          <Button
                            as={Link}
                            to={`/claims/${claim.id}/documents`}
                            variant="outline-success"
                            size="sm"
                          >
                            <i className="bi bi-upload me-1"></i>
                            Upload
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            </div>
          </Card.Body>
        </Card>
      )}

      {/* Help Section */}
      {claims.length > 0 && (
        <Row className="mt-4">
          <Col md={12}>
            <Card className="bg-light">
              <Card.Body>
                <Row className="align-items-center">
                  <Col md={8}>
                    <h5 className="mb-2">Need help with your claim?</h5>
                    <p className="text-muted mb-md-0">
                      Contact our claims department for assistance with the claims process.
                    </p>
                  </Col>
                  <Col md={4} className="text-md-end">
                    <Button variant="outline-primary">
                      <i className="bi bi-headset me-2"></i>
                      Contact Support
                    </Button>
                  </Col>
                </Row>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}

      {/* Quick Tips */}
      {claims.length > 0 && (
        <Row className="mt-4">
          <Col md={4}>
            <Card className="h-100">
              <Card.Body>
                <div className="d-flex align-items-center mb-3">
                  <div className="bg-primary bg-opacity-10 p-3 rounded-circle me-3">
                    <i className="bi bi-clock-history text-primary"></i>
                  </div>
                  <h6 className="mb-0">Processing Time</h6>
                </div>
                <p className="text-muted small mb-0">
                  Most claims are processed within 5-7 business days after all documents are received.
                </p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="h-100">
              <Card.Body>
                <div className="d-flex align-items-center mb-3">
                  <div className="bg-success bg-opacity-10 p-3 rounded-circle me-3">
                    <i className="bi bi-file-earmark-text text-success"></i>
                  </div>
                  <h6 className="mb-0">Documentation</h6>
                </div>
                <p className="text-muted small mb-0">
                  Upload all relevant documents (photos, receipts, police reports) to speed up processing.
                </p>
              </Card.Body>
            </Card>
          </Col>
          <Col md={4}>
            <Card className="h-100">
              <Card.Body>
                <div className="d-flex align-items-center mb-3">
                  <div className="bg-warning bg-opacity-10 p-3 rounded-circle me-3">
                    <i className="bi bi-telephone text-warning"></i>
                  </div>
                  <h6 className="mb-0">Need Updates?</h6>
                </div>
                <p className="text-muted small mb-0">
                  Check claim status here or call our claims hotline at 1-800-555-CLAIM.
                </p>
              </Card.Body>
            </Card>
          </Col>
        </Row>
      )}
    </Container>
  );
}

export default Claims;
