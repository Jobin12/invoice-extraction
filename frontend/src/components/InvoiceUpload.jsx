import { useState } from 'react';
import InvoiceDataDisplay from './InvoiceDataDisplay';

const InvoiceUpload = () => {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first.");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/extract', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                let errorMessage = response.statusText;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch (e) {
                    // content is not json
                }
                throw new Error(`Upload failed: ${errorMessage}`);
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card">
            <h1>Invoice Extraction</h1>
            <p className="subtitle">Extraction powered by Gemini 2.5 Pro</p>
            <div className="upload-section">
                <div className="upload-area">
                    <input
                        type="file"
                        accept=".pdf"
                        onChange={handleFileChange}
                        className="file-input"
                    />
                    <p className="text-secondary">
                        {file ?
                            `Selected: ${file.name}` :
                            "Drag & Drop your invoice PDF here or click to browse"
                        }
                    </p>
                </div>

                <button onClick={handleUpload} disabled={loading || !file}>
                    {loading ? 'Extracting...' : 'Extract Data'}
                </button>
            </div>

            {loading && <div className="spinner"></div>}

            {error && (
                <div className="status-box" style={{ borderColor: 'var(--error)', color: '#fca5a5' }}>
                    <strong>Error:</strong> {error}
                </div>
            )}

            {result && (
                <InvoiceDataDisplay data={result.raw_response} />
            )}
        </div>
    );
};

export default InvoiceUpload;
