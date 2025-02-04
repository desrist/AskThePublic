import React from "react";
import { MenuItem, MenuList } from "@mui/material";
import { styled } from "@mui/system";

const CustomMenuList = styled(MenuList)({
  height: "100px",
  width: "500px",
  display: "flex",
  alignItems: "center",
  justifyContent: "space-around",
  margin: "0 auto",
  padding: "10px",
  flexDirection: "row",
  backgroundColor: "var(--color-gray-200)",
  color: "gray",
});

const CustomMenuItem = styled(MenuItem)({
  margin: "0 10px",
  padding: "20px",
  textDecoration: "none",
  "&:hover": {
    backgroundColor: "var(--color-gray-300)",
    borderRadius: "50px"
  }
});

const NaviContainer = ({ handleClose }) => {
  return (
    <CustomMenuList>
      <CustomMenuItem onClick={handleClose}>Option 1</CustomMenuItem>
      <CustomMenuItem onClick={handleClose}>Option 2</CustomMenuItem>
      <CustomMenuItem onClick={handleClose}>Option 3</CustomMenuItem>
    </CustomMenuList>
  );
};

export default NaviContainer;