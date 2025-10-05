import React, { useState, useEffect } from "react";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";

dayjs.extend(relativeTime);
dayjs.extend(utc);

export default function Timestamp({ created }) {
  const [displayTime, setDisplayTime] = useState(
    dayjs.utc(created).local().fromNow(),
  );
  useEffect(() => {
    const interval = setInterval(() => {
      setDisplayTime(dayjs.utc(created).local().fromNow());
    }, 60000);
    return () => clearInterval(interval);
  }, [created]);

  return <p>{displayTime}</p>;
}
