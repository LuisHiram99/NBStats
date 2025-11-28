import type { Teams } from '../types/entities.js';
import { API_URL } from '../app/constants.js';

export async function getTeams(): Promise<Teams> {
	try {
		const response = await fetch(`${API_URL}teams/all`);
		if (!response.ok) {
			throw new Error(`HTTP error! status: ${response.status}`);
		}
		const data = await response.json();
		return data;
	} catch (error) {
		console.error('Error fetching teams:', error);
		// Return empty array as fallback
		return [];
	}
}
