import React, { useState, useEffect } from "react";
import Post from "./post";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState(null);
  const [loading, setLoading] = useState(false); // optionally show loading state

  // Fetch the first page of posts on mount
  useEffect(() => {
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
    setLoading(true);
    fetch(url, { credentials: "same-origin" })
      .then((res) => res.json())
      .then((data) => {
        console.log("API response", data); // <--- Add this line
        setPosts((prevPosts) => [...prevPosts, ...data.results]);
        setNext(data.next);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }

  return (
    <div>
      {posts.length === 0 && !loading && <p>No posts yet.</p>}
      {posts.map((p) => (
        <Post key={p.postid} url={p.url} />
      ))}
      {loading && <p>Loading...</p>}
      {next && !loading && (
        <button type="button" onClick={() => loadMore(next)}>
          Load More
        </button>
      )}
    </div>
  );
}