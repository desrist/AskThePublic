// hooks for input field

import { useState, useEffect, useRef } from "react";

const useInput = (initialValue) => {
  const [inputValue, setInputValue] = useState(initialValue);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  return {
    inputValue,
    setInputValue,
    textareaRef,
    handleInputChange,
  };
};

export default useInput;
