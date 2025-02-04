import { useState, useCallback } from 'react';

const useDrawer = () => {
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleDrawerOpen = useCallback(() => {
    setDrawerOpen(true);
  }, []);

  const handleDrawerClose = useCallback(() => {
    setDrawerOpen(false);
  }, []);

  const toggleDrawer = useCallback(() => {
    setDrawerOpen((prev) => !prev);
  }, []);

  return {
    drawerOpen,
    handleDrawerOpen,
    handleDrawerClose,
    toggleDrawer,
  };
};

export default useDrawer;
