import { Link } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Button } from '../components/common/Button';

export default function HomePage() {
    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            {/* Hero Section */}
            <div className="text-center mb-16">
                <h1 className="text-5xl font-bold text-gray-900 mb-4">
                    Hệ Thống Kiểm Tra Đạo Văn AI
                </h1>
                <p className="text-xl text-gray-600 mb-8">
                    Công nghệ truy xuất thông tin đa giai đoạn cho văn bản tiếng Việt
                </p>
                <div className="flex gap-4 justify-center">
                    <Link to="/check">
                        <Button size="lg">
                            Bắt Đầu Kiểm Tra
                        </Button>
                    </Link>
                    <Link to="/corpus">
                        <Button variant="secondary" size="lg">
                            Quản Lý Kho Tài Liệu
                        </Button>
                    </Link>
                </div>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-8 mb-16">
                <Card title="Xử Lý Tiếng Việt">
                    <p className="text-gray-600">
                        Công nghệ NLP tiên tiến với tách từ, chuẩn hóa thanh điệu, và loại bỏ từ dừng cho tiếng Việt.
                    </p>
                </Card>

                <Card title="Truy Xuất Đa Giai Đoạn">
                    <p className="text-gray-600">
                        Kết hợp BM25 (từ vựng) + Semantic embeddings + Cross-encoder re-ranking để đạt độ chính xác cao nhất.
                    </p>
                </Card>

                <Card title="Hiệu Năng Cao">
                    <p className="text-gray-600">
                        Thời gian phản hồi nhanh (&lt;200ms) với độ chính xác 85-90% F1-score trên bộ dữ liệu chuẩn tiếng Việt.
                    </p>
                </Card>
            </div>

            {/* How it Works */}
            <Card title="Cách Thức Hoạt Động">
                <div className="space-y-6">
                    <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                            1
                        </div>
                        <div>
                            <h3 className="font-semibold text-lg mb-2">Tạo Kho Tài Liệu Tham Khảo</h3>
                            <p className="text-gray-600">
                                Thêm các tài liệu tham chiếu (PDF, DOCX, TXT) để tạo kho dữ liệu so sánh.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                            2
                        </div>
                        <div>
                            <h3 className="font-semibold text-lg mb-2">Nộp Văn Bản Cần Kiểm Tra</h3>
                            <p className="text-gray-600">
                                Nhập hoặc tải lên văn bản bạn muốn kiểm tra đạo văn.
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start gap-4">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold">
                            3
                        </div>
                        <div>
                            <h3 className="font-semibold text-lg mb-2">Nhận Kết Quả Chi Tiết</h3>
                            <p className="text-gray-600">
                                Xem điểm tương đồng, các đoạn văn trùng khớp và chỉ số nghi ngờ đạo văn.
                            </p>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Stats */}
            <div className="grid md:grid-cols-4 gap-6 mt-12">
                <div className="text-center">
                    <div className="text-4xl font-bold text-blue-600 mb-2">88%</div>
                    <div className="text-gray-600">Độ Chính Xác</div>
                </div>
                <div className="text-center">
                    <div className="text-4xl font-bold text-blue-600 mb-2">&lt;200ms</div>
                    <div className="text-gray-600">Thời Gian Phản Hồi</div>
                </div>
                <div className="text-center">
                    <div className="text-4xl font-bold text-blue-600 mb-2">3</div>
                    <div className="text-gray-600">Giai Đoạn Truy Xuất</div>
                </div>
                <div className="text-center">
                    <div className="text-4xl font-bold text-blue-600 mb-2">100%</div>
                    <div className="text-gray-600">Hỗ Trợ Tiếng Việt</div>
                </div>
            </div>
        </div>
    );
}
