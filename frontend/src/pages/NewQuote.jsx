import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Form, Button, Alert } from 'react-bootstrap';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../services/api';

function NewQuote() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [formData, setFormData] = useState({
    product_id: '',
    coverage_amount: 250000,
    deductible: 500,
    additional_options: {}
  });
  const [calculatedPrice, setCalculatedPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    fetchProducts();
    
    const params = new URLSearchParams(location.search);
    const productId = params.get('productId');
    if (productId) {
      setFormData(prev => ({ ...prev, product_id: productId }));
    }
  }, [location]);

  useEffect(() => {
    if (formData.product_id && products.length > 0) {
      const product = products.find(p => p.id === parseInt(formData.product_id));
      setSelectedProduct(product);
      calculatePremium();
    }
  }, [formData.product_id, formData.coverage_amount, formData.deductible, products]);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products');
      setProducts(response.data);
    } catch (error) {
      console.error('Error fetching products:', error);
      setError('Failed to load products');
    }
  };

  const calculatePremium = () => {
    if (!selectedProduct) return;
    
    const basePrice = selectedProduct.base_price;
    const coverageAmount = parseFloat(formData.coverage_amount);
    const deductible = parseFloat(formData.deductible);
    
    // Simple premium calculation
    const price = basePrice * (coverageAmount / 100000) * (1 - (deductible / 10000));
    setCalculatedPrice(Math.max(price, 100)); // Minimum premium $100
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
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/quotes', {
        product_id: parseInt(formData.product_id),
        coverage_amount: parseFloat(formData.coverage_amount),
        deductible: parseFloat(formData.deductible)
      });
      
      navigate(`/quotes/${response.data.id}`);
    } catch (error) {
      console.error('Error creating quote:', error);
      setError(error.response?.data?.error || 'Failed to create quote');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container>
      <Row className="justify-content-center">
        <Col md={8}>
          <h2 className="mb-4">Get a New Quote</h2>
          
          {error && (
            <Alert variant="danger" className="mb-4">
              {error}
            </Alert>
          )}
          
          <Card>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Select Product</Form.Label>
                  <Form.Select
                    name="product_id"
                    value={formData.product_id}
                    onChange={handleInputChange}
                    required
                  >
                    <option value="">Choose a product...</option>
                    {products.map(product => (
                      <option key={product.id} value={product.id}>
                        {product.name} - ${product.base_price}/year
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>

                {selectedProduct && (
                  <>
                    <Form.Group className="mb-3">
                      <Form.Label>Coverage Amount ($)</Form.Label>
                      <Form.Control
                        type="range"
                        name="coverage_amount"
                        min="100000"
                        max="1000000"
                        step="50000"
                        value={formData.coverage_amount}
                        onChange={handleInputChange}
                      />
                      <div className="d-flex justify-content-between">
                        <span>$100,000</span>
                        <span className="fw-bold">
                          ${parseInt(formData.coverage_amount).toLocaleString()}
                        </span>
                        <span>$1,000,000</span>
                      </div>
                    </Form.Group>

                    <Form.Group className="mb-3">
                      <Form.Label>Deductible ($)</Form.Label>
                      <Form.Control
                        type="range"
                        name="deductible"
                        min="0"
                        max="5000"
                        step="250"
                        value={formData.deductible}
                        onChange={handleInputChange}
                      />
                      <div className="d-flex justify-content-between">
                        <span>$0</span>
                        <span className="fw-bold">
                          ${parseInt(formData.deductible).toLocaleString()}
                        </span>
                        <span>$5,000</span>
                      </div>
                    </Form.Group>

                    <Card className="bg-light mb-4">
                      <Card.Body>
                        <Row>
                          <Col md={6}>
                            <p className="mb-1">Base Price:</p>
                            <p className="mb-1">Coverage Factor:</p>
                            <p className="mb-1">Deductible Discount:</p>
                            <hr />
                            <p className="fw-bold">Estimated Premium:</p>
                          </Col>
                          <Col md={6} className="text-end">
                            <p className="mb-1">${selectedProduct.base_price}/year</p>
                            <p className="mb-1">
                              {(formData.coverage_amount / 100000).toFixed(2)}x
                            </p>
                            <p className="mb-1">
                              {(formData.deductible / 10000 * 100).toFixed(0)}% off
                            </p>
                            <hr />
                            <p className="fw-bold text-primary">
                              ${calculatedPrice?.toFixed(2)}/year
                            </p>
                          </Col>
                        </Row>
                      </Card.Body>
                    </Card>

                    <div className="d-grid gap-2">
                      <Button 
                        variant="primary" 
                        type="submit" 
                        size="lg"
                        disabled={loading}
                      >
                        {loading ? 'Creating Quote...' : 'Get Quote'}
                      </Button>
                      <Button 
                        variant="outline-secondary" 
                        onClick={() => navigate('/products')}
                      >
                        Cancel
                      </Button>
                    </div>
                  </>
                )}
              </Form>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default NewQuote;
