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

        </div>
    );
};

export default InvoiceDataDisplay;
