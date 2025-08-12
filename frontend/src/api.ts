const BASE_URL = "http://localhost:8000";

export async function api<T>(path: string, options: RequestInit = {}):
    Promise<T> {
        const res = await fetch(
            `${BASE_URL}${path}`,
            {headers: 
                {'Content-Type': 'application/json'},
                ...options,
            }
        );
        if (!res.ok) {
            const text = await res.text();
            throw new Error(text || `HTTP ${res.status}`);
        }
        return res.json();
    }
