import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

export default function Timestamp({ created }) {
  const [displayTime, setDisplayTime] = useState("");

  useEffect(() => {
    // Set immediately
    setDisplayTime(dayjs.utc(created).local().fromNow());

    // Small timeout ensures interval registers *after* Cypress clock starts
    const startTimer = setTimeout(() => {
      const interval = setInterval(() => {
        setDisplayTime(dayjs.utc(created).local().fromNow());
      }, 1000);
      // Clean up
      return () => clearInterval(interval);
    }, 0);

    return () => clearTimeout(startTimer);
  }, [created]);

  return <p data-testid="post-time-ago">{displayTime}</p>;
}
