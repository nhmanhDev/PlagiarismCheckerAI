import { useState } from 'react';
import { Card } from './common/Card';
import { Button } from './common/Button';
import type { CheckResponse } from '../types';

interface ChatPanelProps {
    queryText: string;
    detectionResults: CheckResponse | null;
}

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export function ChatPanel({ queryText, detectionResults }: ChatPanelProps) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const sendMessage = async (userQuestion?: string) => {
        if (!detectionResults) return;

        const question = userQuestion || input;
        if (!question.trim() && !userQuestion) return;

        // Add user message
        if (!userQuestion) {
            const userMsg: Message = { role: 'user', content: question };
            setMessages(prev => [...prev, userMsg]);
        }

        setInput('');
        setLoading(true);

        try {
            const response = await fetch('/api/v1/chat/explain', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    query_text: queryText,
                    detection_results: detectionResults.results,
                    user_question: userQuestion ? null : question
                })
            });

            const data = await response.json();

            // Add assistant message
            const assistantMsg: Message = {
                role: 'assistant',
                content: data.response
            };
            setMessages(prev => [...prev, assistantMsg]);

        } catch (error) {
            console.error('Chat error:', error);
            const errorMsg: Message = {
                role: 'assistant',
                content: '❌ Xin lỗi, đã có lỗi xảy ra. Vui lòng kiểm tra kết nối hoặc thử lại sau.'
            };
            setMessages(prev => [...prev, errorMsg]);
        } finally {
            setLoading(false);
        }
    };

    const explainResults = () => {
        sendMessage('auto-explain');
    };

    return (
        <Card title="💬 Trợ Lý AI - Giải Thích Kết Quả">
            <div className="flex flex-col h-[500px]">
                {/* Messages Area */}
                <div className="flex-1 overflow-y-auto space-y-3 mb-4 p-4 bg-gray-50 rounded-lg">
                    {messages.length === 0 ? (
                        <div className="text-center text-gray-500 mt-12">
                            <div className="text-4xl mb-3">🤖</div>
                            <p className="text-lg font-medium mb-2">Xin chào! Tôi là trợ lý AI</p>
                            <p className="text-sm mb-6">Tôi có thể giúp bạn hiểu rõ hơn về kết quả kiểm tra đạo văn</p>
                            {detectionResults && (
                                <Button onClick={explainResults} variant="primary" className="mx-auto">
                                    📊 Giải Thích Kết Quả Này
                                </Button>
                            )}
                        </div>
                    ) : (
                        <>
                            {messages.map((msg, idx) => (
                                <div
                                    key={idx}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div
                                        className={`max-w-[80%] px-4 py-3 rounded-lg ${msg.role === 'user'
                                                ? 'bg-blue-600 text-white'
                                                : 'bg-white border border-gray-200 shadow-sm'
                                            }`}
                                    >
                                        <p className="text-sm whitespace-pre-wrap leading-relaxed">
                                            {msg.content}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {loading && (
                                <div className="flex justify-start">
                                    <div className="bg-white border border-gray-200 px-4 py-3 rounded-lg shadow-sm">
                                        <div className="flex items-center space-x-2">
                                            <div className="flex space-x-1">
                                                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                                                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                                                <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                                            </div>
                                            <span className="text-sm text-gray-500">Đang suy nghĩ...</span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Quick Questions (show only when no messages) */}
                {detectionResults && messages.length === 0 && (
                    <div className="mb-3 px-2">
                        <p className="text-xs text-gray-500 mb-2">Câu hỏi gợi ý:</p>
                        <div className="flex flex-wrap gap-2">
                            <button
                                onClick={() => sendMessage('Tại sao hệ thống phát hiện đạo văn?')}
                                className="text-xs px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 hover:border-blue-400 rounded-full transition-colors"
                                disabled={loading}
                            >
                                🔍 Tại sao phát hiện?
                            </button>
                            <button
                                onClick={() => sendMessage('Các điểm số có nghĩa là gì?')}
                                className="text-xs px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 hover:border-blue-400 rounded-full transition-colors"
                                disabled={loading}
                            >
                                📊 Điểm số nghĩa là gì?
                            </button>
                            <button
                                onClick={() => sendMessage('Làm thế nào để cải thiện văn bản?')}
                                className="text-xs px-3 py-1.5 bg-white border border-gray-300 hover:bg-gray-50 hover:border-blue-400 rounded-full transition-colors"
                                disabled={loading}
                            >
                                💡 Cải thiện như thế nào?
                            </button>
                        </div>
                    </div>
                )}

                {/* Input Area */}
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyPress={(e) => {
                            if (e.key === 'Enter' && !loading && input.trim()) {
                                sendMessage();
                            }
                        }}
                        placeholder={detectionResults ? "Hỏi về kết quả kiểm tra..." : "Chưa có kết quả để hỏi"}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                        disabled={loading || !detectionResults}
                    />
                    <Button
                        onClick={() => sendMessage()}
                        disabled={loading || !input.trim() || !detectionResults}
                        className="px-6"
                    >
                        {loading ? '...' : 'Gửi'}
                    </Button>
                </div>
            </div>
        </Card>
    );
}
