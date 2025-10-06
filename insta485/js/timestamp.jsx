import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

export default function Timestamp({ created }) {
  const [displayTime, setDisplayTime] = useState("");

  useEffect(() => {
    // add a guard clause to avoid setting up interval
    // if created is null or undefined
    if (!created) return;

    // Set immediately
    setDisplayTime(dayjs.utc(created).local().fromNow());

    let interval = null;

    // Small timeout ensures interval registers *after* Cypress clock starts
    const startTimer = setTimeout(() => {
      interval = setInterval(() => {
        setDisplayTime(dayjs.utc(created).local().fromNow());
      }, 60000);
    }, 0);

    // Clean up both timeout and interval
    return () => {
      clearTimeout(startTimer);
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [created]);

  return <p data-testid="post-time-ago">{displayTime}</p>;
}
