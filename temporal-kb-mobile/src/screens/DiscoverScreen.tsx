import React, { useEffect, useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Appbar, Card, Text, Button } from 'react-native-paper';
import { CompositeScreenProps } from '@react-navigation/native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';
import { format } from 'date-fns';

import { RootStackParamList, MainTabParamList } from '../navigation/types';
import { LoadingState } from '../components/LoadingState';
import { apiClient } from '../api/client';
import { Entry } from '../types';
import { spacing } from '../theme';

type Props = CompositeScreenProps<
  BottomTabScreenProps<MainTabParamList, 'Discover'>,
  NativeStackScreenProps<RootStackParamList>
>;

export const DiscoverScreen: React.FC<Props> = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [onThisDayEntries, setOnThisDayEntries] = useState<Entry[]>([]);
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    loadDiscoverData();
  }, []);

  const loadDiscoverData = async () => {
    try {
      setLoading(true);
      const [onThisDay, statsData] = await Promise.all([
        apiClient.getOnThisDay(),
        apiClient.getStats(),
      ]);
      setOnThisDayEntries(onThisDay);
      setStats(statsData);
    } catch (error) {
      console.error('Failed to load discover data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEntryPress = (entryId: string) => {
    navigation.navigate('EntryDetail', { entryId });
  };

  if (loading) {
    return <LoadingState message="Loading insights..." />;
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Discover" />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {stats && (
          <Card style={styles.card}>
            <Card.Title title="Your Knowledge Base" />
            <Card.Content>
              <View style={styles.statsGrid}>
                <View style={styles.statItem}>
                  <Text variant="headlineMedium">{stats.total_entries}</Text>
                  <Text variant="bodySmall">Entries</Text>
                </View>
                <View style={styles.statItem}>
                  <Text variant="headlineMedium">{Math.round(stats.total_words / 1000)}k</Text>
                  <Text variant="bodySmall">Words</Text>
                </View>
                <View style={styles.statItem}>
                  <Text variant="headlineMedium">{stats.total_tags}</Text>
                  <Text variant="bodySmall">Tags</Text>
                </View>
                <View style={styles.statItem}>
                  <Text variant="headlineMedium">{stats.total_projects}</Text>
                  <Text variant="bodySmall">Projects</Text>
                </View>
              </View>
            </Card.Content>
          </Card>
        )}

        {onThisDayEntries.length > 0 && (
          <Card style={styles.card}>
            <Card.Title
              title="On This Day"
              subtitle={format(new Date(), 'MMMM d')}
            />
            <Card.Content>
              {onThisDayEntries.map((entry) => (
                <Button
                  key={entry.id}
                  mode="outlined"
                  style={styles.entryButton}
                  onPress={() => handleEntryPress(entry.id)}
                >
                  {entry.title}
                </Button>
              ))}
            </Card.Content>
          </Card>
        )}
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
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.lg,
  },
  statItem: {
    alignItems: 'center',
    minWidth: 80,
  },
  entryButton: {
    marginBottom: spacing.sm,
  },
});
