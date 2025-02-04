import React, { useState } from "react";
import { Title } from "../../components/Title";
import { VuesaxBulkMenu1 } from "../../icons/VuesaxBulkMenu1";
import { VuesaxLinearFlash5 } from "../../icons/VuesaxLinearFlash5";
import { VuesaxTwotoneMicrophone1 } from "../../icons/VuesaxTwotoneMicrophone1";
import { OutlineArrowCircleUp } from "../../icons/OutlineArrowCircleUp";
import "./style.css";
import ChatContainer from "../../components/ChatContainer/ChatContainer";
import useChat from "../../hooks/useChat";
import useDynamicProperty from "../../hooks/useDynamicProperty";
import { RiRobot2Line } from "react-icons/ri";
import { IconButton, Popover, SwipeableDrawer } from "@mui/material";
import NaviContainer from "../../components/NaviContainer/NaviContainer";
import SidebarContainer from "../../components/SidebarContainer/SidebarContainer";
import ListIcon from '@mui/icons-material/List';
import QuestionAnswerOutlinedIcon from '@mui/icons-material/QuestionAnswerOutlined';
import Tooltip from "@mui/material/Tooltip";
import { purple, blue } from '@mui/material/colors';

export const Home = () => {
  const { 
    inputValue,
    setInputValue,
    isListening,
    handleVoiceInput,
    messages,
    startedChat,
    textareaRef,
    handleInputChange,
    handleSend,
    handleSuggestionClick,
    loading,
    error,
    sources,
    scores,
  } = useChat();

  const [selectedTopic, setSelectedTopic] = useState(null);
  const [selectedUserType, setSelectedUsertype] = useState(null);
  const [selectedChain, setSelectedChain] = useState('retrievalqa');
  const [selectedModel, setSelectedModel] = useState('gpt-4o-mini');
  const [searchOptions, setSearchOptions] = useState({ searchType: 'similarity', search_kwargs: { k: 15 } });

  const properties = ["default", "variant-2", "variant-3", "variant-4"];
  const property = useDynamicProperty(properties);

  const handleSendWithTopic = () => {
    handleSend(inputValue, selectedTopic, selectedUserType, selectedChain, selectedModel, searchOptions); // Send query and selected parameters to backend
    setInputValue(""); // Clear input field
  };

  const handleSubmit = async (event = null) => {
    if (event) event.preventDefault();
    handleSendWithTopic(inputValue);
    setInputValue("");
  };
  
  // enter key to send query, shift enter to add new line
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading && inputValue) {
        handleSend(inputValue, selectedTopic, selectedUserType, selectedChain, selectedModel, searchOptions);
        setInputValue("");
      }
    }
  };

  // start new chat
  const handleNewChat = () => {
    // setStartedChat(false);
    // setInputValue("");
    // setMessages([]);
    // // setSources([]);
    // // setError(null);
    // setLoading(false);
    // setIsTerminated(true);

    // if (abortController) {
    //   abortController.abort();
    // }
    // setAbortController(null);
    window.location.reload();
  };

  // menu
  const [anchorEl, setAnchorEl] = useState(null);
  const handleMenuClick = (event) => {
    event.stopPropagation();
    event.preventDefault();
    setAnchorEl(event.currentTarget);
  };
  const handleMenuClose = (event) => {
    event.stopPropagation();
    event.preventDefault();
    setAnchorEl(null);
  };
  const open = Boolean(anchorEl);

  // sidebar
  const [drawerOpen, setDrawerOpen] = useState(false);
  const handleDrawerToggle = (open) => (event) => {
    if (event.type === 'keydown' && (event.key === 'Tab' || event.key === 'Shift')) {
      return;
    }
    setDrawerOpen(open);
  };

  return (
    <div className="home">
      <div className="top">
        <div className="navigation-bar">
          <div className="side-bar">
            <Tooltip title='More Options Here' placement="bottom">
              <IconButton edge="start" color="inherit" onClick={handleDrawerToggle(true)}>
                <ListIcon className="list-icon" sx={{ color: blue[500] }}/>
              </IconButton>
            </Tooltip>
            <Tooltip title = 'New Chat' placement="bottom">
              <IconButton edge="end" color="inherit" onClick={handleNewChat}>
                <QuestionAnswerOutlinedIcon className="newchat-icon" sx={{ color: blue[500] }}/>
              </IconButton>
            </Tooltip>
          </div>
          <div className="menu">
            {/* <IconButton edge="start" color="inherit" onClick={handleMenuClick}>
              <VuesaxBulkMenu1 className="vuesax-bulk-menu" />
            </IconButton> */}
          </div>
          <Popover
            anchorEl={anchorEl}
            open={open}
            onClose={handleMenuClose}
            anchorOrigin={{
              vertical: 'bottom',
              horizontal: 'center',
            }}
            transformOrigin={{
              vertical: 'top',
              horizontal: 'center',
            }}
          >
            <NaviContainer handleClose={handleMenuClose} />
          </Popover>
        </div>
        {startedChat ? (
          <ChatContainer
            inputValue={inputValue}
            handleInputChange={handleInputChange}
            handleVoiceInput={handleVoiceInput}
            handleSend={handleSubmit}
            isListening={isListening}
            textareaRef={textareaRef}
            messages={messages}
            loading={loading}
            error={error}
            sources={sources}
            scores={scores}
          />
        ) : (
          <div className="contents">
            <div className="div">
              {/* <Title
                className="title-instance"
                property1={property}
                text="Citizen Feedback Enhancer"
                visible={true}
              /> */}
              <p className="title">Citizen Feedback Enhancer</p>
              <div className="subtitle">
                <p className="text-wrapper">
                  Ask me freely about EU laws and initiatives, this chatbot will present publics' opinions about them.
                </p>
              </div>
            </div>
            <div className="frame" />
            <div className="search-bar">
              <div className="content">
                <RiRobot2Line size="20px" className="robot-icon" />
                <textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyDown={handleKeyDown}
                  className="text-wrapper-2"
                  placeholder="Ask ...?"
                  rows={1}
                />
              </div>
              <button onClick={handleVoiceInput} className="voice-button">
                <VuesaxTwotoneMicrophone1 className="icon-instance-node" />
              </button>
              <button onClick={handleSubmit} className="send-button">
                <OutlineArrowCircleUp className="outline-arrow-circle-up" color='var(--black)'/>
              </button>
            </div>
            <div className="bottom">
              <div className="text-wrapper-3">You may ask</div>
              <div className="boxes">
                <div className="suggestion-card" onClick={() => handleSuggestionClick("How do stakeholders view the EU's Renewable Energy Directive and its impact on energy transition?")}>
                  <p className="suggestion-question">
                    <span className="lineup">How do stakeholders view the EU's Renewable Energy Directive </span>
                    <span className="linedown">and its impact on energy transition?</span>
                  </p>
                  <div className="frame-2">
                    <div className="text-wrapper-5">Ask this</div>
                    <VuesaxLinearFlash5 className="vuesax-linear-flash" />
                  </div>
                </div>
                <div className="suggestion-card" onClick={() => handleSuggestionClick("What are the main concerns of EU citizens regarding the Common Agricultural Policy (CAP)?")}>
                  <p className="suggestion-question">
                    <span className="lineup">What are the main concerns of EU citizens regarding the </span>
                    <span className="linedown">Common Agricultural Policy (CAP)?</span>
                  </p>
                  <div className="frame-2">
                    <div className="text-wrapper-5">Ask this</div>
                    <VuesaxLinearFlash5 className="vuesax-linear-flash" />
                  </div>
                </div>
                <div className="suggestion-card" onClick={() => handleSuggestionClick("How do European citizens view the EU’s policies on managing migration and asylum seekers?")}>
                  <p className="suggestion-question">
                    <span className="lineup">How do European citizens view the EU's policies on managing </span>
                    <span className="linedown">migration and asylum seekers?</span>
                  </p>
                  <div className="frame-2">
                    <div className="text-wrapper-5">Ask this</div>
                    <VuesaxLinearFlash5 className="vuesax-linear-flash" />
                  </div>
                </div>
              </div>
            </div>
            {loading && <p>Loading...</p>}
            {error && <p>{error}</p>}
          </div>
        )}
      </div>
      <SwipeableDrawer
        anchor="left"
        sx={{
          flexShrink: 0,
          height: '100vh',
          '& .MuiDrawer-paper': {
            width: 670,
            height: '100vh',
          },
        }}
        open={drawerOpen}
        onClose={handleDrawerToggle(false)}
        onOpen={handleDrawerToggle(true)}
      >
        <SidebarContainer 
          setSelectedTopic={setSelectedTopic}
          setSelectedUsertype={setSelectedUsertype}
          setSelectedChain={setSelectedChain}
          setSelectedModel={setSelectedModel}
          setSearchOptions={setSearchOptions}
        />
      </SwipeableDrawer>
    </div>
  );
};
