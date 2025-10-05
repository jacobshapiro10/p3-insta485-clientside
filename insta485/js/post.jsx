import React, { useState, useEffect } from "react";
import Timestamp from "./timestamp";

// The parameter of this function is an object with a string called url inside it.
// url is a prop for the Post component.
export default function Post({ url }) {
  /* Display image and post owner of a single post */

  const [imgUrl, setImgUrl] = useState("");       // string
  const [owner, setOwner] = useState("");         // string
  const [comments, setComments] = useState([]);   // array (starts empty)
  const [created, setCreated] = useState("");     // string
  const [ownerImgUrl, setOwnerImgUrl] = useState("");
  const [ownerShowUrl, setOwnerShowUrl] = useState("");
  const [likes, setLikes] = useState({ numLikes: 0, lognameLikesThis: false, url: null });
  const [postId, setPostId] = useState(0);


  useEffect(() => {
    fetch(url, { credentials: "same-origin" })
      .then(res => res.json())
      .then(data => {
        setPostId(data.postid)
        setOwner(data.owner);
        setOwnerImgUrl(data.ownerImgUrl);
        setOwnerShowUrl(data.ownerShowUrl);
        setImgUrl(data.imgUrl);
        setCreated(data.created);
        setLikes(data.likes);
        setComments(data.comments);
      });
  }, [url]);

  function handleLikeClick() {
  if (likes.lognameLikesThis) {
    // Unlike: DELETE the existing like
    fetch(likes.url, {
      method: "DELETE",
      credentials: "same-origin"
    })
    .then(() => {
      setLikes({
        ...likes,
        numLikes: likes.numLikes - 1,
        lognameLikesThis: false,
        url: null
      });
    });
  } else {
    // Like: POST a new like
    fetch(`/api/v1/likes/?postid=${postId}`, {
      method: "POST",
      credentials: "same-origin",
    })
    .then(res => res.json())
    .then(data => {
      setLikes({
        ...likes,
        numLikes: likes.numLikes + 1,
        lognameLikesThis: true,
        url: data.url
      });
    });
  }
}


 return (
    <div className="post">
      {/* Owner info */}
      <a href={ownerShowUrl}>
        <img src={ownerImgUrl} alt="profile pic" width="40" />
        <span>{owner}</span>
      </a>

      {/* Post image */}
      <img src={imgUrl} alt="post" width="500" />
      

      {/* Created timestamp */}
      <Timestamp created={created} />

      {/* Likes */}
      <button data-testid="like-unlike-button" onClick={(handleLikeClick)}>
        {likes.lognameLikesThis ? "Unlike" : "Like"}
      </button>
      <p>{likes.numLikes} likes</p>

      {/* Comments */}
      <div>
        {comments.map(c => (
          <div key={c.commentid}>
            <a href={c.ownerShowUrl}>{c.owner}</a>:{" "}
            <span data-testid="comment-text">{c.text}</span>
            {c.lognameOwnsThis && (
              <button data-testid="delete-comment-button">Delete</button>
            )}
          </div>
        ))}
      </div>

      {/* New comment form */}
      <form data-testid="comment-form">
        <input type="text" placeholder="Add a comment..." />
      </form>
    </div>
  );
}