import { Link } from "react-router-dom";
import "./chatList.css";
import { useEffect, useState } from "react";

const ChatList = () => {
  const [chats, setChats] = useState(
    JSON.parse(localStorage.getItem("chat_session_ids")) || []
  );

  useEffect(() => {
    const handleStorageChange = (event) => {
      if (event.key === "chat_session_ids") {
        setChats(JSON.parse(event.newValue) || []);
      }
    };

    window.addEventListener("storage", handleStorageChange);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
    };
  }, []);

  return (
    <div className="chatList">
      <Link to="/chat">Create a new chat</Link>
      <Link to="/knowledge-base">Your knowledge base</Link>
      <hr />
      <span className="title">RECENT CHATS</span>
      <div className="list">
        {chats.length > 0 ? (
          chats.map((chatId, index) => (
            <Link key={index} to={`/chat/${chatId}`}>
              Chat - {chatId}
            </Link>
          ))
        ) : (
          <p>No recent chat found</p>
        )}
      </div>
    </div>
  );
};

export default ChatList;
