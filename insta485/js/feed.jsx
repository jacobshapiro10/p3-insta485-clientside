import React, { useState, useEffect, useCallback } from "react";
import Post from "./post";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState(null);
  const [loading, setLoading] = useState(false);

  // Scroll to top when component mounts
  useEffect(() => {
    if ("scrollRestoration" in history) {
      history.scrollRestoration = "manual";
    }
    window.scrollTo(0, 0);
  }, []);

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

  // Use useCallback to memoize loadMore
  const loadMore = useCallback((url) => {
    if (!url || loading) return;
    setLoading(true);
    fetch(url, { credentials: "same-origin" })
      .then((res) => res.json())
      .then((data) => {
        setPosts((prevPosts) => [...prevPosts, ...data.results]);
        setNext(data.next);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [loading]);

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
  }, [loading, next, loadMore]); // Add loadMore to dependencies

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