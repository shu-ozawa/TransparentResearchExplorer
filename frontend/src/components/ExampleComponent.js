import React from 'react';
import { Button } from '@mui/material';

const ExampleComponent = () => {
  const handleClick = () => {
    alert('Button clicked!');
  };

  return (
    <div>
      <h1>Welcome to the Transparent Research Explorer!</h1>
      <Button variant="contained" color="primary" onClick={handleClick}>
        Click Me
      </Button>
    </div>
  );
};

export default ExampleComponent;
