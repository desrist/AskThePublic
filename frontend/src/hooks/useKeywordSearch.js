import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import debounce from 'lodash/debounce';

function useKeywordSearch() {
  const [keyword, setKeyword] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedResult, setSelectedResult] = useState(null);
  const [summary, setSummary] = useState(null);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);

  const handleKeywordChange = (newValue) => {
    setKeyword(newValue);
  };
  const BASE_URL = "http://18.156.85.182:8080";

  // api for searching keywords
  const handleKeywordSearch = useCallback(async () => {
    if (!keyword.trim()) {
      setError('Please enter a keyword to search.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.get(
        `${BASE_URL}/search_keywords`, 
        { params: { keyword } }
      );
      setSearchResults(response.data);

      if (response.data.length === 0) {
        setError('No matching documents found.');
        setTimeout(() => {
          setError(null);
        }, 2000); // 2 seconds delay before clearing the error message
      }

    } catch (error) {
      console.error("Error fetching search results:", error);
      setError(error.response?.data?.detail || error.message || 'An error occurred');
      setTimeout(() => {
        setError(null);
      }, 2000); // 2 seconds delay before clearing the error message
    } finally {
      setIsLoading(false);
    }
  }, [keyword]);

  // api for generate summary
  const generateSummary = useCallback(async (initiative_id) => {
    setIsGeneratingSummary(true);
    setSummary(null);
    try {
      const response = await axios.post(
        `${BASE_URL}/generate_summary/${initiative_id}`
      );
      setSummary(response.data.summary);
    } catch (error) {
      console.error("Error generating summary:", error);
      setSummary('Failed to generate summary.');
    } finally {
      setIsGeneratingSummary(false);
    }
  }, []);

  const debouncedSearch = useCallback(debounce(handleKeywordSearch, 1000), [handleKeywordSearch]);

  useEffect(() => {
    if (keyword.trim()) {
      debouncedSearch();
    }
    return () => {
      debouncedSearch.cancel();
    };
  }, [keyword, debouncedSearch]);

  useEffect(() => {
    if (selectedResult) {
      setKeyword(selectedResult.shortTitle || String(selectedResult.id));
    }
  }, [selectedResult]);

  return {
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
    setSummary,
  };
}

export default useKeywordSearch;
