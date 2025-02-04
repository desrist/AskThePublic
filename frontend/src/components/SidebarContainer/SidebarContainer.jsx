import React, { useState } from 'react';
import { useTheme } from '@mui/material/styles';
import OutlinedInput from '@mui/material/OutlinedInput';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CircularProgress from '@mui/material/CircularProgress';
import Autocomplete from '@mui/material/Autocomplete';
import useKeywordSearch from '../../hooks/useKeywordSearch';
import './style.css';

const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      maxwidth: 200,
      width: 100,
    },
  },
};

const topic_dict = {
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

// const chainOptions = [
//   {value: 'conversational', label: 'Conversational Retrieval Chain'},
//   {value: 'retrievalqa', label: 'QA Retrieval Chain'}
// ];

// const modelOptions = [
//   { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
//   { value: 'gpt-4o-mini', label: 'GPT-4o Mini' },
//   { value: 'gpt-4o', label: 'GPT-4o' },
// ];

// const searchTypeOptions = [
//   { value: 'similarity', label: 'Similarity' },
//   { value: 'mmr', label: 'MMR (Maximal Marginal Relevance)' },
// ];

// const fetchKOptions = [20, 30, 40];

export default function SidebarContainer({ setSelectedTopic, setSelectedUsertype, setSelectedChain, setSelectedModel, setSearchOptions }) {
  const theme = useTheme();
  const [first, setFirst] = useState('');
  const [usertype, setUsertype] = useState('');
  const [k, setK] = useState(15);
  // const [chain, setChain] = useState('retrievalqa');
  // const [model, setModel] = useState('gpt-4o');
  // const [searchType, setSearchType] = useState('similarity');
  
  // const [fetchK, setFetchK] = useState(20);
  // const [lambdaMult, setLambdaMult] = useState(0.5);
  // const [scoreThreshold, setScoreThreshold] = useState(0.8);
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const firstOptions = ['Any', ...Object.values(topic_dict)];

  const handleFirstChange = (event) => {
    setFirst(event.target.value);
  };

  const handleUsertypeChange = (event) => {
    setUsertype(event.target.value);
  };

  // const handleChainChange = (event) => {
  //   setChain(event.target.value);
  // }

  // const handleModelChange = (event) => {
  //   setModel(event.target.value);
  // };

  // const handleSearchTypeChange = (event) => {
  //   setSearchType(event.target.value);
  // };

  const handleSubmit = () => {
    const topic = first === 'Any' ? null : first;
    const selectedUsertype = usertype === 'Any' ? null : usertype;
    setSelectedTopic(topic);
    console.log(topic);
    setSelectedUsertype(selectedUsertype);
    console.log(selectedUsertype);
    // setSelectedChain(chain);
    // setSelectedModel(model);
    setSearchOptions({
      // searchType,
      search_kwargs: {
        k,
        // fetch_k: searchType === 'mmr' ? fetchK : undefined,
        // lambda_mult: searchType === 'mmr' ? lambdaMult : undefined,
        // score_threshold: searchType === 'similarity_score_threshold' ? scoreThreshold : undefined,
      }
    });
    setOpenSnackbar(true); // open Snackbar
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false); // close Snackbar
  };

  const {
    keyword,
    searchResults,
    isLoading,
    error,
    handleKeywordChange,
    handleKeywordSearch,
    selectedResult,
    setSelectedResult,
    generateSummary,
    summary,
    isGeneratingSummary,
    setSummary
  } = useKeywordSearch();

  return (
    <div className="sidebar-container">
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <div className="title">Settings</div>
        </AccordionSummary>

        <AccordionDetails>
          <div className='select-box'>
            {/* Topic */}
            <FormControl className="form-control">
              <InputLabel id="first-select-label">Topics</InputLabel>
              <Select
                labelId="first-select-label"
                id="first-select"
                value={first}
                onChange={handleFirstChange}
                input={<OutlinedInput label="Topics" />}
                MenuProps={MenuProps}
              >
                {firstOptions.map((option) => (
                  <MenuItem key={option} value={option}>
                    {option}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            {/* userType*/}
            <FormControl className="form-control">
              <InputLabel id="usertype-select-label">User Type</InputLabel>
              <Select
                labelId="usertype-select-label"
                id="usertype-select"
                value={usertype}
                onChange={handleUsertypeChange}
                input={<OutlinedInput label="User Type" />}
                MenuProps={MenuProps}
              >
                {usertypeOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            {/* Chain */}
            {/* <FormControl className="form-control">
              <InputLabel id="chain-select-label">Retrieval Chain</InputLabel>
              <Select
                labelId="chain-select-label"
                id="chain-select"
                value={chain}
                onChange={handleChainChange}
                input={<OutlinedInput label="Retrieval Chain" />}
                MenuProps={MenuProps}
              >
                {chainOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl> */}
            {/* Model */}
            {/* <FormControl className="form-control">
              <InputLabel id="model-select-label">Model</InputLabel>
              <Select
                labelId="model-select-label"
                id="model-select"
                value={model}
                onChange={handleModelChange}
                input={<OutlinedInput label="Model" />}
                MenuProps={MenuProps}
              >
                {modelOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl> */}
            {/* Search Type */}
            {/* <FormControl className="form-control">
              <InputLabel id="search-type-select-label">Search Type</InputLabel>
              <Select
                labelId="search-type-select-label"
                id="search-type-select"
                value={searchType}
                onChange={handleSearchTypeChange}
                input={<OutlinedInput label="Search Type" />}
                MenuProps={MenuProps}
              >
                {searchTypeOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    {option.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {(searchType === 'similarity' || searchType === 'mmr' || searchType === 'similarity_score_threshold') && (
              <TextField
                label="Number of Results (k)"
                type="number"
                value={k}
                onChange={(e) => setK(parseInt(e.target.value))}
                fullWidth
                margin="normal"
              />
            )}

            {searchType === 'mmr' && (
              <>
                <FormControl className="form-control">
                  <InputLabel id="fetch-k-select-label">Fetch K (MMR)</InputLabel>
                  <Select
                    labelId="fetch-k-select-label"
                    id="fetch-k-select"
                    value={fetchK}
                    onChange={(e) => setFetchK(parseInt(e.target.value))}
                    input={<OutlinedInput label="Fetch K (MMR)" />}
                    MenuProps={MenuProps}
                  >
                    {fetchKOptions.map((option) => (
                      <MenuItem key={option} value={option}>
                        {option}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <TextField
                  label="Lambda Mult (MMR)"
                  type="number"
                  value={lambdaMult}
                  onChange={(e) => setLambdaMult(parseFloat(e.target.value))}
                  fullWidth
                  margin="normal"
                />
              </>
            )}

            {searchType === 'similarity_score_threshold' && (
              <TextField
                label="Score Threshold"
                type="number"
                value={scoreThreshold}
                onChange={(e) => setScoreThreshold(parseFloat(e.target.value))}
                fullWidth
                margin="normal"
              />
            )} */}
            {/* Number of Results */}
            <TextField
              label="Number of Returned Sources (Recommend 5-30)"
              type="text"
              value={k === 0 || k ? k : ""}
              onChange={(e) => {
                const value = parseInt(e.target.value, 10);
                setK(Number.isNaN(value) ? "" : value);
              }}
              inputProps={{
                inputMode: "numeric",
                pattern: "[0-9]*",
              }}
              fullWidth
              margin="normal"
            />
            <Button className="submit-button" variant="contained" color="primary" onClick={handleSubmit}>
              Submit
            </Button>
          </div>
        </AccordionDetails>
      </Accordion>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <div className="title">Search for Initiatives of Interest</div>
        </AccordionSummary>
        <AccordionDetails>
          <div className="keyword-search-box">
            <Autocomplete
              freeSolo
              options={searchResults}
              getOptionLabel={(option) => {
                return typeof option === 'string' ? option : option.shortTitle || String(option.id);
              }}
              filterOptions={(options, state) => {
                return options.filter((option) => {
                  const label = option.shortTitle || String(option.id);
                  return label.toLowerCase().includes(state.inputValue.toLowerCase()) ||
                    String(option.id).includes(state.inputValue);
                });
              }}
              inputValue={keyword}
              onInputChange={(event, newInputValue) => {
                handleKeywordChange(newInputValue);
              }}
              onChange={(event, newValue) => {
                if (newValue) {
                  setSelectedResult(newValue);
                  setSummary(null);
                } else {
                  setSelectedResult(null);
                  setSummary(null);
                }
              }}
              renderInput={(params) => (
                <TextField
                  {...params}
                  label="Search by Title or ID"
                  variant="outlined"
                  fullWidth
                  margin="normal"
                  InputProps={{
                    ...params.InputProps,
                    endAdornment: (
                      <>
                        {isLoading ? <CircularProgress color="inherit" size={20} /> : null}
                        {params.InputProps.endAdornment}
                      </>
                    ),
                  }}
                />
              )}
              renderOption={(props, option) => (
                <li {...props} key={option.id}>
                  {option.shortTitle || String(option.id)}
                </li>
              )}
            />

            {error && <Alert severity="error">{error}</Alert>}

            {selectedResult && (
              <div className="search-results">
                <div className="search-result-item" key={selectedResult.id}>
                  <h3>{selectedResult.shortTitle}</h3>
                  <p>Topic: {selectedResult.topic}</p>
                  <p>Feedback Count: {selectedResult.totalFeedback}</p>
                  <a href={selectedResult.links} target="_blank" rel="noopener noreferrer">
                    Go to this initiative
                  </a>
                  <div className='summary-button'>
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={() => generateSummary(selectedResult.id)}
                      disabled={isGeneratingSummary}
                    >
                      {isGeneratingSummary ? 'Generating...' : 'Generate Summary'}
                    </Button>
                  </div>
                  {summary && (
                    <div className="summary-result">
                      <p>{summary}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </AccordionDetails>
      </Accordion>

      {/* Snackbar */}
      <Snackbar 
        open={openSnackbar} 
        autoHideDuration={1200} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          Successfully submitted!
        </Alert>
      </Snackbar>
    </div>
  );
}
