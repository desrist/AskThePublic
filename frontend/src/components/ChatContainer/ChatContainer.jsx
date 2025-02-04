// build interface for chatting 

import React, { useEffect, useRef, useState } from "react";
import { VuesaxBulkMenu1 } from "../../icons/VuesaxBulkMenu1";
import { VuesaxTwotoneMicrophone1 } from "../../icons/VuesaxTwotoneMicrophone1";
import { OutlineArrowCircleUp } from "../../icons/OutlineArrowCircleUp";
import StopCircleOutlinedIcon from '@mui/icons-material/StopCircleOutlined';
import CircularProgress from '@mui/material/CircularProgress';
import "./style.css";
import { RiRobot2Line } from "react-icons/ri";
import SourceContainer from "../SourceContainer/SourceContainer";
import RatingContainer from "../RatingContainer/RatingContainer";
import ReactMarkdown from "react-markdown";
import { purple, blue } from '@mui/material/colors';
import { Tooltip, IconButton, Popover, SwipeableDrawer, MenuItem, Select, FormControl, InputLabel, Grid } from "@mui/material";
import QuestionAnswerOutlinedIcon from '@mui/icons-material/QuestionAnswerOutlined';

const parseMessageText = (text) => {
  return <ReactMarkdown children={text} />;
  // const lines = text.split("\n").filter((line) => line.trim() !== ""); // Split by line and filter empty lines
  // return lines.map((line, index) => {
  //   if (line.startsWith("# ")) {
  //     return <h1 key={index} className="message-title">{line.replace("# ", "")}</h1>;
  //   } else if (line.startsWith("## ")) {
  //     return <h2 key={index} className="message-title">{line.replace("## ", "")}</h2>;
  //   }  else if (line.startsWith("### ")) {
  //     return <h3 key={index} className="message-title">{line.replace("### ", "")}</h3>;
  //   }  else if (line.startsWith("#### ")) {
  //     return <h4 key={index} className="message-subtitle">{line.replace("#### ", "")}</h4>;
  //   } else if (line.startsWith("- ")) {
  //     return <li key={index} className="message-list-item">{line.replace("- ", "")}</li>;
  //   } else {
  //     // Process bold text (e.g., **bold**)
  //     const formattedLine = line.replace(/\*\*(.*?)\*\*/g, (match, p1) => `<strong>${p1}</strong>`);
  //     return <p key={index} dangerouslySetInnerHTML={{ __html: formattedLine }} />;
  //   }
  // });
};


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

const ChatContainer = ({
  inputValue,
  handleInputChange,
  handleVoiceInput,
  handleSend,
  isListening,
  textareaRef,
  messages,
  loading,
  error,
  sources,
  scores,
  terminateOutput,
  selectedTopic,
  setSelectedTopic,
  selectedUserType,
  setSelectedUserType,
}) => {
  // control scroll

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!loading) {
      handleSend();
    }
  };

  // enter key to send query, shift enter to add new line
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) {
        handleSend();
      }
    }
  }

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

  return (
    <div className="chat">
      <div className="top">
        <div style={{ display: "flex" }}>

          <div className="search-bar">
            <div className="search-bar-content">
              <textarea
                ref={textareaRef}
                value={inputValue}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                className="text-wrapper-2"
                placeholder="Ask ...!"
                rows={1}
                disabled={loading}
              />
            </div>
            <button onClick={handleVoiceInput} className="voice-button" disabled={loading}>
              <VuesaxTwotoneMicrophone1 className="icon-instance-node" />
            </button>
            <button onClick={handleSubmit} className="send-button" disabled={loading}>
              <OutlineArrowCircleUp className="outline-arrow-circle-up" color='var(--black)' />
            </button>

            {/* <button 
            onClick={loading ? terminateOutput : handleSubmit} 
            className="send-button"
            title={loading ? "Stop" : "Send"}
          >
            {loading ? (
              <StopCircleOutlinedIcon style={{ color: "gray" }} />
            ) : (
              <OutlineArrowCircleUp className="outline-arrow-circle-up" color='var(--black)' />
            )}
          </button> */}
          </div>
          <Tooltip title='New Chat' placement="bottom">
            <IconButton edge="end" color="inherit" onClick={handleNewChat}>
              <QuestionAnswerOutlinedIcon className="newchat-icon" sx={{ color: blue[500] }} />
            </IconButton>
          </Tooltip>
        </div>
        <Grid container justifyContent="center" style={{ marginTop: "15px" }} spacing={2}>
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
                    setSelectedUserType(value === "ANY" ? null : value);
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
      </div>

      <div className="main-content">
        <div className="left-content">
          {/* <RatingContainer scores={scores} /> */}
        </div>
        <div className="chat-content">
          <div className="messages-container">
            <div className="empty-content"></div>
            <div className="messages-content">
              {messages.map((message, index) => (
                <div key={index} className={`message ${message.type}`}>
                  {message.type === "bot" && (
                    <div className="icon-wrapper">
                      <RiRobot2Line size="20px" className="robot-icon" />
                    </div>
                  )}
                  <div className="message-text">
                    {/* {message.text} */}
                    <ReactMarkdown>{message.text}</ReactMarkdown>
                  </div>
                </div>
              ))}
              {loading && (
                <div className="message bot">
                  <div className="icon-wrapper">
                    <RiRobot2Line size="20px" className="robot-icon" />
                  </div>
                  <div className="loading-text">
                    <CircularProgress size={30} />
                    <p>Searching for Relevant Public Opinions ...</p>
                  </div>
                </div>
              )}
              {error && (
                <div className="message bot">
                  <div className="icon-wrapper">
                    <RiRobot2Line size="20px" className="robot-icon" />
                  </div>
                  <div className="message-text">{error}</div>
                </div>
              )}
            </div>
          </div>
        </div>
        <div className="right-content">
          <SourceContainer sources={sources} loading={loading} />
        </div>
      </div>
    </div>
  );
};

export default ChatContainer;