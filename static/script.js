/**
 * SenoritaAssistant/static/script.js
 * FINAL CLEAN VERSION: Stable Button-Activated Voice Mode.
 */

document.addEventListener('DOMContentLoaded', () => {
    const chatLog = document.getElementById('chat-log');
    const commandInput = document.getElementById('command-input');
    const sendButton = document.getElementById('send-button');
    const stopButton = document.getElementById('stop-speaking-button');

    let globalUtterance = null;
    let femaleVoice = null;
    let initialGreetingSpoken = false;
    
    // Voice Recognition Variables
    let recognition = null;
    let isListening = false; // Simple state: listening or not
    let voiceCommandButton = null;
    let commandTimeoutId = null;

    // --- CONFIGURATION ---
    const SPEECH_LANGUAGE = 'en-US'; 
    const MAX_COMMAND_DURATION = 5000;
    // ------------------------------------

    // --- Voice Recognition Initialization ---
    function initializeVoiceRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            console.log('Speech recognition not supported in this browser');
            return false;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        
        recognition.continuous = false; // One command per click
        recognition.interimResults = false;
        recognition.lang = SPEECH_LANGUAGE;
        
        recognition.onstart = function() {
            isListening = true;
            updateVoiceButtonState();
            console.log('Voice recognition started. Ready for command.');
            
            // Set timeout to automatically stop if user is silent
            commandTimeoutId = setTimeout(() => {
                if (isListening) {
                    recognition.stop();
                    speakText("Sorry, I didn't catch that.");
                }
            }, MAX_COMMAND_DURATION);
        };
        
        recognition.onresult = function(event) {
            clearTimeout(commandTimeoutId);
            const transcript = event.results[event.results.length - 1][0].transcript.trim();
            
            if (transcript) {
                console.log('Voice command received:', transcript);
                recognition.stop(); 
                commandInput.value = transcript;
                sendCommand();
            }
        };
        
        recognition.onerror = function(event) {
            clearTimeout(commandTimeoutId);
            console.error('Voice recognition error:', event.error);
            isListening = false;
            updateVoiceButtonState();
            
            if (event.error !== 'no-speech') {
                speakText("I experienced an issue with the microphone.");
            }
        };
        
        recognition.onend = function() {
            clearTimeout(commandTimeoutId);
            isListening = false;
            updateVoiceButtonState();
            console.log('Voice recognition ended.');
        };
        
        return true;
    }
    
    function updateVoiceButtonState() {
        if (voiceCommandButton) {
            if (isListening) {
                voiceCommandButton.style.backgroundColor = '#ff4444';
                voiceCommandButton.textContent = '🎤 Listening...';
                voiceCommandButton.title = 'Click to stop listening';
            } else {
                voiceCommandButton.style.backgroundColor = '#4CAF50';
                voiceCommandButton.textContent = '🎤 Voice';
                voiceCommandButton.title = 'Click to start voice command';
            }
        }
    }
    
    function startCommandRecognition() {
        if (!recognition) { 
            if (!initializeVoiceRecognition()) return; 
        }
        
        if (isListening) {
            // If already listening, stop the current session
            recognition.stop(); 
        } else {
            // Start a new session
            try {
                recognition.start();
            } catch (e) {
                console.warn("Recognition start failed, possibly already running.", e);
            }
        }
    }


    function toggleVoiceRecognition() {
        // Direct call to the start/stop logic
        startCommandRecognition();
    }

    // --- Voice Initialization Function ---
    function initializeVoices() {
        if (initialGreetingSpoken) return;

        const voices = window.speechSynthesis.getVoices();

        if (voices.length === 0) {
            if (window.speechSynthesis.onvoiceschanged !== initializeVoices) {
                window.speechSynthesis.onvoiceschanged = initializeVoices;
            }
            return;
        }

        const englishVoices = voices.filter(voice => voice.lang.startsWith('en'));
        const maleVoiceNames = ['david', 'aaron', 'paul', 'mike', 'zack', 'daniel'];

        femaleVoice = englishVoices.find(voice =>
            voice.name.toLowerCase().includes('female') ||
            voice.name.toLowerCase().includes('zira') ||
            voice.name.toLowerCase().includes('samantha') ||
            voice.name.toLowerCase().includes('ava')
        );

        if (!femaleVoice) {
            femaleVoice = englishVoices.find(voice =>
                !voice.name.toLowerCase().includes('male') &&
                !maleVoiceNames.some(name => voice.name.toLowerCase().includes(name))
            );
        }

        if (!femaleVoice) {
            femaleVoice = englishVoices[0] || voices[0];
        }

        if (femaleVoice && !initialGreetingSpoken) {
            initialGreeting();
            initialGreetingSpoken = true;
        }
    }

    function initialGreeting() {
        const text = "Hello! I'm Senorita Assistant. How can I help you? Click the Voice button to speak your command."; 
        addMessage(text, 'assistant');
        speakText(text);
    }

    initializeVoices();


    // --- Media Cleanup Function (Unchanged) ---
    function removeVideoPlayer() {
        const mediaContainer = document.getElementById('video-player-container');
        if (mediaContainer) {
            mediaContainer.innerHTML = '';
            mediaContainer.style.display = 'none';
        }
        const oldPlayers = chatLog.querySelectorAll('.inline-video-player');
        oldPlayers.forEach(player => player.remove());
    }
    // --- End Media Cleanup Functions ---


    // --- Utility Functions (TTS/Highlighting) ---
    function cleanupHighlighting() {
        const highlighted = chatLog.querySelectorAll('.spoken-word');
        highlighted.forEach(span => span.classList.remove('spoken-word'));
    }

    function stopSpeaking() {
        if (window.speechSynthesis.speaking) {
            window.speechSynthesis.cancel();
            cleanupHighlighting();
            stopButton.disabled = true;
        }
    }
    
    // --- addStructuredMessage (Only supports image/image_list) ---
    function addStructuredMessage(data, sender) {
        const chatBody = document.getElementById('chat-log');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        // 1. Text Content
        const text_to_display = data.text_response || "Here is your content.";
        let display_text = text_to_display.replace(/\*\*/g, '<b>').replace(/\*\*/g, '</b>').trim();
        const words = display_text.split(/(\s+)/);
        const textContentContainer = document.createElement('p');

        words.forEach((word, index) => {
            if (word.trim() !== '') {
                const span = document.createElement('span');
                span.innerHTML = word; 
                span.id = `word-${index}`;
                textContentContainer.appendChild(span);
            } else {
                textContentContainer.appendChild(document.createTextNode(word));
            }
        });
        messageDiv.appendChild(textContentContainer);

        // 2. Image/Image List Content
        if (data.type === 'image') {
            const imgElement = document.createElement('img');
            imgElement.src = data.content;
            imgElement.alt = "Image from search";
            imgElement.style.maxWidth = '100%';
            imgElement.style.height = 'auto';
            imgElement.style.borderRadius = '8px';
            imgElement.style.marginTop = '10px';
            imgElement.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.2)';
            messageDiv.appendChild(imgElement);

        } else if (data.type === 'image_list') {
            const imageListContainer = document.createElement('div');
            imageListContainer.className = 'image-list-container';
            imageListContainer.style.display = 'grid';
            imageListContainer.style.gridTemplateColumns = 'repeat(auto-fit, minmax(200px, 1fr))';
            imageListContainer.style.gap = '10px';
            imageListContainer.style.marginTop = '10px';
            imageListContainer.style.paddingTop = '10px';
            imageListContainer.style.borderTop = '1px solid #ddd';

            data.content.forEach(image => {
                const imageItem = document.createElement('div');
                imageItem.className = 'image-list-item';
                imageItem.style.position = 'relative';
                imageItem.style.overflow = 'hidden';
                imageItem.style.borderRadius = '8px';
                imageItem.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
                imageItem.style.cursor = 'pointer';
                imageItem.style.transition = 'transform 0.2s';

                imageItem.addEventListener('mouseenter', () => {
                    imageItem.style.transform = 'scale(1.02)';
                });
                imageItem.addEventListener('mouseleave', () => {
                    imageItem.style.transform = 'scale(1)';
                });

                imageItem.onclick = () => {
                    window.open(image.url, '_blank');
                };

                const imgElement = document.createElement('img');
                imgElement.src = image.url;
                imgElement.alt = image.title || 'Image from search';
                imgElement.style.width = '100%';
                imgElement.style.height = '150px';
                imgElement.style.objectFit = 'cover';
                imgElement.style.display = 'block';
                
                imgElement.onerror = function() {
                    this.style.display = 'none';
                    const errorDiv = document.createElement('div');
                    errorDiv.style.width = '100%';
                    errorDiv.style.height = '150px';
                    errorDiv.style.backgroundColor = '#f0f0f0';
                    errorDiv.style.display = 'flex';
                    errorDiv.style.alignItems = 'center';
                    errorDiv.style.justifyContent = 'center';
                    errorDiv.style.color = '#666';
                    errorDiv.textContent = 'Image failed to load';
                    imageItem.replaceChild(errorDiv, this);
                };

                imageItem.appendChild(imgElement);
                imageListContainer.appendChild(imageItem);
            });

            messageDiv.appendChild(imageListContainer);

            // Load More button logic
            const loadMoreButton = document.createElement('button');
            loadMoreButton.textContent = 'Load More Images';
            loadMoreButton.style.marginTop = '10px';
            loadMoreButton.style.padding = '8px 16px';
            loadMoreButton.style.backgroundColor = '#4CAF50';
            loadMoreButton.style.color = 'white';
            loadMoreButton.style.border = 'none';
            loadMoreButton.style.borderRadius = '4px';
            loadMoreButton.style.cursor = 'pointer';
            loadMoreButton.style.fontSize = '0.9em';
            loadMoreButton.style.transition = 'background-color 0.2s';

            loadMoreButton.addEventListener('mouseenter', () => {
                loadMoreButton.style.backgroundColor = '#45a049';
            });
            loadMoreButton.addEventListener('mouseleave', () => {
                loadMoreButton.style.backgroundColor = '#4CAF50';
            });

            loadMoreButton.onclick = async () => {
                loadMoreButton.disabled = true;
                loadMoreButton.textContent = 'Loading...';
                
                try {
                    const response = await fetch('/send_command', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text: 'more' })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        const assistantResponse = data.response;
                        
                        if (typeof assistantResponse === 'object' && assistantResponse.type === 'image_list') {
                            assistantResponse.content.forEach(image => {
                                const imageItem = document.createElement('div');
                                imageItem.className = 'image-list-item';
                                imageItem.style.position = 'relative';
                                imageItem.style.overflow = 'hidden';
                                imageItem.style.borderRadius = '8px';
                                imageItem.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.1)';
                                imageItem.style.cursor = 'pointer';
                                imageItem.style.transition = 'transform 0.2s';

                                imageItem.addEventListener('mouseenter', () => {
                                    imageItem.style.transform = 'scale(1.02)';
                                });
                                imageItem.addEventListener('mouseleave', () => {
                                    imageItem.style.transform = 'scale(1)';
                                });

                                imageItem.onclick = () => {
                                    window.open(image.url, '_blank');
                                };

                                const imgElement = document.createElement('img');
                                imgElement.src = image.url;
                                imgElement.alt = image.title || 'Image from search';
                                imgElement.style.width = '100%';
                                imgElement.style.height = '150px';
                                imgElement.style.objectFit = 'cover';
                                imgElement.style.display = 'block';
                                
                                imgElement.onerror = function() {
                                    this.style.display = 'none';
                                    const errorDiv = document.createElement('div');
                                    errorDiv.style.width = '100%';
                                    errorDiv.style.height = '150px';
                                    errorDiv.style.backgroundColor = '#f0f0f0';
                                    errorDiv.style.display = 'flex';
                                    errorDiv.style.alignItems = 'center';
                                    errorDiv.style.justifyContent = 'center';
                                    errorDiv.style.color = '#666';
                                    errorDiv.textContent = 'Image failed to load';
                                    imageItem.replaceChild(errorDiv, this);
                                };

                                imageItem.appendChild(imgElement);
                                imageListContainer.appendChild(imageItem);
                            });
                            
                            loadMoreButton.textContent = 'Load More Images';
                        } else {
                            loadMoreButton.textContent = 'No More Images';
                            loadMoreButton.disabled = true;
                            loadMoreButton.style.backgroundColor = '#ccc';
                        }
                    }
                } catch (error) {
                    console.error('Error loading more images:', error);
                    loadMoreButton.textContent = 'Error Loading';
                }
                
                loadMoreButton.disabled = false;
            };

            messageDiv.appendChild(loadMoreButton);
        } 

        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;

        return messageDiv.querySelector('p'); 
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;

        if (sender === 'assistant' || sender === 'assistant error') {
            text = text.replace(/\*\*\*/g, '').replace(/\*\*/g, '').trim();

            const words = text.split(/(\s+)/);
            const textContentContainer = document.createElement('p');

            words.forEach((word, index) => {
                if (word.trim() !== '') {
                    const span = document.createElement('span');
                    span.textContent = word;
                    span.id = `word-${index}`;
                    textContentContainer.appendChild(span);
                } else {
                    textContentContainer.appendChild(document.createTextNode(word));
                }
            });
            messageDiv.appendChild(textContentContainer);
        } else {
            messageDiv.innerHTML = `<p>${text}</p>`;
        }

        chatLog.appendChild(messageDiv);
        chatLog.scrollTop = chatLog.scrollHeight;

        return messageDiv.querySelector('p');
    }

    function speakText(text) {
        stopSpeaking();
        if (!('speechSynthesis' in window) || !text) { return; }

        const utterance = new SpeechSynthesisUtterance(text);
        globalUtterance = utterance;
        const lastMessageElement = chatLog.lastElementChild;
        let wordSpans = null;

        utterance.rate = 1.2;
        if (femaleVoice) { utterance.voice = femaleVoice; }

        if (lastMessageElement && lastMessageElement.classList.contains('assistant')) {
            wordSpans = lastMessageElement.querySelectorAll('span');
        }

        utterance.onboundary = (event) => {
            if (event.name === 'word' && wordSpans) {
                cleanupHighlighting();

                const textBeforeBoundary = text.substring(0, event.charIndex);
                let wordIndex = textBeforeBoundary.trim().split(/(\s+)/).filter(w => w.trim() !== '').length;
                wordIndex = Math.max(0, wordIndex);

                if (wordSpans && wordIndex < wordSpans.length) {
                    wordSpans[wordIndex].classList.add('spoken-word');
                }
            }
        };

        utterance.onstart = () => { stopButton.disabled = false; };
        utterance.onend = () => { cleanupHighlighting(); stopButton.disabled = true; globalUtterance = null; };
        utterance.onerror = (event) => { console.error('Speech Synthesis Error:', event.error); cleanupHighlighting(); stopButton.disabled = true; globalUtterance = null; };

        window.speechSynthesis.speak(utterance);
    }
    
    async function sendCommand() {
        const userText = commandInput.value.trim();
        if (!userText) return;

        addMessage(userText, 'user');
        commandInput.value = '';
        stopSpeaking();
        removeVideoPlayer();

        try {
            const response = await fetch('/send_command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text: userText })
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ response: 'Server returned error.' }));
                const errorMessage = errorData.response || `HTTP Error: ${response.statusText} (${response.status})`;
                addMessage(errorMessage, 'assistant error');
                speakText("I had trouble connecting to the server. Please check the console.");
                return;
            }

            const data = await response.json();

            const assistantResponse = data.response; 

            if (typeof assistantResponse === 'object' && assistantResponse !== null && (assistantResponse.type === 'image' || assistantResponse.type === 'image_list')) {
                addStructuredMessage(assistantResponse, 'assistant');
                speakText(assistantResponse.text_response);

            } else {
                const textResponse = typeof assistantResponse === 'string' ? assistantResponse : assistantResponse.content || "Sorry, I received an unknown non-text response.";
                addMessage(textResponse, 'assistant');
                speakText(textResponse);
            }

        } catch (error) {
            console.error('Fetch error:', error);
            addMessage('Network Error: Could not reach the server.', 'assistant error');
            speakText('I lost my connection. Please check the network.');
        }
    }

    sendButton.addEventListener('click', sendCommand);
    commandInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            sendCommand();
        }
    });
    
    voiceCommandButton = document.getElementById('voice-command-button');
    if (voiceCommandButton) {
        voiceCommandButton.addEventListener('click', toggleVoiceRecognition);
    }
    stopButton.addEventListener('click', stopSpeaking);
});