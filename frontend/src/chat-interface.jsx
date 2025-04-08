import React, { useState, useEffect, useRef } from 'react';

function ChatInterface() {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null); // Ref for scrolling
    const textareaRef = useRef(null); // Ref for textarea

    // Function to scroll to bottom
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    // Adjust textarea height automatically
    const adjustTextareaHeight = () => {
        const textarea = textareaRef.current;
        if (textarea) {
            textarea.style.height = 'auto';
            textarea.style.height = `${Math.min(textarea.scrollHeight, 150)}px`;
        }
    };

    // Scroll to bottom whenever messages change
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSendMessage = async () => {
        if (inputValue.trim()) {
            const userMessage = { text: inputValue, sender: 'user' };
            setMessages(prevMessages => [...prevMessages, userMessage]);
            setInputValue('');
            setIsLoading(true);

            // Reset textarea height
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }

            try {
                // Make API call to backend
                const response = await fetch('http://localhost:8000/responses', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: userMessage.text }),
                });

                if (!response.ok) {
                    throw new Error(`API request failed with status ${response.status}`);
                }

                const data = await response.json();

                // Add bot response from the API
                const botMessage = {
                    text: data.result || "Sorry, I couldn't process your request.",
                    sender: 'bot'
                };

                setMessages(prevMessages => [...prevMessages, botMessage]);
            } catch (error) {
                console.error('Error sending message:', error);

                // Add error message in case of failure
                const errorMessage = {
                    text: "Sorry, there was an error processing your message. Please try again.",
                    sender: 'bot'
                };

                setMessages(prevMessages => [...prevMessages, errorMessage]);
            } finally {
                setIsLoading(false);
            }
        }
    };

    const handleInputChange = (event) => {
        setInputValue(event.target.value);
        adjustTextareaHeight();
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter' && !event.shiftKey) { // Send on Enter, allow Shift+Enter for newline
            event.preventDefault(); // Prevent default Enter behavior (newline)
            handleSendMessage();
        }
    };

    return (
        <div className="chat-interface">
            <div className="message-list">
                {messages.map((msg, index) => (
                    <div key={index} className={`message-container message-${msg.sender}`}>
                        {msg.sender === 'bot' && <div className="message-avatar bot-avatar">AI</div>}
                        <div className="message-bubble">
                            {msg.text}
                        </div>
                        {msg.sender === 'user' && <div className="message-avatar user-avatar">You</div>}
                    </div>
                ))}
                {isLoading && (
                    <div className="message-container message-bot">
                        <div className="message-avatar bot-avatar">AI</div>
                        <div className="message-bubble">
                            <div className="typing-indicator">
                                <span></span>
                                <span></span>
                                <span></span>
                            </div>
                        </div>
                    </div>
                )}
                {messages.length === 0 && !isLoading && (
                    <div className="welcome-message">
                        <h2>AltoGPT</h2>
                        <p>How can I help you today?</p>
                    </div>
                )}
                {/* Dummy div to help scroll to bottom */}
                <div ref={messagesEndRef} />
            </div>
            <div className="input-area">
                <textarea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyPress={handleKeyPress}
                    className="message-input"
                    placeholder="Message AltoGPT..."
                    rows="1" // Start with one row, auto-expand if needed
                    disabled={isLoading}
                />
                <button
                    onClick={handleSendMessage}
                    className="send-button"
                    disabled={!inputValue.trim() || isLoading}
                >
                    <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="send-icon">
                        <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </button>
            </div>
        </div>
    );
}

export default ChatInterface;
