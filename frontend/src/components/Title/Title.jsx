
import PropTypes from "prop-types";
import React from "react";
import "./style.css";

export const Title = ({ className, property1, text = "Citizen Feedback Enhancer", visible = true }) => {
  if (!visible) return null;

  return (
    <div className={`title ${className}`}>
      <p className={`title-text ${property1}`}>{text}</p>
    </div>
  );
};

Title.propTypes = {
  className: PropTypes.string,
  property1: PropTypes.oneOf(["variant-4", "variant-2", "variant-3", "default"]),
  text: PropTypes.string,
  visible: PropTypes.bool,
};
