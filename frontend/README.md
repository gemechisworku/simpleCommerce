# simpleCommerce Frontend

ReactJS frontend application for the simpleCommerce platform.

## Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   ├── atoms/      # Atomic components
│   │   ├── molecules/  # Molecular components
│   │   └── organisms/  # Organism components
│   ├── pages/          # Page components
│   │   ├── customer/   # Customer storefront pages
│   │   ├── admin/      # Admin dashboard pages
│   │   └── auth/       # Authentication pages
│   ├── services/       # API services
│   ├── hooks/          # Custom React hooks
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript types
│   ├── theme/          # Theme configuration
│   └── constants/      # Constants
├── public/             # Static files
├── package.json        # Dependencies
└── tsconfig.json       # TypeScript configuration
```

## Setup

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API URL
   ```

3. **Start development server**
   ```bash
   npm start
   ```

## Available Scripts

- `npm start`: Start development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm run lint`: Run ESLint
- `npm run format`: Format code with Prettier

## Development

### Theme System

The application uses a global theme configuration system. All components should use theme values instead of hardcoded colors/sizes.

Theme configuration is located in `src/theme/`.

### Component Organization

Components follow atomic design principles:
- **Atoms**: Basic building blocks (buttons, inputs, labels)
- **Molecules**: Simple component groups (form fields, product cards)
- **Organisms**: Complex components (headers, forms, lists)
- **Templates**: Page layouts
- **Pages**: Complete pages

### API Integration

API services are located in `src/services/` and use axios for HTTP requests.

## Environment Variables

- `REACT_APP_API_URL`: Backend API URL (default: http://localhost:8000/api/v1)
- `REACT_APP_ENVIRONMENT`: Environment (development/production)

