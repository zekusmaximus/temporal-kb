import React, { useEffect, useState } from 'react';
import { View, FlatList, StyleSheet, RefreshControl } from 'react-native';
import { Appbar, FAB } from 'react-native-paper';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { CompositeScreenProps } from '@react-navigation/native';
import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';

import { RootStackParamList, MainTabParamList } from '../navigation/types';
import { EntryCard } from '../components/EntryCard';
import { LoadingState } from '../components/LoadingState';
import { EmptyState } from '../components/EmptyState';
import { useEntries } from '../hooks/useEntries';
import { useStore } from '../store';
import { spacing } from '../theme';

type Props = CompositeScreenProps<
  BottomTabScreenProps<MainTabParamList, 'Home'>,
  NativeStackScreenProps<RootStackParamList>
>;

export const HomeScreen: React.FC<Props> = ({ navigation }) => {
  const { entries, isLoading } = useStore();
  const { loadRecent, error } = useEntries();
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadInitial();
  }, []);

  const loadInitial = async () => {
    try {
      await loadRecent(20);
    } catch (err) {
      console.error('Failed to load entries:', err);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadInitial();
    setRefreshing(false);
  };

  const handleEntryPress = (entryId: string) => {
    navigation.navigate('EntryDetail', { entryId });
  };

  const handleCreatePress = () => {
    navigation.navigate('CreateEntry');
  };

  const handleSettingsPress = () => {
    navigation.navigate('Settings');
  };

  if (isLoading && entries.length === 0) {
    return (
      <View style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="Temporal KB" />
          <Appbar.Action icon="cog" onPress={handleSettingsPress} />
        </Appbar.Header>
        <LoadingState message="Loading recent entries..." />
      </View>
    );
  }

  if (!isLoading && entries.length === 0) {
    return (
      <View style={styles.container}>
        <Appbar.Header>
          <Appbar.Content title="Temporal KB" />
          <Appbar.Action icon="cog" onPress={handleSettingsPress} />
        </Appbar.Header>
        <EmptyState
          title="No Entries Yet"
          message="Start building your knowledge base by creating your first entry."
          actionLabel="Create Entry"
          onAction={handleCreatePress}
        />
        <FAB
          icon="plus"
          style={styles.fab}
          onPress={handleCreatePress}
        />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Temporal KB" />
        <Appbar.Action icon="cog" onPress={handleSettingsPress} />
      </Appbar.Header>

      <FlatList
        data={entries}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <EntryCard
            entry={item}
            onPress={() => handleEntryPress(item.id)}
          />
        )}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={handleRefresh} />
        }
        contentContainerStyle={styles.list}
      />

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={handleCreatePress}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  list: {
    paddingBottom: spacing.xl,
  },
  fab: {
    position: 'absolute',
    right: spacing.md,
    bottom: spacing.md,
  },
});
