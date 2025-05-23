# Frontend Documentation

This document provides an overview of the frontend architecture, components, state management, API interactions, and data flow for the Transparent Research Explorer application.

## Overall Architecture

The frontend is built using React. The main entry point for the application is `frontend/src/App.js`.

-   **`App.js`**: This file sets up the main application structure. It defines the overall layout by rendering common components like `Header`, `MainContent`, and `Footer`. It also wraps the entire application with `AppProvider` from `frontend/src/contexts/AppContext.js`, which makes global state accessible to all nested components.
-   **`frontend/src/pages/HomePage.js`**: This is the primary page of the application. It orchestrates the core user-facing functionalities, including the form for keyword input, triggering query generation, and displaying the query tree visualization.

## Components

The reusable UI elements of the application are organized into components, primarily located in the `frontend/src/components/` directory.

-   **`QueryInputForm.js`**: This component renders a form where users can input their initial keywords or research theme. Upon submission, it calls an `onSubmit` handler (provided by its parent, `HomePage.js`) with the entered keywords.
-   **`PaperCard.js`**: This component is designed to display detailed information about a research paper in a card format. It expects a `paper` object as a prop, containing details like title, authors, abstract, relevance score, and categories. It also includes action buttons (e.g., "Details", "Select", "PDF").
    -   *Note*: Currently, `HomePage.js` includes `PaperCardWithDummyData`, a helper exported from `PaperCard.js`, which renders the `PaperCard` with predefined dummy data. This suggests its intended use is to display actual paper data fetched from the backend in response to user queries or interactions.
-   **`QueryTreeVisualizer.js`**: This component is responsible for rendering a hierarchical query tree structure. It uses the D3.js library to create an interactive SVG visualization. It accepts `data` (the tree structure) as a prop and provides zoom functionality.
-   **Layout Components**:
    -   **`Header.js`**: Renders the application header, typically containing the application title or branding.
    -   **`Footer.js`**: Renders the application footer, often used for copyright information or secondary links.
    -   **`MainContent.js`**: A wrapper component that encloses the main content area of any given page, ensuring consistent layout.
-   **`ExampleComponent.js`**: This component appears to be a placeholder or a component used for initial development and testing, possibly for verifying Material UI integration. It includes a simple button with an alert action. It might not be part of the core production functionality.

## State Management

The application employs a combination of global and local state management.

-   **`AppContext.js` (`frontend/src/contexts/AppContext.js`)**:
    -   This file defines `AppContext` and `AppProvider` using React's Context API for global state management.
    -   `AppProvider` initializes a `data` state variable and a `setData` function to update it.
    -   **Intended Use**: The `AppContext` is designed to hold data that needs to be shared across various components without explicit prop drilling (e.g., user authentication status, application-wide settings, or perhaps globally accessible query results).
    -   **Current Integration**: While `AppProvider` wraps the application in `App.js`, the global `data` state it provides does not appear to be actively used by the reviewed components in their current implementation. The infrastructure is in place for future use.
-   **Local Component State (`useState`)**:
    -   Individual components manage their own internal state using the `useState` hook.
    -   For example, `QueryInputForm.js` uses `useState` to manage the value of the keyword input field (`initialKeywords`).
    -   `HomePage.js` uses `useState` to store and manage `queryTreeData` that is fetched from the API and passed to the `QueryTreeVisualizer`.

## API Interaction

All communication with the backend server is centralized within the `frontend/src/services/apiService.js` module.

-   **`apiService.js`**: This service exports an object containing methods for making API calls.
    -   **`generateQuery(initialKeywords)`**:
        -   Sends a `POST` request to the `/api/generate` endpoint.
        -   The request body includes the `{ initial_keywords: initialKeywords }`.
        -   **Purpose**: This function is used to submit the user's research theme/keywords to the backend, which then processes them to generate a main query and potentially related sub-queries or search results.
    -   **`fetchQueryTreeData()`**:
        -   Sends a `GET` request to the `/api/queries/tree` endpoint.
        -   **Purpose**: This function is used to fetch the hierarchical data structure representing the relationships between queries (e.g., an initial query and its refined versions or related concepts). This data is then used by the `QueryTreeVisualizer` component.
    -   The service also includes a generic `fetchData(endpoint)` function and basic error handling for network responses.

## Data Flow

The following describes the typical sequence of operations and data movement within the frontend:

1.  **Keyword Input**:
    -   The user types their research keywords into the `QueryInputForm` rendered on `HomePage.js`.
2.  **Query Generation Request**:
    -   Upon submitting the form, the `onSubmit` handler in `QueryInputForm` calls the `handleKeywordsSubmit` function in `HomePage.js`.
    -   `handleKeywordsSubmit` then invokes `apiService.generateQuery()` with the provided keywords.
3.  **Handling `generateQuery` Results**:
    -   The backend processes the request and returns a response (e.g., containing the original query and a list of related queries).
    -   **Current Handling**: In the current implementation in `HomePage.js`, the result from `generateQuery` is logged to the console and displayed to the user via a browser `alert()`.
    -   **Intended Use**: It's likely that the intended use for this data is to update the application state, perhaps displaying the generated queries more effectively in the UI, potentially populating a list of research papers (using `PaperCard`), or updating the `QueryTreeVisualizer`.
4.  **Fetching Query Tree Data**:
    -   `HomePage.js` contains a button ("Load Query Tree"). When clicked, it triggers the `loadQueryTreeData` function.
    -   `loadQueryTreeData` calls `apiService.fetchQueryTreeData()`.
5.  **Visualizing Query Tree**:
    -   The data returned from `apiService.fetchQueryTreeData()` (which should be a hierarchical JSON object) is stored in the `queryTreeData` state variable within `HomePage.js`.
    -   This `queryTreeData` is then passed as a prop to the `QueryTreeVisualizer.js` component.
    -   `QueryTreeVisualizer` uses D3.js to render this data as an interactive tree diagram.
6.  **Displaying Paper Information**:
    -   The `PaperCard.js` component is designed to show details of individual research papers.
    -   Currently, it's demonstrated on `HomePage.js` using `PaperCardWithDummyData`, which uses static, hardcoded paper information.
    -   **Intended Purpose**: In a fully functional application, paper data would likely be fetched from the backend (possibly as part of the `generateQuery` response or through separate API calls based on user interaction with queries) and then dynamically rendered using multiple instances of the `PaperCard` component.
---
