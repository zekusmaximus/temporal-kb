import React, { useEffect, useState } from 'react';
import { View, ScrollView, StyleSheet } from 'react-native';
import { Text, Chip, Divider, Button, Menu, Appbar } from 'react-native-paper';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import Markdown from 'react-native-markdown-display';
import { format } from 'date-fns';

import { RootStackParamList } from '../navigation/types';
import { LoadingState } from '../components/LoadingState';
import { apiClient } from '../api/client';
import { Entry, RelatedEntry } from '../types';
import { spacing, colors } from '../theme';

type Props = NativeStackScreenProps<RootStackParamList, 'EntryDetail'>;

export const EntryDetailScreen: React.FC<Props> = ({ route, navigation }) => {
  const { entryId } = route.params;
  const [entry, setEntry] = useState<Entry | null>(null);
  const [relatedEntries, setRelatedEntries] = useState<RelatedEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [menuVisible, setMenuVisible] = useState(false);

  useEffect(() => {
    loadEntry();
    loadRelated();
  }, [entryId]);

  const loadEntry = async () => {
    try {
      setLoading(true);
      const data = await apiClient.getEntry(entryId);
      setEntry(data);
    } catch (error) {
      console.error('Failed to load entry:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadRelated = async () => {
    try {
      const data = await apiClient.getRelatedEntries(entryId, 5);
      setRelatedEntries(data);
    } catch (error) {
      console.error('Failed to load related entries:', error);
    }
  };

  const handleEdit = () => {
    if (entry) {
      setMenuVisible(false);
      navigation.navigate('EditEntry', { entry });
    }
  };

  const handleDelete = async () => {
    if (entry) {
      try {
        await apiClient.deleteEntry(entry.id);
        navigation.goBack();
      } catch (error) {
        console.error('Failed to delete entry:', error);
      }
    }
  };

  const handleRelatedPress = (id: string) => {
    navigation.push('EntryDetail', { entryId: id });
  };

  if (loading || !entry) {
    return <LoadingState message="Loading entry..." />;
  }

  return (
    <View style={styles.container}>
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Entry" />
        <Menu
          visible={menuVisible}
          onDismiss={() => setMenuVisible(false)}
          anchor={<Appbar.Action icon="dots-vertical" onPress={() => setMenuVisible(true)} />}
        >
          <Menu.Item onPress={handleEdit} title="Edit" leadingIcon="pencil" />
          <Menu.Item onPress={handleDelete} title="Delete" leadingIcon="delete" />
        </Menu>
      </Appbar.Header>

      <ScrollView style={styles.content}>
        <Text variant="headlineMedium" style={styles.title}>
          {entry.title}
        </Text>

        <View style={styles.metadata}>
          <Text variant="bodySmall" style={styles.metaText}>
            {format(new Date(entry.created_at), 'MMMM d, yyyy')}
          </Text>
          <Text variant="bodySmall" style={styles.metaText}>
            {entry.word_count} words
          </Text>
          <Text variant="bodySmall" style={styles.metaText}>
            {entry.entry_type}
          </Text>
        </View>

        {entry.tags.length > 0 && (
          <View style={styles.tags}>
            {entry.tags.map((tag) => (
              <Chip key={tag} style={styles.chip}>
                {tag}
              </Chip>
            ))}
          </View>
        )}

        {entry.projects.length > 0 && (
          <View style={styles.projects}>
            <Text variant="labelMedium" style={styles.sectionLabel}>
              Projects:
            </Text>
            {entry.projects.map((project) => (
              <Chip key={project} style={styles.chip} icon="folder">
                {project}
              </Chip>
            ))}
          </View>
        )}

        <Divider style={styles.divider} />

        <Markdown style={markdownStyles}>{entry.content}</Markdown>

        {relatedEntries.length > 0 && (
          <>
            <Divider style={styles.divider} />
            <Text variant="titleMedium" style={styles.sectionTitle}>
              Related Entries
            </Text>
            {relatedEntries.map((related) => (
              <Button
                key={related.entry.id}
                mode="outlined"
                style={styles.relatedButton}
                onPress={() => handleRelatedPress(related.entry.id)}
              >
                {related.entry.title}
              </Button>
            ))}
          </>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  chip: {
    height: 32,
  },
  container: {
    flex: 1,
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  divider: {
    marginVertical: spacing.lg,
  },
  metaText: {
    color: colors.text.secondary,
  },
  metadata: {
    flexDirection: 'row',
    gap: spacing.md,
    marginBottom: spacing.md,
  },
  projects: {
    alignItems: 'center',
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  relatedButton: {
    marginBottom: spacing.sm,
  },
  sectionLabel: {
    marginRight: spacing.xs,
  },
  sectionTitle: {
    marginBottom: spacing.md,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
    marginBottom: spacing.sm,
  },
  title: {
    marginBottom: spacing.sm,
  },
});

const markdownStyles = {
  body: {
    fontSize: 16,
    lineHeight: 24,
  },
  heading1: {
    fontSize: 24,
    fontWeight: 'bold' as const,
    marginTop: spacing.lg,
    marginBottom: spacing.sm,
  },
  heading2: {
    fontSize: 20,
    fontWeight: 'bold' as const,
    marginTop: spacing.md,
    marginBottom: spacing.sm,
  },
  paragraph: {
    marginBottom: spacing.sm,
  },
  code_inline: {
    backgroundColor: colors.code.background,
    padding: 2,
    borderRadius: 3,
  },
  code_block: {
    backgroundColor: colors.code.background,
    padding: spacing.sm,
    borderRadius: spacing.xs,
    marginVertical: spacing.sm,
  },
};
