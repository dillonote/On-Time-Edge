# On Time Edge

A lightweight edge service for time-sensitive task scheduling and delivery.

## Prerequisites

- [Node.js](https://nodejs.org/) >= 18
- npm >= 9 (ships with Node 18+)

## Setup

```bash
# Clone the repository
git clone https://github.com/dillonote/On-Time-Edge.git
cd On-Time-Edge

# Install dependencies
npm install

# Copy the example environment file and fill in your values
cp .env.example .env
```

## Running locally

```bash
# Start the development server
npm run dev

# Start in production mode
npm start
```

## Testing

```bash
# Run the full test suite
npm test

# Run tests in watch mode
npm run test:watch
```

## Linting & formatting

```bash
# Lint the codebase
npm run lint

# Auto-fix lint issues
npm run lint:fix

# Check formatting
npm run format:check

# Apply formatting
npm run format
```

## Project structure

```
On-Time-Edge/
├── src/            # Application source code
├── tests/          # Test files
├── .env.example    # Example environment variables
├── CLAUDE.md       # AI-assisted development guidance
└── README.md       # This file
```

## Contributing

1. Create a feature branch from `main`.
2. Keep changes small and focused.
3. Add or update tests when behavior changes.
4. Open a pull request with a clear description of what changed and why.

## License

See [LICENSE](LICENSE) for details.
