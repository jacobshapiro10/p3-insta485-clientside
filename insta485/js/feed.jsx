import React, { useState, useEffect } from "react";
import Post from "./Post";

export default function Feed() {
  const [posts, setPosts] = useState([]);
  const [next, setNext] = useState(null);

  useEffect(() => {
    fetch(("/api/v1/posts/"), { credentials: "same-origin" })
      .then(res => res.json())
      .then((data) => 
        {
          setPosts(data.results);
          setNext(data.next);   

        })

  }, []);

  return (
    <div>
      {posts.map(p => (
        <Post key={p.postid} url={p.url} />
        
      ))}
      
       {next && (
        <button onClick={() => loadMore(next)}>
          Load More
        </button>
      )}

    </div>
    
  );
}
