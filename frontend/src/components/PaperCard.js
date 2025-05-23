import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Button, Chip, CircularProgress } from '@mui/material';
import apiService from '../services/apiService';

const dummyPaper = {
  title: "A Dummy Paper Title",
  authors: ["John Doe", "Jane Smith"],
  date: "2023/10/05",
  abstract:
    "This is a dummy abstract for the paper. It should provide a brief summary of what the research is about...",
  relevanceScore: null, // out of 5
  categories: ["cs.AI", "cs.LG"],
};

const PaperCard = ({ paper, query }) => {
  const { title, authors, date, abstract, relevanceScore, categories } = paper;
  const [score, setScore] = useState(relevanceScore);
  const [loading, setLoading] = useState(!relevanceScore);

  // Fetch score if not already provided
  useEffect(() => {
    if (!relevanceScore && query) {
      setLoading(true);
      apiService.getPaperScore(paper, query)
        .then(response => {
          const scoreValue = Math.round(response.score * 5); // Convert 0-1 scale to 0-5
          setScore(scoreValue);
          setLoading(false);
        })
        .catch(error => {
          console.error("Error fetching paper score:", error);
          setLoading(false);
        });
    }
  }, [paper, query, relevanceScore]);

  return (
    <Card sx={{ maxWidth: 345, margin: 2 }}>
      <CardContent>
        <Typography variant="h6" component="div">
          {title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {authors.join(", ")} ({date})
        </Typography>

        <Typography variant="body2" color="text.secondary" paragraph>
          {abstract.split('\n')[0]}
        </Typography>

        {/* Relevance score with text */}
        <div style={{ display: 'flex', alignItems: 'center' }}>
          {loading ? (
            <CircularProgress size={16} />
          ) : (
            `Relevance: ${score !== null ? `${score}/5` : 'N/A'}`
          )}
        </div>

        {/* Categories */}
        {categories && categories.map((category, index) => (
          <Chip
            key={index}
            label={category}
            size="small"
            style={{ marginRight: 4, marginTop: 8 }}
          />
        ))}

        {/* Action buttons */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 16 }}>
          <Button size="small">Details</Button>
          <Button size="small" color="primary">
            Select
          </Button>
          <Button size="small">PDF</Button>
        </div>
      </CardContent>
    </Card>
  );
};

// For testing purposes, export a component that uses the dummy data
const PaperCardWithDummyData = () => (
  <PaperCard paper={dummyPaper} query="dummy query" />
);

export default PaperCard;
export { PaperCardWithDummyData };
