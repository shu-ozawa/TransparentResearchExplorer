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
  const { title, authors, date, abstract, categories } = paper; // relevanceScore removed from destructuring here as we refer to paper.relevanceScore directly

  const initialScore = typeof paper.relevanceScore === 'number'
    ? Math.round(paper.relevanceScore * 5)
    : null;
  const [score, setScore] = useState(initialScore);
  const [loading, setLoading] = useState(typeof paper.relevanceScore !== 'number');

  // Fetch score if not already provided, or update if prop changes
  useEffect(() => {
    // Check if relevanceScore from props is null or undefined
    if (typeof paper.relevanceScore !== 'number' && query) {
      setLoading(true);
      apiService.getPaperScore(paper, query) // paper object passed to API
        .then(response => {
          const scoreValue = Math.round(response.score * 5); // API returns 0-1, scale to 0-5
          setScore(scoreValue);
          setLoading(false);
        })
        .catch(error => {
          console.error("Error fetching paper score:", error);
          setScore(null); // Set score to null on error
          setLoading(false);
        });
    } else if (typeof paper.relevanceScore === 'number' && score !== Math.round(paper.relevanceScore * 5)) {
      // This handles the case where props update, ensuring the displayed score reflects the prop.
      // Also useful if initialScore was null but then paper.relevanceScore becomes available from props later.
      setScore(Math.round(paper.relevanceScore * 5));
      setLoading(false); // Ensure loading is false if score is provided
    } else if (typeof paper.relevanceScore === 'number' && loading) {
      // If score was provided initially but loading was true for some reason, set loading to false.
      setLoading(false);
    }
  }, [paper, paper.relevanceScore, query, score, loading]); // Added paper.relevanceScore and loading to dependency array

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
