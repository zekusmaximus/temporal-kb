import React, { useState, useEffect } from 'react';
import { View, ScrollView, StyleSheet, Alert } from 'react-native';
import { Appbar, TextInput, Button, Card, Switch, List, Divider } from 'react-native-paper';
import { NativeStackScreenProps } from '@react-navigation/native-stack';

import { RootStackParamList } from '../navigation/types';
import { apiClient } from '../api/client';
import { useStore } from '../store';
import { spacing } from '../theme';

type Props = NativeStackScreenProps<RootStackParamList, 'Settings'>;

export const SettingsScreen: React.FC<Props> = ({ navigation }) => {
  const { isDarkMode, toggleDarkMode } = useStore();
  const [apiUrl, setApiUrl] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    const config = await apiClient.getConfig();
    setApiUrl(config.baseUrl);
    setApiKey(config.apiKey);
  };

  const handleSave = async () => {
    if (!apiUrl.trim()) {
      Alert.alert('Error', 'API URL is required');
      return;
    }

    if (!apiKey.trim()) {
      Alert.alert('Error', 'API Key is required');
      return;
    }

    try {
      setSaving(true);
      await apiClient.setConfig(apiUrl.trim(), apiKey.trim());
      Alert.alert('Success', 'Settings saved successfully');
    } catch (error) {
      console.error('Failed to save settings:', error);
      Alert.alert('Error', 'Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    if (!apiUrl.trim() || !apiKey.trim()) {
      Alert.alert('Error', 'Please configure API URL and API Key first');
      return;
    }

    try {
      setTesting(true);
      await apiClient.setConfig(apiUrl.trim(), apiKey.trim());
      const response = await apiClient.healthCheck();
      Alert.alert('Success', 'Connection successful!');
    } catch (error: any) {
      console.error('Connection test failed:', error);
      Alert.alert(
        'Connection Failed',
        error.message || 'Could not connect to the API. Please check your settings.'
      );
    } finally {
      setTesting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Settings" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        <Card style={styles.card}>
          <Card.Title title="API Configuration" />
          <Card.Content>
            <TextInput
              label="API URL"
              value={apiUrl}
              onChangeText={setApiUrl}
              placeholder="http://localhost:8000"
              mode="outlined"
              style={styles.input}
              autoCapitalize="none"
              autoCorrect={false}
            />

            <TextInput
              label="API Key"
              value={apiKey}
              onChangeText={setApiKey}
              placeholder="your-api-key"
              mode="outlined"
              style={styles.input}
              autoCapitalize="none"
              autoCorrect={false}
              secureTextEntry
            />

            <Button
              mode="contained"
              onPress={handleSave}
              loading={saving}
              disabled={saving || testing}
              style={styles.button}
            >
              Save Configuration
            </Button>

            <Button
              mode="outlined"
              onPress={handleTestConnection}
              loading={testing}
              disabled={saving || testing}
              style={styles.button}
            >
              Test Connection
            </Button>
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Appearance" />
          <Card.Content>
            <List.Item
              title="Dark Mode"
              description="Switch between light and dark themes"
              left={(props) => <List.Icon {...props} icon="theme-light-dark" />}
              right={() => (
                <Switch value={isDarkMode} onValueChange={toggleDarkMode} />
              )}
            />
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="About" />
          <Card.Content>
            <List.Item
              title="Version"
              description="1.0.0"
              left={(props) => <List.Icon {...props} icon="information" />}
            />
            <Divider />
            <List.Item
              title="Temporal KB"
              description="Your personal knowledge management system"
              left={(props) => <List.Icon {...props} icon="book-open-variant" />}
            />
          </Card.Content>
        </Card>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  card: {
    marginBottom: spacing.md,
  },
  input: {
    marginBottom: spacing.md,
  },
  button: {
    marginTop: spacing.sm,
  },
});
