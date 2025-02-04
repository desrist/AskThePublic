// hooks for voice recognition

import { useState, useEffect } from "react";

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'en-US';

const useVoiceRecognition = (setInputValue) => {
  const [isListening, setIsListening] = useState(false);

  const handleVoiceInput = () => {
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputValue(prevValue => prevValue + " " + transcript);
      setIsListening(false); // Reset state after speech recognition ends
    };

    recognition.onend = () => {
      setIsListening(false); // Reset status after recognition is completed
    };
  };

  return {
    isListening,
    handleVoiceInput,
  };
};

export default useVoiceRecognition;
