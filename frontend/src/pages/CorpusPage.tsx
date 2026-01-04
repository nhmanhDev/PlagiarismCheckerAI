import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { corpusService } from '../services/corpusService';

export default function CorpusPage() {
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [corpusName, setCorpusName] = useState('');
    const [corpusText, setCorpusText] = useState('');
    const [useFileUpload, setUseFileUpload] = useState(false);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const queryClient = useQueryClient();

    const { data: corpora, isLoading } = useQuery({
        queryKey: ['corpora'],
        queryFn: corpusService.list,
    });

    const createMutation = useMutation({
        mutationFn: async (data: { name: string; corpus_text?: string; file?: File }) => {
            if (data.file) {
                return corpusService.createFromFile(data.name, data.file);
            } else if (data.corpus_text) {
                return corpusService.createFromText({ name: data.name, corpus_text: data.corpus_text });
            }
            throw new Error("Either corpus_text or file must be provided");
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['corpora'] });
            // Delay closing to show success message
            setTimeout(() => {
                setShowCreateForm(false);
                setCorpusName('');
                setCorpusText('');
                setSelectedFile(null);
                setUseFileUpload(false);
            }, 2000);
        },
        onError: (error: any) => {
            console.error('Create error:', error);
        }
    });

    const deleteMutation = useMutation({
        mutationFn: corpusService.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['corpora'] });
        },
    });

    const activateMutation = useMutation({
        mutationFn: corpusService.activate,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['corpora'] });
        },
    });

    const handleCreate = (e: React.FormEvent) => {
        e.preventDefault();

        if (useFileUpload && selectedFile) {
            // File upload mode
            createMutation.mutate({
                name: corpusName,
                file: selectedFile
            });
        } else if (!useFileUpload && corpusText) {
            // Text input mode
            createMutation.mutate({
                name: corpusName,
                corpus_text: corpusText
            });
        }
    };

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Quản Lý Kho Tài Liệu</h1>
                <Button onClick={() => setShowCreateForm(!showCreateForm)}>
                    {showCreateForm ? 'Hủy' : '+ Tạo Kho Mới'}
                </Button>
            </div>

            {/* Create Form */}
            {showCreateForm && (
                <Card title="Tạo Kho Tài Liệu Mới" className="mb-8">
                    <form onSubmit={handleCreate} className="space-y-4">
                        <Input
                            label="Tên Kho Tài Liệu"
                            value={corpusName}
                            onChange={(e) => setCorpusName(e.target.value)}
                            placeholder="VD: Bài Báo Nghiên Cứu 2024"
                            required
                        />

                        {/* Toggle between text and file upload */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Phương thức nhập liệu
                            </label>
                            <div className="flex gap-4 mb-4">
                                <label className="flex items-center">
                                    <input
                                        type="radio"
                                        name="inputMode"
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
                                        name="inputMode"
                                        value="file"
                                        checked={useFileUpload}
                                        onChange={() => setUseFileUpload(true)}
                                        className="mr-2"
                                    />
                                    Upload file (PDF, TXT)
                                </label>
                            </div>
                        </div>

                        {!useFileUpload ? (
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">
                                    Nội Dung Kho Tài Liệu
                                </label>
                                <textarea
                                    value={corpusText}
                                    onChange={(e) => setCorpusText(e.target.value)}
                                    className="w-full h-48 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    placeholder="Dán các tài liệu tham khảo của bạn vào đây..."
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

                        <Button type="submit" loading={createMutation.isPending} disabled={createMutation.isPending}>
                            {createMutation.isPending ? 'Đang tạo...' : 'Tạo Kho Tài Liệu'}
                        </Button>

                        {createMutation.isError && (
                            <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                                <p className="text-red-800 text-sm">
                                    Lỗi: {(createMutation.error as any)?.response?.data?.detail || (createMutation.error as any)?.message || 'Không thể tạo kho tài liệu'}
                                </p>
                            </div>
                        )}

                        {createMutation.isSuccess && (
                            <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
                                <p className="text-green-800 text-sm">
                                    ✓ Đã tạo kho tài liệu thành công!
                                </p>
                            </div>
                        )}
                    </form>
                </Card>
            )}

            {/* Corpus List */}
            <Card title="Các Kho Tài Liệu Của Bạn">
                {isLoading && (
                    <div className="text-center py-8">
                        <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto"></div>
                    </div>
                )}

                {corpora && corpora.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        <p>Chưa có kho tài liệu nào. Tạo kho mới để bắt đầu!</p>
                    </div>
                )}

                {corpora && corpora.length > 0 && (
                    <div className="space-y-4">
                        {corpora.map((corpus) => (
                            <div
                                key={corpus.id}
                                className={`p-4 rounded-lg border-2 ${corpus.is_active
                                    ? 'bg-blue-50 border-blue-600'
                                    : 'bg-white border-gray-200'
                                    }`}
                            >
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="font-semibold text-lg">{corpus.name}</h3>
                                        <p className="text-sm text-gray-600 mt-1">
                                            {corpus.segment_count} đoạn văn • Tạo ngày{' '}
                                            {new Date(corpus.created_at).toLocaleDateString('vi-VN')}
                                        </p>
                                        {corpus.is_active && (
                                            <span className="inline-block mt-2 px-2 py-1 bg-blue-600 text-white text-xs rounded">
                                                Đang Kích Hoạt
                                            </span>
                                        )}
                                    </div>

                                    <div className="flex gap-2">
                                        {!corpus.is_active && (
                                            <Button
                                                variant="secondary"
                                                size="sm"
                                                onClick={() => activateMutation.mutate(corpus.id)}
                                                loading={activateMutation.isPending}
                                            >
                                                Kích Hoạt
                                            </Button>
                                        )}
                                        <Button
                                            variant="danger"
                                            size="sm"
                                            onClick={() => {
                                                if (confirm('Xóa kho tài liệu này?')) {
                                                    deleteMutation.mutate(corpus.id);
                                                }
                                            }}
                                            loading={deleteMutation.isPending}
                                        >
                                            Xóa
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </Card>
        </div>
    );
}
