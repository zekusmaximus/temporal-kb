# Temporal KB Mobile App

A production-ready React Native mobile application for the Temporal Knowledge Base system, built with Expo and TypeScript.

## Features

### Core Functionality
- **Recent Entries**: View your most recently updated entries
- **Search**: Both keyword and semantic search capabilities
- **Entry Management**: Create, read, update, and delete entries
- **Markdown Support**: Rich text rendering for entry content
- **Tags & Projects**: Organize entries with tags and projects
- **Related Entries**: Discover connected knowledge
- **On This Day**: See entries from this day in history
- **Statistics**: Track your knowledge base growth

### User Experience
- **Material Design 3**: Modern, accessible UI components
- **Dark Mode**: Toggle between light and dark themes
- **Pull-to-Refresh**: Update content with a simple gesture
- **Type-Safe Navigation**: Leveraging TypeScript for reliability
- **Form Validation**: React Hook Form integration
- **Offline Configuration**: API settings stored locally

## Tech Stack

- **Framework**: Expo (React Native)
- **Language**: TypeScript with strict mode
- **UI Library**: React Native Paper (Material Design 3)
- **Navigation**: React Navigation v6
- **State Management**: Zustand
- **Forms**: React Hook Form
- **HTTP Client**: Axios
- **Storage**: AsyncStorage
- **Markdown**: react-native-markdown-display
- **Date Utilities**: date-fns

## Project Structure

```
temporal-kb-mobile/
├── src/
│   ├── api/              # API client and requests
│   │   └── client.ts
│   ├── components/       # Reusable UI components
│   │   ├── EntryCard.tsx
│   │   ├── SearchBar.tsx
│   │   ├── LoadingState.tsx
│   │   └── EmptyState.tsx
│   ├── hooks/           # Custom React hooks
│   │   └── useEntries.ts
│   ├── navigation/      # Navigation configuration
│   │   ├── types.ts
│   │   └── AppNavigator.tsx
│   ├── screens/         # App screens
│   │   ├── HomeScreen.tsx
│   │   ├── SearchScreen.tsx
│   │   ├── DiscoverScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   ├── EntryDetailScreen.tsx
│   │   ├── CreateEntryScreen.tsx
│   │   ├── EditEntryScreen.tsx
│   │   └── SettingsScreen.tsx
│   ├── store/           # Zustand state store
│   │   └── index.ts
│   ├── types/           # TypeScript type definitions
│   │   └── index.ts
│   ├── utils/           # Utility functions
│   └── theme/           # Theme configuration
│       └── index.ts
├── assets/              # Images, fonts, etc.
├── App.tsx             # Root component
└── package.json        # Dependencies

```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Expo CLI: `npm install -g expo-cli`
- For iOS: macOS with Xcode (or use Expo Go app)
- For Android: Android Studio (or use Expo Go app)

### Installation

1. Navigate to the mobile app directory:
```bash
cd temporal-kb-mobile
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

4. Run on your platform:
```bash
npm run android  # Android
npm run ios      # iOS (macOS only)
npm run web      # Web browser
```

### Quick Start with Expo Go

1. Install Expo Go on your phone:
   - [iOS App Store](https://apps.apple.com/app/expo-go/id982107779)
   - [Google Play Store](https://play.google.com/store/apps/details?id=host.exp.exponent)

2. Start the dev server: `npm start`

3. Scan the QR code with:
   - **iOS**: Camera app
   - **Android**: Expo Go app

## Configuration

### First Time Setup

1. Launch the app
2. Navigate to the Profile tab → Settings (gear icon)
3. Enter your API configuration:
   - **API URL**: Your Temporal KB server URL (e.g., `http://192.168.1.100:8000`)
   - **API Key**: Your API key from the backend
4. Tap "Test Connection" to verify
5. Tap "Save Configuration"

### API Server Requirements

Your Temporal KB API server must be:
- Running and accessible from your mobile device
- Configured with CORS to allow mobile app requests
- Using the same API key you configured in the app

**Note**: Use your computer's local IP address (not `localhost`) when running the server locally.

## Screens Overview

### Home
- Displays 20 most recent entries
- Pull-to-refresh to update
- Tap entry to view details
- FAB button to create new entry
- Settings access via gear icon

### Search
- **Keyword Mode**: Traditional text search
- **Semantic Mode**: AI-powered semantic search with similarity scores
- Real-time results

### Discover
- **Statistics**: Total entries, words, tags, projects
- **On This Day**: Entries created on this date in history

### Profile
- Personal statistics dashboard
- Tags overview (top 10)
- Projects overview (top 10)
- Quick access to settings

### Entry Detail
- Full markdown rendering
- Metadata (date, word count, type)
- Tags and projects
- Related entries
- Edit/delete actions

### Create/Edit Entry
- Title and content fields
- Entry type selector (note, legal_case, code_snippet, etc.)
- Tag management
- Project management
- Form validation

### Settings
- API URL configuration
- API key management
- Connection testing
- Dark mode toggle
- App version info

## API Integration

The app connects to your Temporal KB API backend using:

```typescript
// Example API calls
apiClient.getRecent(20)              // Get recent entries
apiClient.search("query")            // Keyword search
apiClient.semanticSearch("query")    // Semantic search
apiClient.createEntry(data)          // Create entry
apiClient.updateEntry(id, data)      // Update entry
apiClient.deleteEntry(id)            // Delete entry
apiClient.getRelatedEntries(id)      // Get related entries
apiClient.getOnThisDay()             // Get temporal entries
```

All API calls include:
- Automatic API key injection
- Request/response interceptors
- Error handling
- 30-second timeout

## Development

### Running Tests
```bash
npm test
```

### Type Checking
```bash
npx tsc --noEmit
```

### Linting
```bash
npm run lint
```

### Building for Production

#### Android
```bash
eas build --platform android
```

#### iOS
```bash
eas build --platform ios
```

See [Expo EAS Build](https://docs.expo.dev/build/introduction/) for detailed build instructions.

## Troubleshooting

### Connection Issues

**Problem**: Can't connect to API server

**Solutions**:
1. Verify API URL uses your computer's IP address, not `localhost`
2. Ensure API server is running: `http://YOUR_IP:8000/health`
3. Check firewall settings allow connections
4. Verify API key is correct
5. Use "Test Connection" in Settings

### Cannot Find Module Errors

**Problem**: Import errors or module not found

**Solutions**:
1. Clear cache: `npm start -- --clear`
2. Reinstall dependencies: `rm -rf node_modules && npm install`
3. Reset Metro bundler: `npm start -- --reset-cache`

### Dark Mode Issues

**Problem**: Theme not switching properly

**Solution**: Force close and restart the app

## Contributing

1. Create a feature branch
2. Make your changes
3. Test on both iOS and Android
4. Submit a pull request

## License

Part of the Temporal KB project.

## Support

For issues and questions:
- Check existing GitHub issues
- Create a new issue with:
  - Device/OS version
  - Expo version
  - Steps to reproduce
  - Screenshots if applicable
