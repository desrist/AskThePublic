

import PropTypes from "prop-types";
import React from "react";

export const AiIcon = ({ color = "url(#paint0_linear_8_119)", className }) => {
  return (
    <svg
      className={`ai-icon ${className}`}
      fill="none"
      height="22"
      viewBox="0 0 22 22"
      width="22"
      xmlns="http://www.w3.org/2000/svg"
    >
      <g className="g" clipPath="url(#clip0_8_232)">
        <path
          className="path"
          d="M8 3L10.5 8.5L16 11L10.5 13.5L8 19L5.5 13.5L0 11L5.5 8.5L8 3ZM8 7.83L7 10L4.83 11L7 12L8 14.17L9 12L11.17 11L9 10L8 7.83ZM18 8L16.74 5.26L14 4L16.74 2.75L18 0L19.25 2.75L22 4L19.25 5.26L18 8ZM18 22L16.74 19.26L14 18L16.74 16.75L18 14L19.25 16.75L22 18L19.25 19.26L18 22Z"
          fill={color}
        />
      </g>
      <defs className="defs">
        <linearGradient
          className="linear-gradient"
          gradientUnits="userSpaceOnUse"
          id="paint0_linear_8_232"
          x1="0"
          x2="26.5261"
          y1="0"
          y2="10.0304"
        >
          <stop className="stop" offset="0.158668" stopColor="#15C7FF" />
          <stop className="stop" offset="0.60652" stopColor="#474FFF" />
          <stop className="stop" offset="0.891362" stopColor="#0015D2" />
        </linearGradient>
        <clipPath className="clip-path" id="clip0_8_232">
          <rect className="rect" fill="white" height="22" width="22" />
        </clipPath>
      </defs>
    </svg>
  );
};

AiIcon.propTypes = {
  color: PropTypes.string,
};
