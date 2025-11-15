import React, { useState } from 'react';
import { StyleSheet } from 'react-native';
import { Searchbar } from 'react-native-paper';
import { spacing } from '../theme';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
}

export const SearchBarComponent: React.FC<SearchBarProps> = ({
  onSearch,
  placeholder = 'Search your knowledge base...',
}) => {
  const [query, setQuery] = useState('');

  const handleSearch = () => {
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  return (
    <Searchbar
      placeholder={placeholder}
      onChangeText={setQuery}
      value={query}
      onSubmitEditing={handleSearch}
      style={styles.searchbar}
    />
  );
};

const styles = StyleSheet.create({
  searchbar: {
    margin: spacing.md,
  },
});
