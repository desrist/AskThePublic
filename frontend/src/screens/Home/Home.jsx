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
import { Tooltip, IconButton, Popover, SwipeableDrawer, MenuItem, Select, FormControl, InputLabel, Grid } from "@mui/material";
import NaviContainer from "../../components/NaviContainer/NaviContainer";
import SidebarContainer from "../../components/SidebarContainer/SidebarContainer";
import ListIcon from '@mui/icons-material/List';
import { purple, blue } from '@mui/material/colors';
import InfoIcon from "@mui/icons-material/Info";

import QuestionAnswerOutlinedIcon from '@mui/icons-material/QuestionAnswerOutlined';


const usertypeOptions = [
  { value: 'ANY', label: 'Any' },
  { value: 'ACADEMIC_RESEARCH_INSTITTUTION', label: 'Academic Research Institution' },
  { value: 'BUSINESS_ASSOCIATION', label: 'Business Association' },
  { value: 'COMPANY', label: 'Company' },
  { value: 'CONSUMER_ORGANISATION', label: 'Consumer Organisation' },
  { value: 'ENVIRONMENTAL_ORGANISATION', label: 'Environmental Organisation' },
  { value: 'EU_CITIZEN', label: 'EU Citizen' },
  { value: 'NGO', label: 'NGO' },
  { value: 'NON_EU_CITIZEN', label: 'Non EU Citizen' },
  { value: 'OTHER', label: 'Other' },
  { value: 'PUBLIC_AUTHORITY', label: 'Public Authority' },
  { value: 'TRADE_UNION', label: 'Trade Union' },
];

const topic_dict = {
  "Any": "Any",
  "AGRI": "Agriculture and rural development",
  "FINANCE": "Banking and financial services",
  "BORDERS": "Borders and security",
  "BUDGET": "Budget",
  "BUSINESS": "Business and industry",
  "CLIMA": "Climate action",
  "COMP": "Competition",
  "CONSUM": "Consumers",
  "CULT": "Culture and media",
  "CUSTOMS": "Customs",
  "DIGITAL": "Digital economy and society",
  "ECFIN": "Economy, finance and the euro",
  "EAC": "Education and training",
  "EMPL": "Employment and social affairs",
  "ENER": "Energy",
  "ENV": "Environment",
  "ENLARG": "EU enlargement",
  "NEIGHBOUR": "European neighbourhood policy",
  "FOOD": "Food safety",
  "FOREIGN": "Foreign affairs and security policy",
  "FRAUD": "Fraud prevention",
  "HOME": "Home affairs",
  "HUMAN": "Humanitarian aid and civil protection",
  "INST": "Institutional affairs",
  "INTDEV": "International cooperation and development",
  "JUST": "Justice and fundamental rights",
  "MARE": "Maritime affairs and fisheries",
  "ASYL": "Migration and asylum",
  "HEALTH": "Public health",
  "REGIO": "Regional policy",
  "RESEARCH": "Research and innovation",
  "SINGMARK": "Single market",
  "SPORT": "Sport",
  "STAT": "Statistics",
  "TAX": "Taxation",
  "TRADE": "Trade",
  "TRANSPORT": "Transport",
  "YOUTH": "Youth"
};


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
    scores
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

  const handleUserTypeChange = (event) => {
    setSelectedUsertype(event.target.value);
  };
  const handleTopicChange = (event) => {
    setSelectedTopic(event.target.value);
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
          <div className="header">
          </div>
          <div className="menu">
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
            selectedTopic={selectedTopic}
            setSelectedTopic={setSelectedTopic}
            selectedUserType={selectedUserType}
            setSelectedUserType={setSelectedUsertype}
          />
        ) : (
          <div className="contents">
            <p className="title">Ask ...!</p>
            <div className="subtitle">
              <p className="text-wrapper">
                This AI-powered app allows you to explore public opinions about EU policies and initiatives listed on the
                <strong><a href="https://ec.europa.eu/info/law/better-regulation/have-your-say_en"> "Have Your Say"</a></strong> website,
                enabling you to ask specific groups of people questions about their perspectives on these topics.
              </p>
            </div>
            <div style={{ display: "flex" }}>
              <div className="search-bar">
                <div className="content">
                  <RiRobot2Line size="20px" className="robot-icon" />
                  <textarea
                    ref={textareaRef}
                    value={inputValue}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                    className="text-wrapper-2"
                    placeholder="What ... ?"
                    rows={1}
                  />
                </div>
                <button onClick={handleVoiceInput} className="voice-button">
                  <VuesaxTwotoneMicrophone1 className="icon-instance-node" />
                </button>
                <button onClick={handleSubmit} className="send-button">
                  <OutlineArrowCircleUp className="outline-arrow-circle-up" color='var(--black)' />
                </button>
              </div>
              <Tooltip title='New Chat' placement="bottom">
                <IconButton edge="end" color="inherit" onClick={handleNewChat}>
                  <QuestionAnswerOutlinedIcon className="newchat-icon" sx={{ color: blue[500] }} />
                </IconButton>
              </Tooltip>

            </div>
            <Grid container justifyContent="center" spacing={2}>
              {/* User Type Selection */}
              <Grid item xs={2}>
                <Tooltip title="Whom do you want to ask with your question?" placement="top" arrow>
                  <FormControl fullWidth>
                    <InputLabel id="user-type-label">Whom</InputLabel>
                    <Select
                      labelId="user-type-label"
                      id="user-type-dropdown"
                      value={selectedUserType || "ANY"}
                      onChange={(e) => {
                        const value = e.target.value;
                        setSelectedUsertype(value === "ANY" ? null : value);
                      }}
                      className="search-bar-drop"
                    >
                      {usertypeOptions.map((option) => (
                        <MenuItem key={option.value} value={option.value}>
                          {option.label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Tooltip>
              </Grid>

              {/* Topic Selection */}
              <Grid item xs={2}>
                <Tooltip title="What topic do you want to ask about?" placement="top" arrow>
                  <FormControl fullWidth>
                    <InputLabel id="topic-label" shrink>
                      About
                    </InputLabel>
                    <Select
                      labelId="topic-label"
                      id="topic-dropdown"
                      value={selectedTopic || "Any"}
                      onChange={(e) => {
                        const value = e.target.value;
                        setSelectedTopic(value === "Any" ? null : value);
                      }}
                      className="search-bar-drop"
                    >
                      {Object.entries(topic_dict).map(([value, label]) => (
                        <MenuItem key={value} value={label}>
                          {label}
                        </MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                </Tooltip>
              </Grid>
            </Grid>

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