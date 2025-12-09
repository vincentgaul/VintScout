import { useEffect, useState } from 'react';
import type { Condition } from '../types';
import * as api from '../services/api';

let cachedConditions: Condition[] | null = null;
let pendingPromise: Promise<Condition[]> | null = null;

export function useConditions() {
  const [conditions, setConditions] = useState<Condition[]>(cachedConditions ?? []);

  useEffect(() => {
    if (cachedConditions) {
      return;
    }

    if (!pendingPromise) {
      pendingPromise = api.getConditions().then(data => {
        const sorted = [...data].sort((a, b) => a.sort_order - b.sort_order);
        cachedConditions = sorted;
        return sorted;
      });
    }

    pendingPromise.then(data => setConditions(data));
  }, []);

  return conditions;
}
