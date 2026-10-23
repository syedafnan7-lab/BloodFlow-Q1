import { useEffect, useState } from 'react';

export function useRound2Study() {
  const [study, setStudy] = useState(null);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    fetch('/round2-benchmark-20261007-01.json')
      .then((response) => {
        if (!response.ok) throw new Error(`Round 2 artifact request failed (${response.status})`);
        return response.json();
      })
      .then((value) => { if (active) setStudy(value); })
      .catch((issue) => { if (active) setError(issue.message || 'Could not load the Round 2 artifact.'); });
    return () => { active = false; };
  }, []);
  return { study, error };
}
