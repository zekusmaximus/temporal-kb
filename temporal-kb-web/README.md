# Temporal Knowledge Base - Desktop Web UI

A minimalist desktop web interface for Temporal Knowledge Base, inspired by early Wikipedia design principles.

## Features

- **Clean, minimalist design** - Focused on content with simple, readable typography
- **Full knowledge base management** - Create, edit, search, and organize entries
- **Advanced search** - Keyword, semantic, and hybrid search modes
- **Temporal features** - Timeline view and "On This Day" retrospectives
- **Knowledge discovery** - Explore connections and relationships between entries
- **Responsive design** - Works on desktop and tablet devices
- **Markdown support** - Write entries with Markdown formatting

## Technology Stack

- **React 18** - Modern UI library
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server
- **React Router** - Client-side routing
- **Axios** - API communication
- **marked** - Markdown rendering
- **DOMPurify** - XSS protection for rendered content

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Temporal KB backend API running (default: http://localhost:8000)

### Installation

```bash
cd temporal-kb-web
npm install
```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at http://localhost:3000

### Building for Production

```bash
npm run build
```

The production build will be in the `dist` directory.

### Preview Production Build

```bash
npm run preview
```

## Configuration

The web UI connects to the backend API via proxy configuration in `vite.config.ts`. By default, it proxies `/api` requests to `http://localhost:8000`.

To connect to a different backend:

1. Edit `vite.config.ts` and change the proxy target
2. Or set up a reverse proxy in production

## Design Philosophy

This UI embraces the minimalist aesthetic of early Wikipedia (circa 2001-2005):

- **Serif fonts** - Linux Libertine and Georgia for readability
- **Simple layouts** - Clean, structured content presentation
- **Minimal color** - Focus on black text on white background
- **Classic elements** - Underlined links, simple borders, clean typography
- **Content-first** - Functionality over decoration

## Project Structure

```
temporal-kb-web/
├── src/
│   ├── api/           # API client
│   ├── components/    # Reusable components
│   ├── pages/         # Page components
│   ├── types/         # TypeScript types
│   ├── App.tsx        # Main app component
│   ├── main.tsx       # Entry point
│   └── index.css      # Global styles
├── public/            # Static assets
├── index.html         # HTML template
└── vite.config.ts     # Vite configuration
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format code with Prettier

## Pages

- **Home** - Dashboard with recent entries and statistics
- **Search** - Advanced search with multiple modes
- **Entry View** - Read entries with related content
- **Create/Edit** - Form for creating and editing entries
- **Timeline** - Temporal view of events and "On This Day"
- **Discover** - Explore connections between entries

## Browser Support

Modern browsers with ES2020 support:
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## License

Same as the main Temporal KB project
