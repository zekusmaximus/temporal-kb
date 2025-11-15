import React from 'react';
import { View, StyleSheet } from 'react-native';
import { Card, Text, Chip } from 'react-native-paper';
import { format } from 'date-fns';
import { Entry } from '../types';
import { spacing } from '../theme';

interface EntryCardProps {
  entry: Entry;
  onPress: () => void;
}

export const EntryCard: React.FC<EntryCardProps> = ({ entry, onPress }) => {
  const preview = entry.content.substring(0, 150).replace(/\n/g, ' ');

  return (
    <Card style={styles.card} onPress={onPress}>
      <Card.Content>
        <Text variant="titleMedium" numberOfLines={2} style={styles.title}>
          {entry.title}
        </Text>

        <Text variant="bodySmall" numberOfLines={3} style={styles.preview}>
          {preview}...
        </Text>

        <View style={styles.metadata}>
          <Text variant="labelSmall" style={styles.date}>
            {format(new Date(entry.updated_at), 'MMM d, yyyy')}
          </Text>

          <Text variant="labelSmall" style={styles.wordCount}>
            {entry.word_count} words
          </Text>
        </View>

        {entry.tags.length > 0 && (
          <View style={styles.tags}>
            {entry.tags.slice(0, 3).map((tag) => (
              <Chip key={tag} compact style={styles.chip}>
                {tag}
              </Chip>
            ))}
            {entry.tags.length > 3 && (
              <Chip compact style={styles.chip}>
                +{entry.tags.length - 3}
              </Chip>
            )}
          </View>
        )}
      </Card.Content>
    </Card>
  );
};

const styles = StyleSheet.create({
  card: {
    marginHorizontal: spacing.md,
    marginVertical: spacing.sm,
  },
  title: {
    marginBottom: spacing.sm,
  },
  preview: {
    marginBottom: spacing.sm,
    color: '#666',
  },
  metadata: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  date: {
    color: '#999',
  },
  wordCount: {
    color: '#999',
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  chip: {
    height: 24,
  },
});
