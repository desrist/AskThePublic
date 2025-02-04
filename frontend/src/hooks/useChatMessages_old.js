// import { useState } from "react";
// import axios from "axios";

// const useChatMessages = () => {
//   const [messages, setMessages] = useState([]);
//   const [startedChat, setStartedChat] = useState(false);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState(null);
//   const [sources, setSources] = useState([]);
//   const [scores, setScores] = useState([]);

//   const handleSend = async (inputValue, selectedTopic, selectedUserType, selectedChain, selectedModel, searchOptions) => {
//     if (inputValue.trim() !== "") {
//       setStartedChat(true);
//       const newMessage = { type: "user", text: inputValue.trim() };
//       setMessages(prevMessages => [...prevMessages, newMessage]);

//       setLoading(true);
//       setError(null);

//       try {
//         // send inputValue to backend
//         const res = await axios.post("https://eej22ko8bc.execute-api.eu-north-1.amazonaws.com/newstage/query", {
//           query: inputValue.trim(),
//           topic: selectedTopic, // topic
//           userType: selectedUserType, // user type
//           chain_type: selectedChain, // chain
//           model_name: selectedModel, // model
//           search_type: searchOptions.searchType, // search type
//           search_kwargs: searchOptions.search_kwargs, // search parameters
//         });

//         const responseMessage = { type: "bot", text: res.data.response };
//         setMessages(prevMessages => [...prevMessages, responseMessage]);
//         setSources(res.data.sources || []);
//         setScores(res.data.scores || null);

//       } catch (error) {
//         console.error("Error fetching data:", error);
//         setError("Error fetching data. Please try again.");
//       } finally {
//         setLoading(false);
//       }
//     }
//   };

//   const handleSuggestionClick = async (question) => {
//     setStartedChat(true);
//     const newMessage = { type: "user", text: question };
//     setMessages(prevMessages => [...prevMessages, newMessage]);

//     setLoading(true);
//     setError(null);

//     try {
//       const res = await axios.post("https://eej22ko8bc.execute-api.eu-north-1.amazonaws.com/newstage/query", {
//         query: question,
//       });

//       const responseMessage = { type: "bot", text: res.data.response };
//       setMessages(prevMessages => [...prevMessages, responseMessage]);
//       setSources(res.data.sources || []);
//       setScores(res.data.scores || null);
//     } catch (error) {
//       console.error("Error fetching data:", error);
//       setError("Error fetching data. Please try again.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return {
//     messages,
//     startedChat,
//     handleSend,
//     handleSuggestionClick,
//     loading,
//     error,
//     sources,
//     scores,
//   };
// };

// export default useChatMessages;


import { useState, useRef } from "react";

const useChatMessages = () => {
  const [messages, setMessages] = useState([]);
  const [startedChat, setStartedChat] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sources, setSources] = useState([]);
  const [scores, setScores] = useState([]);
  const [isTerminated, setIsTerminated] = useState(false);
  const [abortController, setAbortController] = useState(null);

  const terminateOutput = () => {
    setIsTerminated(true);
    setLoading(false);
    // Abort the fetch request
    if (abortController) {
      abortController.abort();
    }
    setMessages((prevMessages) => {
      const updatedMessages = [...prevMessages];
      const lastMessage = updatedMessages[updatedMessages.length - 1];
      if (lastMessage && lastMessage.type === "bot") {
        lastMessage.text += "\n[Terminated by user]";
      }
      return updatedMessages;
    });
  };

  // Function to display text by chunks
  const appendTextSlowly = async (textToAppend) => {
    const chunksize = 6;
    for (let i = 0; i < textToAppend.length; i += chunksize) {
      if (isTerminated) {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 2)); // Adjust speed as needed
      setMessages((prevMessages) => {
        if (isTerminated) {
          return prevMessages; // If is ended, do not update the message
        }
        const updatedMessages = [...prevMessages];
        const lastMessageIndex = updatedMessages.length - 1;
        const lastMessage = updatedMessages[lastMessageIndex];
        if (lastMessage && lastMessage.type === "bot") {
          updatedMessages[lastMessageIndex] = {
            ...lastMessage,
            text: lastMessage.text + textToAppend.slice(i, i + chunksize),
          };
        }
        return updatedMessages;
      });
    }
  };

  const handleSend = async (
    inputValue,
    selectedTopic,
    selectedUserType,
    selectedChain,
    selectedModel,
    searchOptions
  ) => {
    if (inputValue.trim() !== "") {
      setStartedChat(true);
      const newMessage = { type: "user", text: inputValue.trim() };
      setMessages((prevMessages) => [...prevMessages, newMessage]);

      setLoading(true);
      setError(null);
      setIsTerminated(false);

      const controller = new AbortController();
      setAbortController(controller);
      const timeoutId = setTimeout(() => {
        controller.abort();
        setError("Request timed out");
        setLoading(false);
      }, 300000);

      try {
        const response = await fetch(
          "https://eej22ko8bc.execute-api.eu-north-1.amazonaws.com/newstage/query",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              query: inputValue.trim(),
              topic: selectedTopic,
              userType: selectedUserType,
              chain_type: selectedChain,
              model_name: selectedModel,
              search_type: searchOptions.searchType,
              search_kwargs: searchOptions.search_kwargs,
            }),
            signal: controller.signal, // Pass the signal to fetch
          }
        );

        if (!response.ok) {
          if (response.status === 504) {
            throw new Error("Request time out, please decrease the number of sources!");
          } else {
            throw new Error(`Error ${response.status}: ${response.statusText}`);
          }
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let done = false;

        // Add bot message to the messages array
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: "bot", text: "" },
        ]);

        let isAnswer = true;
        let answerText = "";
        let sourcesBuffer = ""; // Initialize buffer for sources
        const endMarker = "<END_OF_ANSWER>";
        while (!done) {
          if (isTerminated) {
            console.log("Output terminated by user.");
            reader.cancel(); // Cancel the reader
            break; // Exit the loop
          }

          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          setLoading(false);

          if (value) {
            let chunk = decoder.decode(value, { stream: true });

            // Connect the chunk to the buffer
            chunk = sourcesBuffer + chunk;
            sourcesBuffer = "";

            if (isAnswer) {
              const endMarkerIndex = chunk.indexOf(endMarker);
              if (endMarkerIndex !== -1) {
                // Found the separator, split the chunk
                const answerChunk = chunk.substring(0, endMarkerIndex);
                // Handle the answer chunk
                answerText += answerChunk;
                await appendTextSlowly(answerChunk);

                // Switch to sources
                isAnswer = false;

                // Add sources chunk to buffer
                sourcesBuffer += chunk.substring(endMarkerIndex + endMarker.length);
              } else {
                // No separator found, add the chunk to the answer
                answerText += chunk;
                await appendTextSlowly(chunk);
              }
            } else {
              // Handle the sources chunk
              sourcesBuffer += chunk;
            }
          }
        }

        if (isTerminated) {
          console.log("Output terminated by user.");
          return;
        }

        //  parse sourcesBuffer
        if (sourcesBuffer) {
          // remove 'Sources:' 
          let sourcesText = sourcesBuffer.trim();
          if (sourcesText.startsWith("Sources:")) {
            sourcesText = sourcesText.substring("Sources:".length).trim();
          }
          const sourceStrings = sourcesText.match(/\{[^}]*\}/g);

          const parsedSources = sourceStrings.map((sourceStr) => JSON.parse(sourceStr));

          setSources(parsedSources);
          setScores(null);
        }
        clearTimeout(timeoutId);
      } catch (error) {
        if (error.name === "AbortError") {
          console.log("Fetch aborted");
        } else {
          console.error("Error fetching data:", error);
          setError("Request time out, please decrease the number of sources!");
        }
      } finally {
        // setLoading(false);
        clearTimeout(timeoutId);
        setAbortController(null);
      }
    }
  };

  // Similar modifications for handleSuggestionClick
  const handleSuggestionClick = async (question) => {
    if (question.trim() !== "") {
      setStartedChat(true);
      const newMessage = { type: "user", text: question };
      setMessages((prevMessages) => [...prevMessages, newMessage]);

      setLoading(true);
      setError(null);
      setIsTerminated(false);

      // Create a new AbortController
      const controller = new AbortController();
      setAbortController(controller);

      try {
        const response = await fetch(
          "https://eej22ko8bc.execute-api.eu-north-1.amazonaws.com/newstage/query",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              query: question,
            }),
            signal: controller.signal, // Pass the signal to fetch
          }
        );

        if (!response.ok) {
          throw new Error(`Error ${response.status}: ${response.statusText}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let done = false;

        // Add bot message to the messages array
        setMessages((prevMessages) => [
          ...prevMessages,
          { type: "bot", text: "" },
        ]);

        let isAnswer = true;
        let answerText = "";
        let sourcesBuffer = ""; // Initialize buffer for sources
        const endMarker = "<END_OF_ANSWER>";

        while (!done) {
          if (isTerminated) {
            console.log("Output terminated by user.");
            reader.cancel(); // Cancel the reader
            break; // Exit the loop
          }

          const { value, done: doneReading } = await reader.read();
          done = doneReading;
          setLoading(false);

          if (value) {
            let chunk = decoder.decode(value, { stream: true });

            // Connect the chunk to the buffer
            chunk = sourcesBuffer + chunk;
            sourcesBuffer = "";

            if (isAnswer) {
              const endMarkerIndex = chunk.indexOf(endMarker);
              if (endMarkerIndex !== -1) {
                // Found the separator, split the chunk
                const answerChunk = chunk.substring(0, endMarkerIndex);
                // Handle the answer chunk
                answerText += answerChunk;
                await appendTextSlowly(answerChunk);

                // Switch to sources
                isAnswer = false;

                // Add sources chunk to buffer
                sourcesBuffer += chunk.substring(endMarkerIndex + endMarker.length);
              } else {
                // No separator found, add the chunk to the answer
                answerText += chunk;
                await appendTextSlowly(chunk);
              }
            } else {
              // Handle the sources chunk
              sourcesBuffer += chunk;
            }
          }
        }

        if (isTerminated) {
          console.log("Output terminated by user.");
          return;
        }

        //  parse sourcesBuffer
        if (sourcesBuffer) {
          // remove 'Sources:' 
          let sourcesText = sourcesBuffer.trim();
          if (sourcesText.startsWith("Sources:")) {
            sourcesText = sourcesText.substring("Sources:".length).trim();
          }
          const sourceStrings = sourcesText.match(/\{[^}]*\}/g);

          const parsedSources = sourceStrings.map((sourceStr) => JSON.parse(sourceStr));

          setSources(parsedSources);
          setScores(null);
        }
      } catch (error) {
        if (error.name === "AbortError") {
          console.log("Fetch aborted");
        } else {
          console.error("Error fetching data:", error);
          setError("Request time out, please decrease the number of sources!");
        }
      } finally {
        // setLoading(false);
        setAbortController(null);
      }
    }
  };

  return {
    messages,
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
    isTerminated,
    setIsTerminated,
    abortController,
    setAbortController,
  };
};

export default useChatMessages;
