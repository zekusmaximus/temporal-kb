import { Entry } from '../types';

export type RootStackParamList = {
  Main: undefined;
  EntryDetail: { entryId: string };
  CreateEntry: undefined;
  EditEntry: { entry: Entry };
  Settings: undefined;
};

export type MainTabParamList = {
  Home: undefined;
  Search: undefined;
  Discover: undefined;
  Profile: undefined;
};
