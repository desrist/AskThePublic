import React, {useEffect} from 'react';
import Rating from '@mui/material/Rating';
import Tooltip from '@mui/material/Tooltip';
import './style.css';


const RatingContainer = ({ scores }) => {
  if (!scores) {
    return <div>No scores available</div>;
  }

  // Convert score to stars: each 2 points corresponds to 1 star
  const scoreToStars = (score) => Math.max(0, Math.round(score / 2));

  return (
    <div className="rating-container">
      {/* Box for Question-Answer Relevance */}
      <Tooltip title="This score represents how well the answer matches the question." placement="top" arrow>
        <div className="rating-box">
            <div className="rating-title">Question-Answer Relevance</div>
            <Rating name="qa-relevance" value={scoreToStars(scores.question_answer_relevance)} readOnly />
        </div>
      </Tooltip>

      {/* Box for Question-Source Relevance */}
      <Tooltip title="This score shows how relevant the source data is to the question." placement="top" arrow>
        <div className="rating-box">
          <div className="rating-title">Question-Source Relevance</div>
          <Rating name="qs-relevance" value={scoreToStars(scores.question_source_relevance)} readOnly />
        </div>
      </Tooltip>

      {/* Box for Answer-Source Alignment */}
      <Tooltip title="This score evaluates how well the answer aligns with the source data." placement="top" arrow>
        <div className="rating-box">
          <div className="rating-title">Answer-Source Alignment</div>
          <Rating name="as-alignment" value={scoreToStars(scores.answer_source_alignment)} readOnly />
        </div>
      </Tooltip>
    </div>
  );
};

export default RatingContainer;
