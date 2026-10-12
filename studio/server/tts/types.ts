export type Lang = 'uz' | 'ru' | 'en';
export type Gender = 'female' | 'male';

export interface WordTiming {
  text: string;
  start: number; // seconds from the start of the clip
  end: number;
}

export interface Voice {
  key: string; // unique: provider:voiceId
  provider: string;
  voiceId: string;
  lang: Lang;
  gender: Gender;
  label: string;
  /** Script this voice reads correctly for Uzbek ('latin' input is converted for espeak, for example). */
  uzInput?: 'latin' | 'cyrillic' | 'any';
}

export interface SynthResult {
  wavPath: string;
  duration: number;
  words: WordTiming[];
  timing: 'exact' | 'estimated';
}

export interface Provider {
  id: string;
  label: string;
  kind: 'offline-open-source' | 'free-online' | 'paid-api';
  /** Environment variables the provider needs. */
  env: string[];
  /** Hosts the provider has to reach (shown to the user when the network blocks them). */
  hosts: string[];
  available(): Promise<{ ok: boolean; reason?: string }>;
  voices(): Promise<Voice[]>;
  synth(text: string, voice: Voice, outBase: string): Promise<SynthResult>;
}
