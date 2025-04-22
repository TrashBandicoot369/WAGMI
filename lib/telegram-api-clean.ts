"use client"

// This file provides a client-side interface to the server-side Telegram API

export interface TelegramUserInfo {
  id: number;
  username?: string;
  first_name?: string;
  last_name?: string;
  found: boolean;
}

export async function searchTelegramUser(username: string): Promise<TelegramUserInfo> {
  try {
    const response = await fetch('/api/telegram/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'Failed to search user');
    }

    return await response.json();
  } catch (error) {
    console.error('Error searching Telegram user:', error);
    return { id: 0, found: false };
  }
} 