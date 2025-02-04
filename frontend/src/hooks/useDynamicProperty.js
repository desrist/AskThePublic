// control the dynamic property of the component

import { useState, useEffect } from "react";

const useDynamicProperty = (properties) => {
  const [property, setProperty] = useState(properties[0]);

  useEffect(() => {
    const interval = setInterval(() => {
      setProperty((prev) => {
        const currentIndex = properties.indexOf(prev);
        const nextIndex = (currentIndex + 1) % properties.length;
        return properties[nextIndex];
      });
    }, 2000);

    return () => clearInterval(interval);
  }, [properties]);

  return property;
};

export default useDynamicProperty;
