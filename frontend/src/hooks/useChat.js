import useVoiceRecognition from "./useVoiceRecognition";
import useInput from "./useInput";
import useChatMessages from "./useChatMessages";

const useChat = () => {
  const { inputValue, setInputValue, textareaRef, handleInputChange } = useInput("");
  const { isListening, handleVoiceInput } = useVoiceRecognition(setInputValue);
  const { messages, 
    setMessages, 
    startedChat, 
    setStartedChat, 
    handleSend, 
    handleSuggestionClick, 
    loading, 
    setLoading,
    error, 
    setError, 
    sources, 
    setSources, 
    scores, 
    terminateOutput,
    abortController,
    setAbortController,
  } = useChatMessages();

  const sendMessage = (inputValue, selectedTopic, selectedUserType, selectedChain, selectedModel, searchOptions) => {
    handleSend(inputValue, selectedTopic, selectedUserType, selectedChain, selectedModel, searchOptions);
    setInputValue("");
  };

  return {
    inputValue,
    setInputValue,
    isListening,
    handleVoiceInput,
    messages,
    setMessages,
    startedChat,
    setStartedChat,
    textareaRef,
    handleInputChange,
    handleSend: sendMessage,
    handleSuggestionClick,
    loading,
    setLoading,
    error,
    setError,
    sources,
    setSources,
    scores,
    terminateOutput,
    abortController,
    setAbortController,
  };
};

export default useChat;
