# NovaSystem Frontend

This is the SvelteKit-based frontend for the NovaSystem project.

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start the development server
npm run dev -- --open
```

## Project Structure

- `src/routes/` - SvelteKit routes
- `src/components/` - Reusable UI components
- `src/lib/` - Utility functions, types, and shared logic
- `src/stores/` - Svelte stores for state management

## Key Features

- **Chat Interface** - Conversational UI for interacting with agents
- **Visualizations** - Data visualization for insights
- **Process Templates** - Predefined process templates
- **Session Management** - Session persistence and history

## Backend Integration

The frontend communicates with the NovaSystem backend API, which should be running at `http://localhost:8000` by default. You can change the API URL in the environment variables.

## Technologies Used

- [SvelteKit](https://kit.svelte.dev/) - Frontend framework
- [TailwindCSS](https://tailwindcss.com/) - CSS framework
- [Chart.js](https://www.chartjs.org/) - Visualization library
- [Axios](https://axios-http.com/) - HTTP client

## Development

### Running Tests

```bash
npm run test
```

### Building for Production

```bash
npm run build
```

### Code Style

We use Prettier and ESLint to maintain code quality:

```bash
# Check formatting
npm run lint

# Fix formatting issues
npm run format
```

## Contributing

Please follow the project's coding standards and submit pull requests to the main repository.