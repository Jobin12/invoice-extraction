import React from 'react';

const InvoiceDataDisplay = ({ data }) => {
    if (!data) return null;

    // Generalized Key formatter
    const formatKey = (key) => key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());

    const renderValue = (val) => {
        if (typeof val === 'object' && val !== null) {
            return (
                <ul className="value-list">
                    {Object.entries(val).map(([k, v]) => (
                        <li key={k}><strong>{formatKey(k)}:</strong> {v}</li>
                    ))}
                </ul>
            );
        }
        return val;
    };

    return (
        <div className="invoice-display fade-in">
            {/* Header Section */}
            <div className="invoice-header">
                <div className="invoice-title">
                    <h2>Invoice {data.invoice_number || 'N/A'}</h2>
                    <span className="invoice-date">{data.invoice_date || 'Date N/A'}</span>
                </div>
                <div className="invoice-meta">
                    {data.due_date && <p><strong>Due:</strong> {data.due_date}</p>}
                </div>
            </div>

            {/* Entities Section */}
            <div className="entities-grid">
                {data.seller && (
                    <div className="entity-card seller">
                        <h3><span className="icon">🏢</span> Seller Details</h3>
                        <div className="entity-content">
                            {data.seller.name_english && <p className="entity-name">{data.seller.name_english}</p>}
                            {data.seller.name_arabic && <p className="entity-name-ar">{data.seller.name_arabic}</p>}
                            {data.seller.address && <p>📍 {data.seller.address}</p>}
                            {data.seller.vat_number && <p>🆔 <strong>VAT:</strong> {data.seller.vat_number}</p>}
                            {data.seller.cr_number && <p>📋 <strong>CR:</strong> {data.seller.cr_number}</p>}
                        </div>
                    </div>
                )}

                {data.buyer && (
                    <div className="entity-card buyer">
                        <h3><span className="icon">👤</span> Buyer Details</h3>
                        <div className="entity-content">
                            {data.buyer.name && <p className="entity-name">{data.buyer.name}</p>}
                            {data.buyer.address && <p>📍 {data.buyer.address}</p>}
                            {data.buyer.vat_number && <p>🆔 <strong>VAT:</strong> {data.buyer.vat_number}</p>}
                        </div>
                    </div>
                )}
            </div>

            {/* Line Items Table */}
            {data.line_items && data.line_items.length > 0 && (
                <div className="table-container">
                    <table className="invoice-table">
                        <thead>
                            <tr>
                                <th>Item Description</th>
                                <th>Qty</th>
                                <th>Unit Price</th>
                                <th>Amount</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.line_items.map((item, index) => (
                                <tr key={index}>
                                    <td>{item.description}</td>
                                    <td>{item.quantity}</td>
                                    <td>{item.unit_price}</td>
                                    <td style={{ fontWeight: 700 }}>{item.total}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Totals Section */}
            {data.totals && (
                <div className="totals-section">
                    {Object.entries(data.totals).map(([key, value]) => (
                        <div key={key} className={`total-row ${key === 'grand_total' ? 'grand-total' : ''}`}>
                            <span className="total-label">{formatKey(key)}</span>
                            <span className="total-value">{value}</span>
                        </div>
                    ))}
                </div>
            )}

            {/* Bank Details (Footer) */}
            {data.bank_details && (
                <div className="bank-details">
                    <h3>🏦 Payment Information</h3>
                    <div className="bank-grid">
                        {Object.entries(data.bank_details).map(([key, value]) => (
                            <div key={key}>
                                <span className="label-sm">{formatKey(key)}</span>
                                <span className="value-sm">{value}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Zoho Integration Section */}
            <ZohoIntegration data={data} />
        </div>
    );
};

const ZohoIntegration = ({ data }) => {
    const [customerName, setCustomerName] = React.useState('');
    const [status, setStatus] = React.useState('idle'); // idle, loading, success, error
    const [message, setMessage] = React.useState('');

    const handleCreateInvoice = async () => {
        if (!customerName.trim()) {
            setStatus('error');
            setMessage('Please enter a customer name.');
            return;
        }

        setStatus('loading');
        setMessage('Creating invoice in Zoho Books...');

        try {
            const response = await fetch('http://localhost:8000/zoho/create-invoice', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    customer_name: customerName,
                    invoice_data: data
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.detail || 'Failed to create invoice');
            }

            setStatus('success');
            setMessage(`Invoice created successfully! ID: ${result.invoice.invoice_id}`);
        } catch (error) {
            setStatus('error');
            setMessage(error.message);
        }
    };

    return (
        <div className="zoho-integration-card" style={{ marginTop: '20px', padding: '20px', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <h3 style={{ marginTop: 0, marginBottom: '15px' }}>🚀 Zoho Books Integration</h3>

            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <input
                    type="text"
                    placeholder="Enter Zoho Customer Name"
                    value={customerName}
                    onChange={(e) => setCustomerName(e.target.value)}
                    style={{
                        flex: 1,
                        padding: '10px',
                        borderRadius: '6px',
                        border: '1px solid rgba(255,255,255,0.2)',
                        background: 'rgba(0,0,0,0.2)',
                        color: 'white'
                    }}
                />
                <button
                    onClick={handleCreateInvoice}
                    disabled={status === 'loading'}
                    style={{
                        padding: '10px 20px',
                        borderRadius: '6px',
                        border: 'none',
                        background: 'linear-gradient(135deg, #00C6FF 0%, #0072FF 100%)',
                        color: 'white',
                        fontWeight: 'bold',
                        cursor: status === 'loading' ? 'not-allowed' : 'pointer',
                        opacity: status === 'loading' ? 0.7 : 1
                    }}
                >
                    {status === 'loading' ? 'Creating...' : 'Create Invoice'}
                </button>
            </div>

            {message && (
                <div style={{
                    marginTop: '15px',
                    padding: '10px',
                    borderRadius: '6px',
                    background: status === 'error' ? 'rgba(255, 0, 0, 0.1)' : 'rgba(0, 255, 0, 0.1)',
                    border: `1px solid ${status === 'error' ? 'rgba(255, 0, 0, 0.3)' : 'rgba(0, 255, 0, 0.3)'}`,
                    color: status === 'error' ? '#ff6b6b' : '#51cf66',
                    fontSize: '0.9em'
                }}>
                    {status === 'error' ? '❌' : '✅'} {message}
                </div>
            )}
        </div>
    );
};

export default InvoiceDataDisplay;
