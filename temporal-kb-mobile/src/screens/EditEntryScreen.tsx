import React, { useState } from 'react';
import { View, ScrollView, StyleSheet, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, Button, Chip, Menu, Appbar } from 'react-native-paper';
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { Controller, useForm } from 'react-hook-form';

import { RootStackParamList } from '../navigation/types';
import { useEntries } from '../hooks/useEntries';
import { EntryCreate } from '../types';
import { spacing } from '../theme';

type Props = NativeStackScreenProps<RootStackParamList, 'EditEntry'>;

interface FormData {
  title: string;
  content: string;
  tags: string[];
  projects: string[];
}

const ENTRY_TYPES = ['note', 'legal_case', 'code_snippet', 'concept', 'meeting_note', 'web_clip'];

export const EditEntryScreen: React.FC<Props> = ({ route, navigation }) => {
  const { entry } = route.params;
  const { updateEntry } = useEntries();
  const [saving, setSaving] = useState(false);
  const [tagInput, setTagInput] = useState('');
  const [projectInput, setProjectInput] = useState('');
  const [entryType, setEntryType] = useState(entry.entry_type);
  const [typeMenuVisible, setTypeMenuVisible] = useState(false);

  const { control, handleSubmit, formState: { errors }, watch, setValue } = useForm<FormData>({
    defaultValues: {
      title: entry.title,
      content: entry.content,
      tags: entry.tags,
      projects: entry.projects,
    },
  });

  const tags = watch('tags');
  const projects = watch('projects');

  const handleAddTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setValue('tags', [...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const handleRemoveTag = (tag: string) => {
    setValue('tags', tags.filter((t) => t !== tag));
  };

  const handleAddProject = () => {
    if (projectInput.trim() && !projects.includes(projectInput.trim())) {
      setValue('projects', [...projects, projectInput.trim()]);
      setProjectInput('');
    }
  };

  const handleRemoveProject = (project: string) => {
    setValue('projects', projects.filter((p) => p !== project));
  };

  const onSubmit = async (data: FormData) => {
    try {
      setSaving(true);
      const entryData: Partial<EntryCreate> = {
        title: data.title,
        content: data.content,
        entry_type: entryType,
        tags: data.tags,
        projects: data.projects,
      };
      await updateEntry(entry.id, entryData);
      navigation.goBack();
    } catch (error) {
      console.error('Failed to update entry:', error);
    } finally {
      setSaving(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <Appbar.Header>
        <Appbar.BackAction onPress={() => navigation.goBack()} />
        <Appbar.Content title="Edit Entry" />
        <Appbar.Action
          icon="check"
          onPress={handleSubmit(onSubmit)}
          disabled={saving}
        />
      </Appbar.Header>

      <ScrollView style={styles.content}>
        <Controller
          control={control}
          name="title"
          rules={{ required: 'Title is required' }}
          render={({ field: { onChange, value } }) => (
            <TextInput
              label="Title"
              value={value}
              onChangeText={onChange}
              error={!!errors.title}
              style={styles.input}
              mode="outlined"
            />
          )}
        />

        <Menu
          visible={typeMenuVisible}
          onDismiss={() => setTypeMenuVisible(false)}
          anchor={
            <Button
              mode="outlined"
              style={styles.typeButton}
              onPress={() => setTypeMenuVisible(true)}
            >
              Type: {entryType}
            </Button>
          }
        >
          {ENTRY_TYPES.map((type) => (
            <Menu.Item
              key={type}
              onPress={() => {
                setEntryType(type);
                setTypeMenuVisible(false);
              }}
              title={type}
            />
          ))}
        </Menu>

        <Controller
          control={control}
          name="content"
          rules={{ required: 'Content is required' }}
          render={({ field: { onChange, value } }) => (
            <TextInput
              label="Content"
              value={value}
              onChangeText={onChange}
              error={!!errors.content}
              multiline
              numberOfLines={15}
              style={[styles.input, styles.contentInput]}
              mode="outlined"
            />
          )}
        />

        <View style={styles.section}>
          <TextInput
            label="Add Tag"
            value={tagInput}
            onChangeText={setTagInput}
            onSubmitEditing={handleAddTag}
            right={<TextInput.Icon icon="plus" onPress={handleAddTag} />}
            style={styles.input}
            mode="outlined"
          />
          <View style={styles.chips}>
            {tags.map((tag) => (
              <Chip
                key={tag}
                onClose={() => handleRemoveTag(tag)}
                style={styles.chip}
              >
                {tag}
              </Chip>
            ))}
          </View>
        </View>

        <View style={styles.section}>
          <TextInput
            label="Add Project"
            value={projectInput}
            onChangeText={setProjectInput}
            onSubmitEditing={handleAddProject}
            right={<TextInput.Icon icon="plus" onPress={handleAddProject} />}
            style={styles.input}
            mode="outlined"
          />
          <View style={styles.chips}>
            {projects.map((project) => (
              <Chip
                key={project}
                onClose={() => handleRemoveProject(project)}
                style={styles.chip}
                icon="folder"
              >
                {project}
              </Chip>
            ))}
          </View>
        </View>

        <Button
          mode="contained"
          onPress={handleSubmit(onSubmit)}
          loading={saving}
          disabled={saving}
          style={styles.submitButton}
        >
          Update Entry
        </Button>
      </ScrollView>
    </KeyboardAvoidingView>
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
  input: {
    marginBottom: spacing.md,
  },
  contentInput: {
    minHeight: 200,
  },
  typeButton: {
    marginBottom: spacing.md,
  },
  section: {
    marginBottom: spacing.lg,
  },
  chips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.xs,
  },
  chip: {
    marginBottom: spacing.xs,
  },
  submitButton: {
    marginTop: spacing.md,
    marginBottom: spacing.xl,
  },
});
