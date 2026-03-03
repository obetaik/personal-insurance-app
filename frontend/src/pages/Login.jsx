import React, { useEffect } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

function Login() {
  const { loginWithRedirect, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  return (
    <Container>
      <Row className="justify-content-center mt-5">
        <Col md={6}>
          <Card className="shadow">
            <Card.Body className="p-5">
              <div className="text-center mb-4">
                <h2 className="mb-3">Welcome Back!</h2>
                <p className="text-muted">
                  Sign in to access your quotes, policies, and manage your account.
                </p>
              </div>

              <div className="d-grid gap-3">
                <Button 
                  variant="primary" 
                  size="lg" 
                  onClick={() => loginWithRedirect()}
                >
                  <i className="bi bi-box-arrow-in-right me-2"></i>
                  Login with Auth0
                </Button>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Login;