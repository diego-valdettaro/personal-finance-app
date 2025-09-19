# Personal Finance Frontend

A modern, responsive React application for personal finance management built with TypeScript, Vite, and Tailwind CSS.

## Features

- 🏠 **Dashboard** - Overview of financial health with key metrics
- 💳 **Transactions** - Manage and track all financial transactions
- 📊 **Budgets** - Set and monitor spending budgets
- 📈 **Reports** - Visualize financial data with charts and analytics
- ⚙️ **Settings** - Customize preferences and manage accounts

## Tech Stack

- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom design tokens
- **UI Components**: shadcn/ui + Radix primitives
- **State Management**: Zustand + TanStack Query
- **Charts**: Recharts
- **Icons**: Lucide React
- **Testing**: Vitest + React Testing Library
- **Routing**: React Router DOM

## Getting Started

### Prerequisites

- Node.js 20.17.0 or higher
- npm or yarn package manager

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Update environment variables in `.env`:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_AUTH_STRATEGY=bearer
```

### Development

Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

### Building

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

### Testing

Run tests:
```bash
npm test
```

Run tests with UI:
```bash
npm test:ui
```

Run tests once:
```bash
npm run test:run
```

## Architecture

### Backend-First Design

This frontend is designed to work with any backend API by:

1. **Dynamic Discovery**: Automatically detects backend schema via OpenAPI/Swagger or response sampling
2. **Adapter Layer**: Translates backend responses to UI-friendly formats
3. **Type Safety**: Generates TypeScript types from backend responses
4. **Progressive Enhancement**: Works with partial data and gracefully handles missing features

### Key Components

- **AppShell**: Main layout with sidebar navigation and header
- **Pages**: Dashboard, Transactions, Budgets, Reports, Settings
- **UI Components**: Reusable components built with shadcn/ui
- **Adapters**: Backend integration layer in `lib/adapters/`
- **API Client**: HTTP client with retry logic and error handling
- **Store**: Global state management with Zustand

### Styling

- **Design System**: Custom CSS variables for consistent theming
- **Dark Mode**: Default dark theme with light mode toggle
- **Responsive**: Mobile-first design with responsive breakpoints
- **Accessibility**: WCAG AA compliant with keyboard navigation

## Configuration

### Environment Variables

- `VITE_API_BASE_URL`: Backend API base URL
- `VITE_AUTH_STRATEGY`: Authentication strategy (bearer|cookie|none)
- `VITE_FEATURE_FLAGS`: JSON object for feature toggles

### Customization

- **Theme**: Modify CSS variables in `src/index.css`
- **Components**: Add new UI components in `src/components/ui/`
- **Pages**: Create new pages in `src/pages/`
- **Adapters**: Extend backend integration in `src/lib/adapters/`

## Backend Integration

The frontend automatically adapts to your backend by:

1. **Schema Discovery**: Detects available endpoints and data structures
2. **Field Mapping**: Maps backend field names to UI-friendly names
3. **Type Generation**: Creates TypeScript types from backend responses
4. **Error Handling**: Gracefully handles API errors and missing data

### Supported Backend Features

- REST API endpoints
- Pagination (page-based, cursor-based, or offset-based)
- Filtering and sorting
- Authentication (Bearer tokens, cookies, or custom headers)
- File uploads (CSV import)
- Real-time updates (if supported)

## Development Guidelines

### Code Style

- Use TypeScript for all new code
- Follow React best practices and hooks patterns
- Use Tailwind CSS for styling
- Write tests for new components
- Use semantic commit messages

### Component Structure

```tsx
// Component file structure
export function ComponentName() {
  // Hooks
  // State
  // Effects
  // Handlers
  // Render
}
```

### API Integration

```tsx
// Use adapters for all API calls
const { data, isLoading, error } = useQuery({
  queryKey: queryKeys.resource.list(filters),
  queryFn: () => adapters.resource.list(filters),
})
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License.