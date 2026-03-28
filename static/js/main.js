// Handle Tab Switching in Login/Register
document.addEventListener("DOMContentLoaded", () => {
    const tabLogin = document.getElementById("tab-login");
    const tabRegister = document.getElementById("tab-register");
    const formLogin = document.getElementById("login-form");
    const formRegister = document.getElementById("register-form");
    const indicator = document.getElementById("tab-indicator");

    if (tabLogin && tabRegister) {
        tabLogin.addEventListener("click", () => {
            tabLogin.classList.remove("text-gray-400");
            tabLogin.classList.add("text-emerald-600", "font-bold");
            tabRegister.classList.remove("text-emerald-600", "font-bold");
            tabRegister.classList.add("text-gray-400");
            formLogin.classList.remove("hidden");
            formRegister.classList.add("hidden");
            indicator.style.transform = "translateX(0)";
        });

        tabRegister.addEventListener("click", () => {
            tabRegister.classList.remove("text-gray-400");
            tabRegister.classList.add("text-emerald-600", "font-bold");
            tabLogin.classList.remove("text-emerald-600", "font-bold");
            tabLogin.classList.add("text-gray-400");
            formRegister.classList.remove("hidden");
            formLogin.classList.add("hidden");
            indicator.style.transform = "translateX(100%)";
        });
    }

    // Handle Login API
    if (formLogin) {
        formLogin.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("login-email").value;
            const password = document.getElementById("login-password").value;
            const errorDiv = document.getElementById("login-error");
            
            try {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({email, password})
                });
                const data = await res.json();
                
                if (data.success) {
                    window.location.href = "/dashboard";
                } else {
                    errorDiv.textContent = data.error || "Login failed";
                    errorDiv.classList.remove("hidden");
                }
            } catch (err) {
                errorDiv.textContent = "Network error";
                errorDiv.classList.remove("hidden");
            }
        });
    }

    // Handle Register
    if (formRegister) {
        formRegister.addEventListener("submit", async (e) => {
            e.preventDefault();
            const email = document.getElementById("register-email").value;
            const password = document.getElementById("register-password").value;
            const errorDiv = document.getElementById("register-error");
            
            try {
                const res = await fetch("/api/auth/register", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({email, password})
                });
                const data = await res.json();
                
                if (data.success) {
                    alert("Registration successful! Please login.");
                    tabLogin.click();
                } else {
                    errorDiv.textContent = data.error || "Registration failed";
                    errorDiv.classList.remove("hidden");
                }
            } catch (err) {
                errorDiv.textContent = "Network error";
                errorDiv.classList.remove("hidden");
            }
        });
    }
});

// Tret AI Global Widget Logic & Voice Commands
document.addEventListener("DOMContentLoaded", () => {
    const tretBtn = document.getElementById("tret-btn");
    const tretChatWindow = document.getElementById("tret-chat-window");
    const tretCloseBtn = document.getElementById("tret-close-btn");
    const tretForm = document.getElementById("tret-form");
    const tretInput = document.getElementById("tret-input");
    const tretHistory = document.getElementById("tret-chat-history");
    const tretLoader = document.getElementById("tret-loader");
    const voiceBtn = document.getElementById("tret-voice-btn");
    const voicePulse = document.getElementById("tret-voice-pulse");

    if (!tretBtn) return; // Wait, tret_widget is on all pages

    let isOpen = false;
    let chatHistoryData = []; // Store session chat history locally

    // Toggle Chat Window
    tretBtn.addEventListener("click", () => {
        isOpen = !isOpen;
        if (isOpen) {
            tretChatWindow.classList.remove("scale-0", "opacity-0", "pointer-events-none");
            tretChatWindow.classList.add("scale-100", "opacity-100", "pointer-events-auto");
            tretInput.focus();
        } else {
            closeChat();
        }
    });

    tretCloseBtn.addEventListener("click", closeChat);

    function closeChat() {
        isOpen = false;
        tretChatWindow.classList.remove("scale-100", "opacity-100", "pointer-events-auto");
        tretChatWindow.classList.add("scale-0", "opacity-0", "pointer-events-none");
        if (isRecording) {
            recognition.stop();
        }
        window.speechSynthesis.cancel(); // Stop talking if closed
    }

    function addTretMessage(role, text) {
        const div = document.createElement("div");
        const isUser = role === "user";
        div.className = `flex ${isUser ? "justify-end" : "justify-start"} animate-fade-in-up`;
        
        let bubbleClass = isUser 
            ? "bg-gradient-to-r from-emerald-500 to-emerald-600 text-white shadow-sm rounded-tl-2xl rounded-tr-sm rounded-bl-2xl rounded-br-2xl"
            : "bg-white border border-gray-100 text-gray-800 shadow-sm rounded-tl-sm rounded-tr-2xl rounded-bl-2xl rounded-br-2xl";

        // Very simple markdown to HTML for bold (since showdown might not be globally imported in main.js, we do a quick replace)
        let htmlText = text.replace(/\*\*(.*?)\*\*/g, '<b>$1</b>').replace(/\n/g, '<br>');

        div.innerHTML = `<div class="max-w-[85%] px-4 py-3 text-sm leading-relaxed transition-all duration-300 hover:shadow-md ${bubbleClass}">${htmlText}</div>`;
        tretHistory.appendChild(div);
        tretHistory.scrollTop = tretHistory.scrollHeight;
    }

    async function submitTretMessage(message) {
        if (!message) return;
        
        addTretMessage("user", message);
        tretInput.value = "";
        tretLoader.classList.remove("hidden");
        
        chatHistoryData.push({role: "user", message: message});

        try {
            const res = await fetch("/api/tret-ai/chat", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    history: chatHistoryData.slice(0, -1), // Send all but the last message
                    message: message
                })
            });
            const data = await res.json();
            
            if (data.response) {
                addTretMessage("ai", data.response);
                chatHistoryData.push({role: "ai", message: data.response});
                speakText(data.response); // Use Voice Synthesis to read the answer!
            }
        } catch (err) {
            addTretMessage("ai", "Oops, I had a network error. Could you try again?");
        } finally {
            tretLoader.classList.add("hidden");
        }
    }

    tretForm.addEventListener("submit", (e) => {
        e.preventDefault();
        submitTretMessage(tretInput.value.trim());
    });

    // --- Voice Command Logic (Speech Recognition & Synthesis) ---
    let isRecording = false;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function() {
            isRecording = true;
            voicePulse.classList.remove("opacity-0");
            voiceBtn.classList.add("text-red-500");
        };

        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            tretInput.value = transcript;
            submitTretMessage(transcript);
        };

        recognition.onerror = function() {
            isRecording = false;
            stopVoiceUI();
        };

        recognition.onend = function() {
            isRecording = false;
            stopVoiceUI();
        };
    }

    function stopVoiceUI() {
        voicePulse.classList.add("opacity-0");
        voiceBtn.classList.remove("text-red-500");
    }

    voiceBtn.addEventListener("click", () => {
        if (!recognition) {
            alert("Your browser or environment does not support Voice Commands. Please use a secure context (HTTPS/localhost) or Chrome/Edge browser.");
            return;
        }
        
        // Stop any current reading
        window.speechSynthesis.cancel();

        if (isRecording) {
            recognition.stop();
        } else {
            recognition.start();
        }
    });

    // Text to Speech
    function speakText(text) {
        if (!window.speechSynthesis) return;
        
        window.speechSynthesis.cancel(); // cancel playing sounds
        
        // Clean markdown from spoken text
        const cleanText = text.replace(/[*#_]/g, "");
        const msg = new SpeechSynthesisUtterance(cleanText);
        msg.rate = 1.0;
        msg.pitch = 1.0;
        
        // Try to find a good English voice
        const voices = window.speechSynthesis.getVoices();
        const genericVoice = voices.find(v => v.lang.includes('en-') && v.name.includes('Female')) || voices[0];
        if (genericVoice) msg.voice = genericVoice;
        
        window.speechSynthesis.speak(msg);
    }
});
