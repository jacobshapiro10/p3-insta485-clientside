// import React, { useState, useEffect } from "react";
// import Post from "./post";

// export default function Feed() {
//   const [posts, setPosts] = useState([]);
//   const [next, setNext] = useState(null);
//   const [loading, setLoading] = useState(false); // optionally show loading state

//   // Fetch the first page of posts on mount
//   useEffect(() => {
//     setLoading(true);
//     fetch("/api/v1/posts/", { credentials: "same-origin" })
//       .then((res) => res.json())
//       .then((data) => {
//         setPosts(data.results);
//         setNext(data.next);
//         setLoading(false);
//       })
//       .catch(() => setLoading(false));
//   }, []);

//   // Load more posts (pagination)
//   function loadMore(url) {
//     setLoading(true);
//     fetch(url, { credentials: "same-origin" })
//       .then((res) => res.json())
//       .then((data) => {
//         console.log("API response", data); // <--- Add this line
//         setPosts((prevPosts) => [...prevPosts, ...data.results]);
//         setNext(data.next);
//         setLoading(false);
//       })
//       .catch(() => setLoading(false));
//   }

//   return (
//     <div>
//       {posts.length === 0 && !loading && <p>No posts yet.</p>}
//       {posts.map((p) => (
//         <Post key={p.postid} url={p.url} />
//       ))}
//       {loading && <p>Loading...</p>}
//       {next && !loading && (
//         <button type="button" onClick={() => loadMore(next)}>
//           Load More
//         </button>
//       )}
//     </div>
//   );
// }

import React, { useState, useEffect } from "react";
import Post from "./post";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState(null);
  const [loading, setLoading] = useState(false); // optionally show loading state

  // 1️⃣ Scroll to top when component mounts
  useEffect(() => {
    if ("scrollRestoration" in history) {
      history.scrollRestoration = "manual";
    }
    window.scrollTo(0, 0);
  }, []); // empty array → only runs once on mount

  // Fetch the first page of posts on mount
  useEffect(() => {
    // window.scrollTo(0, 0); // always start at top on page load
    setLoading(true);
    fetch("/api/v1/posts/", { credentials: "same-origin" })
      .then((res) => res.json())
      .then((data) => {
        setPosts(data.results);
        setNext(data.next);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  // Load more posts (pagination)
  function loadMore(url) {
    if (!url) return;
    setLoading(true);
    fetch(url, { credentials: "same-origin" })
      .then((res) => res.json())
      .then((data) => {
        console.log("API response", data);
        setPosts((prevPosts) => [...prevPosts, ...data.results]);
        setNext(data.next);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }

  // Infinite scroll effect
  useEffect(() => {
    const handleScroll = () => {
      if (
        window.innerHeight + window.scrollY >=
          document.body.offsetHeight - 500 &&
        !loading &&
        next
      ) {
        loadMore(next);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, [loading, next]); // re-run if loading or next changes

  return (
    <div>
      {posts.length === 0 && !loading && <p>No posts yet.</p>}
      {posts.map((p) => (
        <Post key={p.postid} url={p.url} />
      ))}
      {loading && <p>Loading...</p>}
    </div>
  );
}
