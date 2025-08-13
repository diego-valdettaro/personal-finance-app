// api.ts
const BASE_URL = "http://localhost:8000";

export async function api<T = unknown>(path: string, options: RequestInit = {}): Promise<T> {
  // Mezcla headers sin romper FormData ni sobrescribir a ciegas
  const headers = new Headers(options.headers || {});
  const hasBody = options.body !== undefined;

  // Solo pone Content-Type si hay body y no es FormData y no está seteado
  if (hasBody && !(options.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });
  const contentType = res.headers.get('content-type') || '';

  // Función auxiliar para leer el cuerpo de error de forma segura
  const readErrorBody = async () => {
    try {
      if (contentType.includes('application/json')) return await res.json();
      const txt = await res.text();
      return txt || null;
    } catch {
      return null;
    }
  };

  if (!res.ok) {
    const body = await readErrorBody();
    const msg = typeof body === 'string' ? body : JSON.stringify(body ?? { error: res.statusText });
    const err = new Error(msg);
    (err as any).status = res.status;
    throw err;
  }

  // 204 No Content → no intentes parsear JSON
  if (res.status === 204) {
    return undefined as T;
  }

  // Si no es JSON, devuelve texto (o ajusta a tus necesidades)
  if (!contentType.includes('application/json')) {
    const text = await res.text();
    return text as T;
  }

  return (await res.json()) as T;
}
