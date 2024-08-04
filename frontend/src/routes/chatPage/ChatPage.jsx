import "./chatPage.css";
import NewPrompt from "../../components/newPrompt/NewPrompt";
import Message from "../../components/message/message";
import { useLocation } from "react-router-dom";
import { useState, useEffect } from "react";

const ChatPage = () => {
  const path = useLocation().pathname;
  const chatSessionId = path.split("/").pop();

  const [chat, setChat] = useState([]);
  const [dbInfo, setDbInfo] = useState({ dbHost: "", dbPort: "", dbName: "" });

  useEffect(() => {
    const chatHistory = JSON.parse(localStorage.getItem(chatSessionId)) || [];
    setChat(chatHistory);
    const info =
      JSON.parse(localStorage.getItem(`chat_session_info_${chatSessionId}`)) ||
      {};
    setDbInfo({
      dbHost: info.dbHost,
      dbPort: info.dbPort,
      dbName: info.dbName,
    });
  }, [chatSessionId]);

  return (
    <div className="chatPage">
      <div className="dbInfoBar">
        <span className="chatSessionId">Chat session: {chatSessionId}</span>
        <span className="dbConnection">
          {dbInfo.dbHost}:{dbInfo.dbPort}/{dbInfo.dbName}
        </span>
      </div>
      <div className="wrapper">
        <div className="chat">
          {chat.map((message, i) => (
            <div
              className={message.role === "user" ? "message user" : "message"}
              key={i}
            >
              <Message message={message} />
            </div>
          ))}
          <NewPrompt chatSessionId={chatSessionId} />
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
