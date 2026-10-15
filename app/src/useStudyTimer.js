// 学习计时 Hook：页面停留期间每 30 秒累计到今日学习分钟
import { useEffect, useRef } from 'react';
import { Store } from './store';

export function useStudyTimer(active = true) {
  const startRef = useRef(Date.now());
  const accRef = useRef(0);
  const timerRef = useRef(null);

  useEffect(() => {
    if (!active) return;
    startRef.current = Date.now();
    timerRef.current = setInterval(() => {
      const sec = (Date.now() - startRef.current) / 1000;
      accRef.current += sec;
      startRef.current = Date.now();
      if (accRef.current >= 30) {
        const mins = Math.floor(accRef.current / 60);
        accRef.current = accRef.current % 60;
        Store.addMinutes(mins);
      }
    }, 20000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      // 离开时把剩余秒数折入分钟
      const sec = (Date.now() - startRef.current) / 1000 + accRef.current;
      if (sec >= 60) Store.addMinutes(Math.floor(sec / 60));
    };
  }, [active]);
}
