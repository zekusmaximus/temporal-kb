import React, { useEffect, useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Appbar, Card, Text, List, Divider } from 'react-native-paper';
import { CompositeScreenProps } from '@react-navigation/native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';

import { RootStackParamList, MainTabParamList } from '../navigation/types';
import { LoadingState } from '../components/LoadingState';
import { apiClient } from '../api/client';
import { spacing } from '../theme';

type Props = CompositeScreenProps<
  BottomTabScreenProps<MainTabParamList, 'Profile'>,
  NativeStackScreenProps<RootStackParamList>
>;

export const ProfileScreen: React.FC<Props> = ({ navigation }) => {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const [tags, setTags] = useState<string[]>([]);
  const [projects, setProjects] = useState<string[]>([]);

  useEffect(() => {
    loadProfileData();
  }, []);

  const loadProfileData = async () => {
    try {
      setLoading(true);
      const [statsData, tagsData, projectsData] = await Promise.all([
        apiClient.getStats(),
        apiClient.getTags(),
        apiClient.getProjects(),
      ]);
      setStats(statsData);
      setTags(tagsData);
      setProjects(projectsData);
    } catch (error) {
      console.error('Failed to load profile data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSettingsPress = () => {
    navigation.navigate('Settings');
  };

  if (loading) {
    return <LoadingState message="Loading profile..." />;
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Profile" />
        <Appbar.Action icon="cog" onPress={handleSettingsPress} />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        {stats && (
          <Card style={styles.card}>
            <Card.Title title="Statistics" />
            <Card.Content>
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text variant="displaySmall">{stats.total_entries}</Text>
                  <Text variant="bodyMedium">Entries</Text>
                </View>
                <View style={styles.statItem}>
                  <Text variant="displaySmall">{stats.total_words.toLocaleString()}</Text>
                  <Text variant="bodyMedium">Words</Text>
                </View>
              </View>
              <Divider style={styles.divider} />
              <View style={styles.statsRow}>
                <View style={styles.statItem}>
                  <Text variant="displaySmall">{stats.total_tags}</Text>
                  <Text variant="bodyMedium">Tags</Text>
                </View>
                <View style={styles.statItem}>
                  <Text variant="displaySmall">{stats.total_projects}</Text>
                  <Text variant="bodyMedium">Projects</Text>
                </View>
              </View>
            </Card.Content>
          </Card>
        )}

        <Card style={styles.card}>
          <Card.Title title="Tags" subtitle={`${tags.length} total`} />
          <Card.Content>
            {tags.slice(0, 10).map((tag) => (
              <List.Item
                key={tag}
                title={tag}
                left={(props) => <List.Icon {...props} icon="tag" />}
              />
            ))}
            {tags.length > 10 && (
              <Text variant="bodySmall" style={styles.moreText}>
                +{tags.length - 10} more tags
              </Text>
            )}
          </Card.Content>
        </Card>

        <Card style={styles.card}>
          <Card.Title title="Projects" subtitle={`${projects.length} total`} />
          <Card.Content>
            {projects.slice(0, 10).map((project) => (
              <List.Item
                key={project}
                title={project}
                left={(props) => <List.Icon {...props} icon="folder" />}
              />
            ))}
            {projects.length > 10 && (
              <Text variant="bodySmall" style={styles.moreText}>
                +{projects.length - 10} more projects
              </Text>
            )}
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
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: spacing.md,
  },
  statItem: {
    alignItems: 'center',
  },
  divider: {
    marginVertical: spacing.sm,
  },
  moreText: {
    textAlign: 'center',
    color: '#666',
    marginTop: spacing.sm,
  },
});
