import React, { useState } from 'react';
import { View, FlatList, StyleSheet } from 'react-native';
import { Appbar, SegmentedButtons, Text } from 'react-native-paper';
import { CompositeScreenProps } from '@react-navigation/native';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { BottomTabScreenProps } from '@react-navigation/bottom-tabs';

import { RootStackParamList, MainTabParamList } from '../navigation/types';
import { SearchBarComponent } from '../components/SearchBar';
import { EntryCard } from '../components/EntryCard';
import { LoadingState } from '../components/LoadingState';
import { EmptyState } from '../components/EmptyState';
import { apiClient } from '../api/client';
import { useStore } from '../store';
import { Entry, SemanticSearchResult } from '../types';
import { spacing } from '../theme';

type Props = CompositeScreenProps<
  BottomTabScreenProps<MainTabParamList, 'Search'>,
  NativeStackScreenProps<RootStackParamList>
>;

export const SearchScreen: React.FC<Props> = ({ navigation }) => {
  const { isLoading, setIsLoading } = useStore();
  const [searchMode, setSearchMode] = useState<'keyword' | 'semantic'>('keyword');
  const [results, setResults] = useState<Entry[]>([]);
  const [semanticResults, setSemanticResults] = useState<SemanticSearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (query: string) => {
    try {
      setIsLoading(true);
      setHasSearched(true);

      if (searchMode === 'keyword') {
        const data = await apiClient.search(query);
        setResults(data);
        setSemanticResults([]);
      } else {
        const data = await apiClient.semanticSearch(query, 20);
        setSemanticResults(data);
        setResults([]);
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleEntryPress = (entryId: string) => {
    navigation.navigate('EntryDetail', { entryId });
  };

  const displayResults = searchMode === 'keyword' ? results : semanticResults.map(r => r.entry);

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.Content title="Search" />
      </Appbar.Header>

      <SearchBarComponent onSearch={handleSearch} />

      <SegmentedButtons
        value={searchMode}
        onValueChange={(value) => setSearchMode(value as 'keyword' | 'semantic')}
        buttons={[
          { value: 'keyword', label: 'Keyword' },
          { value: 'semantic', label: 'Semantic' },
        ]}
        style={styles.segmented}
      />

      {isLoading ? (
        <LoadingState message="Searching..." />
      ) : hasSearched && displayResults.length === 0 ? (
        <EmptyState
          title="No Results"
          message="Try adjusting your search query or switch search modes."
        />
      ) : !hasSearched ? (
        <EmptyState
          title="Start Searching"
          message="Enter a query above to search your knowledge base."
        />
      ) : (
        <FlatList
          data={displayResults}
          keyExtractor={(item) => item.id}
          renderItem={({ item, index }) => (
            <View>
              <EntryCard
                entry={item}
                onPress={() => handleEntryPress(item.id)}
              />
              {searchMode === 'semantic' && semanticResults[index] && (
                <Text variant="labelSmall" style={styles.score}>
                  Similarity: {(semanticResults[index].similarity_score * 100).toFixed(1)}%
                </Text>
              )}
            </View>
          )}
          contentContainerStyle={styles.list}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  segmented: {
    marginHorizontal: spacing.md,
    marginBottom: spacing.md,
  },
  list: {
    paddingBottom: spacing.xl,
  },
  score: {
    marginHorizontal: spacing.md,
    marginTop: -spacing.sm,
    marginBottom: spacing.sm,
    color: '#666',
  },
});
