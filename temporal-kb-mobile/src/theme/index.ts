import { MD3LightTheme, MD3DarkTheme } from 'react-native-paper';

export const lightTheme = {
  ...MD3LightTheme,
  colors: {
    ...MD3LightTheme.colors,
    primary: '#6200ee',
    secondary: '#03dac6',
    tertiary: '#018786',
    background: '#ffffff',
    surface: '#ffffff',
    error: '#b00020',
  },
};

export const darkTheme = {
  ...MD3DarkTheme,
  colors: {
    ...MD3DarkTheme.colors,
    primary: '#bb86fc',
    secondary: '#03dac6',
    tertiary: '#03dac6',
    background: '#121212',
    surface: '#1e1e1e',
    error: '#cf6679',
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
};

export const colors = {
  text: {
    primary: '#000000',
    secondary: '#666666',
    tertiary: '#999999',
  },
  code: {
    background: '#f5f5f5',
  },
  dark: {
    text: {
      primary: '#FFFFFF',
      secondary: '#AAAAAA',
      tertiary: '#888888',
    },
    code: {
      background: '#2a2a2a',
    },
  },
};
