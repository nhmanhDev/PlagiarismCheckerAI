import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { ChatPanel } from '../components/ChatPanel';
import { plagiarismService } from '../services/plagiarismService';
import type { CheckResponse } from '../types';

export default function CheckPage() {
    const [queryText, setQueryText] = useState('');
    const [alpha, setAlpha] = useState(0.4);
    const [useReranker, setUseReranker] = useState(true);
    const [useFileUpload, setUseFileUpload] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [results, setResults] = useState<CheckResponse | null>(null);

    const checkMutation = useMutation({
        mutationFn: async (data: { query_text?: string; file?: File }) => {
            if (data.file) {
                return plagiarismService.checkMultistageWithFile(data.file, alpha, useReranker);
            } else if (data.query_text) {
                if (useReranker) {
                    return plagiarismService.checkMultistage({
                        query_text: data.query_text,
                        alpha,
                        use_reranker: true,
                        top_n: 5,
                        threshold: 0.75,
                    });
                } else {
                    return plagiarismService.check({
                        query_text: data.query_text,
                        alpha,
                        top_k_lex: 10,
                        top_k_sem: 10,
                        top_n: 5,
                        threshold: 0.75,
                    });
                }
            }
            throw new Error("Either query_text or file must be provided");
        },
        onSuccess: (data) => {
            setResults(data);
        },
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        if (useFileUpload && selectedFile) {
            checkMutation.mutate({ file: selectedFile });
        } else if (!useFileUpload && queryText.trim()) {
            checkMutation.mutate({ query_text: queryText });
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-8">
                Kiểm Tra Đạo Văn
            </h1>

            <div className="grid lg:grid-cols-2 gap-8">
                {/* Input Section */}
                <div>
                    <Card title="Nhập Văn Bản Cần Kiểm Tra">
                        <form onSubmit={handleSubmit} className="space-y-4">
                            {/* Input mode toggle */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Phương thức nhập liệu
                                </label>
                                <div className="flex gap-4 mb-4">
                                    <label className="flex items-center">
                                        <input
                                            type="radio"
                                            name="checkInputMode"
                                            value="text"
                                            checked={!useFileUpload}
                                            onChange={() => setUseFileUpload(false)}
                                            className="mr-2"
                                        />
                                        Nhập văn bản
                                    </label>
                                    <label className="flex items-center">
                                        <input
                                            type="radio"
                                            name="checkInputMode"
                                            value="file"
                                            checked={useFileUpload}
                                            onChange={() => setUseFileUpload(true)}
                                            className="mr-2"
                                        />
                                        Upload file (PDF, TXT)
                                    </label>
                                </div>
                            </div>

                            {/* Conditional input */}
                            {!useFileUpload ? (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Văn Bản Cần Kiểm Tra
                                    </label>
                                    <textarea
                                        value={queryText}
                                        onChange={(e) => setQueryText(e.target.value)}
                                        className="w-full h-64 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        placeholder="Dán hoặc nhập văn bản bạn muốn kiểm tra đạo văn..."
                                        required={!useFileUpload}
                                    />
                                </div>
                            ) : (
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-2">
                                        Chọn File (PDF hoặc TXT)
                                    </label>
                                    <input
                                        type="file"
                                        accept=".pdf,.txt"
                                        onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                        required={useFileUpload}
                                    />
                                    {selectedFile && (
                                        <p className="mt-2 text-sm text-gray-600">
                                            File đã chọn: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
                                        </p>
                                    )}
                                </div>
                            )}

                            <div className="grid grid-cols-2 gap-4">
                                <Input
                                    type="number"
                                    label="Hệ số Alpha (trọng số BM25)"
                                    value={alpha}
                                    onChange={(e) => setAlpha(parseFloat(e.target.value))}
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    helperText="0 = Chỉ semantic, 1 = Chỉ BM25"
                                />

                                <div className="flex items-center pt-6">
                                    <input
                                        type="checkbox"
                                        id="useReranker"
                                        checked={useReranker}
                                        onChange={(e) => setUseReranker(e.target.checked)}
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                    <label htmlFor="useReranker" className="ml-2 text-sm text-gray-700">
                                        Sử dụng Re-ranker đa giai đoạn
                                    </label>
                                </div>
                            </div>

                            <Button
                                type="submit"
                                loading={checkMutation.isPending}
                                className="w-full"
                            >
                                {checkMutation.isPending ? 'Đang kiểm tra...' : 'Kiểm Tra Đạo Văn'}
                            </Button>
                        </form>
                    </Card>
                </div>

                {/* Results Section */}
                <div>
                    <Card title="Kết Quả">
                        {!results && !checkMutation.isPending && (
                            <div className="text-center py-12 text-gray-500">
                                <p>Chưa có kết quả. Nhập văn bản hoặc upload file và nhấn "Kiểm Tra Đạo Văn"</p>
                            </div>
                        )}

                        {checkMutation.isPending && (
                            <div className="text-center py-12">
                                <div className="animate-spin h-12 w-12 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
                                <p className="mt-4 text-gray-600">Đang phân tích văn bản...</p>
                            </div>
                        )}

                        {results && (
                            <div className="space-y-4">
                                {/* Summary */}
                                <div className="bg-gray-50 p-4 rounded-lg">
                                    <div className="grid grid-cols-2 gap-4 text-sm">
                                        <div>
                                            <span className="text-gray-600">Phương pháp:</span>
                                            <span className="ml-2 font-medium">{results.method}</span>
                                        </div>
                                        <div>
                                            <span className="text-gray-600">Tiếng Việt:</span>
                                            <span className="ml-2 font-medium">
                                                {results.vietnamese_detected ? 'Có' : 'Không'}
                                            </span>
                                        </div>
                                        <div>
                                            <span className="text-gray-600">Kết quả tìm thấy:</span>
                                            <span className="ml-2 font-medium">{results.results.length}</span>
                                        </div>
                                        <div>
                                            <span className="text-gray-600">Ngưỡng:</span>
                                            <span className="ml-2 font-medium">{results.threshold}</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Matches */}
                                <div className="space-y-3">
                                    <h3 className="font-semibold">Các Đoạn Trùng Khớp:</h3>
                                    {results.results.map((result, idx) => (
                                        <div
                                            key={idx}
                                            className={`p-4 rounded-lg border-2 ${result.is_suspected
                                                ? 'bg-red-50 border-red-200'
                                                : 'bg-green-50 border-green-200'
                                                }`}
                                        >
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="text-sm font-medium text-gray-700">
                                                    Kết quả #{idx + 1}
                                                </span>
                                                <span
                                                    className={`px-2 py-1 rounded text-xs font-bold ${result.is_suspected
                                                        ? 'bg-red-600 text-white'
                                                        : 'bg-green-600 text-white'
                                                        }`}
                                                >
                                                    {(result.score_final * 100).toFixed(1)}%
                                                </span>
                                            </div>
                                            <p className="text-sm text-gray-800 italic">
                                                "{result.text.substring(0, 200)}
                                                {result.text.length > 200 ? '...' : ''}"
                                            </p>
                                        </div>
                                    ))}

                                    {results.results.length === 0 && (
                                        <div className="text-center py-8 text-gray-500">
                                            <p className="text-lg">Không phát hiện đạo văn</p>
                                            <p className="text-sm mt-2">Văn bản này có vẻ là tác phẩm gốc</p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        )}

                        {checkMutation.isError && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                <p className="text-red-800">
                                    Lỗi khi kiểm tra văn bản. Hãy chắc chắn đã kích hoạt một kho tài liệu.
                                </p>
                            </div>
                        )}
                    </Card>
                </div>
            </div>

            {/* AI Chat Panel - Full Width Below Results */}
            {results && (
                <div className="mt-8">
                    <ChatPanel
                        queryText={useFileUpload && selectedFile ? selectedFile.name : queryText}
                        detectionResults={results}
                    />
                </div>
            )}
        </div>
    );
}
